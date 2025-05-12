import os
from huggingface_hub import hf_hub_download
from flask import Flask, render_template, jsonify, request
from llama_cpp import Llama
import sys
import re # Import regular expressions for more robust parsing if needed

# ... (Keep the rest of your code: Flask app setup, MODEL_STATE, load_model, ensure_model_loaded, generate_question) ...

app = Flask(__name__)

# --- Global Variables ---
MODEL_STATE = {
    "loaded": False,
    "instance": None,
    "gguf_path": None,
}

# --- Model Loading ---
# ... (load_model function remains the same) ...
def load_model():
    """Downloads (if needed) and loads the GGUF model."""
    if MODEL_STATE["loaded"]:
        print("Model already loaded.")
        return

    print("Attempting to load model...")
    try:
        target_dir = os.path.expanduser("./models")
        os.makedirs(target_dir, exist_ok=True)
        model_filename = "qwen2_5_1.5B_instruct_finetuned_fr.q8_0.gguf"
        model_path = os.path.join(target_dir, model_filename)

        if os.path.exists(model_path):
            MODEL_STATE["gguf_path"] = model_path
            print(f"Model found locally at: {MODEL_STATE['gguf_path']}")
        else:
            print("Model not found locally, downloading...")
            MODEL_STATE["gguf_path"] = hf_hub_download(
                repo_id="zinec/finetuned-qwen-fr",
                filename=model_filename,
                local_dir=target_dir,
                local_dir_use_symlinks=False,
            )
            print(f"Model downloaded to: {MODEL_STATE['gguf_path']}")

        print("Initializing Llama...")
        MODEL_STATE["instance"] = Llama(
            model_path=MODEL_STATE["gguf_path"],
            # n_gpu_layers=-1,  # Optional: Uncomment to use GPU acceleration
            # seed=1337,
            # n_ctx=2048,
            n_threads=os.cpu_count() or 2, # Use available cores, default 2
            verbose=False # Reduce llama.cpp logs unless needed
        )
        MODEL_STATE["loaded"] = True
        print("Model loaded successfully.")

    except Exception as e:
        print(f"FATAL: Error loading model: {e}", file=sys.stderr)
        # Optionally exit or handle differently if model load fails critically
        # sys.exit(1)


# --- Flask Routes ---

# Helper function to ensure model is loaded before processing request
def ensure_model_loaded():
    """Checks if model is loaded, loads if not. Returns True if ready, False otherwise."""
    if not MODEL_STATE["loaded"]:
        print("Model not loaded. Triggering load...")
        load_model() # Try to load it now
        if not MODEL_STATE["loaded"]:
             # If still not loaded after attempt
            print("ERROR: Model could not be loaded.", file=sys.stderr)
            return False
    return True

# --- generate_question function (Keep the version from the previous step) ---
@app.route('/generate_question', methods=['POST'])
def generate_question():
    """
    Generates a question based on text provided in a POST request.
    Expects JSON: {"text": "Your text here..."}
    Returns JSON: {"question": "Extracted question", "raw": "Full LLM output"} or {"error": "..."}
    """
    if not ensure_model_loaded():
        return jsonify({"error": "Model not available"}), 503

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
        print("Generating question...")
        output_stream = MODEL_STATE["instance"](prompt, max_tokens=200, stream=True)

        full_response = ""
        print("LLM Response Stream: ", end="")
        for chunk in output_stream:
            text_piece = chunk["choices"][0]["text"]
            full_response += text_piece
            print(text_piece, end="", flush=True)
        print("\n--- End of LLM Stream ---")

        # --- Parsing Logic ---
        raw_output = full_response.strip() # Store the cleaned raw output
        question_prefix = "**Question :**"
        extracted_question = raw_output # Default if prefix not found

        if raw_output.startswith(question_prefix):
            extracted_question = raw_output.removeprefix(question_prefix).strip()
        else:
            print(f"WARNING: LLM output for question did not start with expected prefix '{question_prefix}'. Raw output:\n{raw_output}", file=sys.stderr)

        return jsonify({
            "question": extracted_question,
            "raw": raw_output
        })
        # --- End Parsing Logic ---

    except Exception as e:
        print(f"Error during LLM inference for question generation: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to generate question due to internal error"}), 500

