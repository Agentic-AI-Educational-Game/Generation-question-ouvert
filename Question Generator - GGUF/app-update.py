import os
from huggingface_hub import hf_hub_download
from flask import Flask, jsonify, request
from llama_cpp import Llama
import sys
import re # re is already imported
import json # <--- Added import for json module

app = Flask(__name__)

# --- Global Variables for Multiple Models ---
# Define configuration and state for each model
MODEL_CONFIGS = {
    "question_generator": {
        "repo_id": "zinec/finetuned-qwen-fr",
        "filename": "finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf",
        "loaded": False,
        "instance": None,
        "gguf_path": None,
        "description": "Model for generating questions",
    },
}

# --- Model Loading ---
def load_specific_model(model_name):
    """
    Downloads (if needed) and loads a specific GGUF model based on its name.
    """
    model_info = MODEL_CONFIGS.get(model_name)
    if not model_info:
        print(f"ERROR: Model configuration for '{model_name}' not found.", file=sys.stderr)
        return False

    if model_info["loaded"]:
        print(f"Model '{model_name}' already loaded.")
        return True

    print(f"Attempting to load model '{model_name}' ({model_info['description']})...")
    try:
        target_dir = os.path.expanduser("./models")
        os.makedirs(target_dir, exist_ok=True)

        model_filename = model_info["filename"]
        model_path = os.path.join(target_dir, model_filename)

        if os.path.exists(model_path):
            model_info["gguf_path"] = model_path
            print(f"Model '{model_name}' found locally at: {model_info['gguf_path']}")
        else:
            print(f"Model '{model_name}' not found locally, downloading from {model_info['repo_id']}...")
            model_info["gguf_path"] = hf_hub_download(
                repo_id=model_info["repo_id"],
                filename=model_filename,
                local_dir=target_dir,
                local_dir_use_symlinks=False,
            )
            print(f"Model '{model_name}' downloaded to: {model_info['gguf_path']}")

        print(f"Initializing Llama for '{model_name}'...")
        model_info["instance"] = Llama(
            model_path=model_info["gguf_path"],
            # n_gpu_layers=-1,
            # seed=1337,
            n_ctx=10048,
            n_threads=os.cpu_count() or 2,
            verbose=False
        )
        model_info["loaded"] = True
        print(f"Model '{model_name}' loaded successfully.")
        return True

    except Exception as e:
        print(f"FATAL: Error loading model '{model_name}': {e}", file=sys.stderr)
        model_info["loaded"] = False
        model_info["instance"] = None
        model_info["gguf_path"] = None
        return False

def ensure_specific_model_loaded(model_name):
    model_info = MODEL_CONFIGS.get(model_name)
    if not model_info:
        print(f"ERROR: Attempted to check non-existent model '{model_name}'.", file=sys.stderr)
        return False
    if not model_info["loaded"]:
        print(f"Model '{model_name}' not loaded. Triggering load...")
        if not load_specific_model(model_name):
            print(f"ERROR: Model '{model_name}' could not be loaded.", file=sys.stderr)
            return False
    return True

# --- Flask Routes ---

@app.route('/generate_question', methods=['POST'])
def generate_question():
    if not ensure_specific_model_loaded("question_generator"):
        return jsonify({"error": "Question generation model not available"}), 503

    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' field in JSON payload"}), 400

    input_text = data['text']
    if not input_text or not isinstance(input_text, str):
         return jsonify({"error": "'text' field must be a non-empty string"}), 400

    print(f"\n--- Received text for question generation:\n{input_text[:200]}...")

    prompt = f"""<|im_start|>system
You are an expert question-generation assistant.
When the user gives you a block of text, you must:
1. Generate exactly one relevant question in French based solely on the provided text.
2. Never add any comments, explanations, or additional questions.
3. Use the exact output format:

**Question :** [votre question]

Always follow this layout strictly, with no extra lines or sections.
<|im_end|>
<|im_start|>user
**Instruction :**
À partir *uniquement* du texte fourni, génère une seule question pertinente en français.
Ne dépasse pas une seule question. N’ajoute aucun commentaire ni explication.

Le format de sortie doit être strictement le suivant :
**Question :** [question générée]

**Texte :**
{input_text}
<|im_end|>
<|im_start|>assistant
"""
    try:
        print("Generating question using 'question_generator' model...")
        output_stream = MODEL_CONFIGS["question_generator"]["instance"](prompt, max_tokens=512, stream=True)

        full_response = ""
        print("LLM Response Stream: ", end="")
        for chunk in output_stream:
            text_piece = chunk["choices"][0]["text"]
            full_response += text_piece
            print(text_piece, end="", flush=True)
        print("\n--- End of LLM Stream ---")

        raw_output = full_response.strip()
        extracted_question = raw_output

        match = re.match(r"\*\*Question\s*:\*\*\s*(.*)", raw_output, re.DOTALL)
        if match:
            extracted_question = match.group(1).strip()
        else:
            print(f"WARNING: LLM output for question did not start with expected prefix '**Question :**'. Raw output:\n{raw_output}", file=sys.stderr)

        return jsonify({
            "question": extracted_question,
            "raw": raw_output
        })

    except Exception as e:
        print(f"Error during LLM inference for question generation: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to generate question due to internal error"}), 500



# --- Application Startup ---
if __name__ == '__main__':
    print("Starting Flask app...")
    print("Attempting to load all models on startup...")

    if not load_specific_model("question_generator"):
        print("WARNING: Question generator model failed to load on startup. '/generate_question' might fail.", file=sys.stderr)
    

    all_models_listed = MODEL_CONFIGS.keys()
    all_loaded_successfully = all(MODEL_CONFIGS[name]["loaded"] for name in all_models_listed)

    if all_loaded_successfully:
        print("All configured models loaded successfully on startup.")
    else:
        print("STATUS: Some models failed to load on startup. Check warnings above.", file=sys.stderr)
        for name, config in MODEL_CONFIGS.items():
            if not config["loaded"]:
                print(f"  - Model '{name}' did not load.", file=sys.stderr)

    app.run(host='0.0.0.0', port=5000, debug=True)