# --- START MODIFIED correct_answer function ---
@app.route('/correct_answer', methods=['POST'])
def correct_answer():
    """
    Corrects a student's answer based on original text and the answer.
    Expects JSON: {"text": "Original text...", "student_answer": "Student answer..."}
    Returns JSON: {"note": "...", "erreur": "...", "correction": "...", "raw": "..."} or {"error": "..."}
    """
    if not ensure_model_loaded():
        return jsonify({"error": "Model not available"}), 503

    data = request.get_json()
    if not data or 'text' not in data or 'student_answer' not in data:
        return jsonify({"error": "Missing 'text' or 'student_answer' field in JSON payload"}), 400

    texte = data['text']
    reponse_eleve = data['student_answer']

    if not texte or not isinstance(texte, str):
         return jsonify({"error": "'text' field must be a non-empty string"}), 400
    if not isinstance(reponse_eleve, str):
         return jsonify({"error": "'student_answer' field must be a string"}), 400

    if not reponse_eleve.strip():
        reponse_eleve = "L’élève ne répond pas !"

    print(f"\n--- Received text for correction:\n{texte[:200]}...")
    print(f"--- Received student answer:\n{reponse_eleve[:200]}...")

    prompt = f"""<|im_start|>system
You are an expert error-correction assistant.
When the user gives you an original text and a student’s answer, you must:
1. Assign a score out of 10 and display it as
   Note : X/10
2. Point out the single most important mistake in one sentence prefixed with
   Erreur :
3. Provide the corrected statement prefixed with
   Correction :

Always follow this exact layout, with no extra lines or sections.
<|im_end|>
<|im_start|>user
Voici le texte original : {texte}.
Réponse de l’étudiant : {reponse_eleve}.
<|im_end|>
<|im_start|>assistant
"""
    try:
        print("Generating correction...")
        output_stream = MODEL_STATE["instance"](prompt, max_tokens=300, stream=True)

        full_response = ""
        print("LLM Response Stream: ", end="")
        for chunk in output_stream:
            text_piece = chunk["choices"][0]["text"]
            full_response += text_piece
            print(text_piece, end="", flush=True)
        print("\n--- End of LLM Stream ---")

        # --- Parsing Logic ---
        raw_output = full_response.strip()
        parsed_data = {
            "note": None,
            "erreur": None,
            "correction": None,
            "raw": raw_output
        }

        # Define prefixes (case-sensitive, adjust if needed)
        note_prefix = "Note :"
        erreur_prefix = "Erreur :"
        correction_prefix = "Correction :"

        # Find the start index of each prefix
        # Using find() which returns -1 if not found
        note_start_idx = raw_output.find(note_prefix)
        erreur_start_idx = raw_output.find(erreur_prefix)
        correction_start_idx = raw_output.find(correction_prefix)

        # Extract Note
        if note_start_idx != -1:
            # Find the end of the note section (start of erreur or end of string if erreur not found)
            note_end_idx = erreur_start_idx if erreur_start_idx != -1 else len(raw_output)
            parsed_data["note"] = raw_output[note_start_idx + len(note_prefix):note_end_idx].strip()

        # Extract Erreur
        if erreur_start_idx != -1:
            # Find the end of the erreur section (start of correction or end of string if correction not found)
            erreur_end_idx = correction_start_idx if correction_start_idx != -1 else len(raw_output)
            parsed_data["erreur"] = raw_output[erreur_start_idx + len(erreur_prefix):erreur_end_idx].strip()

        # Extract Correction
        if correction_start_idx != -1:
            # Correction goes from its start index to the end of the string
            parsed_data["correction"] = raw_output[correction_start_idx + len(correction_prefix):].strip()

        # Optional: Add a warning if parsing seems incomplete
        if parsed_data["note"] is None and parsed_data["erreur"] is None and parsed_data["correction"] is None and raw_output:
             print(f"WARNING: Could not parse correction feedback structure. Prefixes might be missing or format unexpected. Raw output:\n{raw_output}", file=sys.stderr)
             # Decide fallback: maybe put raw_output in one field, or leave as None?
             # For now, we just leave fields as None if not found.

        return jsonify(parsed_data)
        # --- End Parsing Logic ---

    except Exception as e:
        print(f"Error during LLM inference for correction: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to generate correction due to internal error"}), 500
# --- END MODIFIED correct_answer function ---


# --- Application Startup ---
if __name__ == '__main__':
    print("Starting Flask app...")
    load_model() # Attempt to load model on startup
    if not MODEL_STATE["loaded"]:
         print("WARNING: Model failed to load on startup. API endpoints requesting the model will fail.", file=sys.stderr)
    app.run(host='0.0.0.0', port=5000, debug=True)