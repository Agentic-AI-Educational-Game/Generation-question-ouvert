import os
from huggingface_hub import hf_hub_download
from flask import Flask, render_template, jsonify
from llama_cpp import Llama

app = Flask(__name__)


global LLM_INSTANCE

MODEL_LOADED = False
LLM_INSTANCE = None
GGUF_PATH = None

def load_model():
    global MODEL_LOADED, LLM_INSTANCE, GGUF_PATH
    if MODEL_LOADED:
        return

    print("Checking if model is already downloaded...")
    try:
        target_dir = os.path.expanduser("./models")
        os.makedirs(target_dir, exist_ok=True)
        model_filename = "qwen2_5_1.5B_instruct_finetuned_fr.q8_0.gguf"
        model_path = os.path.join(target_dir, model_filename)

        if os.path.exists(model_path):
            GGUF_PATH = model_path
            print(f"Model already exists at: {GGUF_PATH}")
        else:
            print("Model not found, downloading...")
            GGUF_PATH = hf_hub_download(
                repo_id="zinec/finetuned-qwen-fr",
                filename=model_filename,
                local_dir=target_dir,
                local_dir_use_symlinks=False
            )
            print(f"Model downloaded to: {GGUF_PATH}")

        LLM_INSTANCE = Llama(
            model_path=GGUF_PATH,
            # n_gpu_layers=-1,  # Optional: Uncomment to use GPU acceleration
            # seed=1337,
            # n_ctx=2048,
            n_threads=2,  # Use all CPU cores

        )
        MODEL_LOADED = True
        print("Model loaded successfully.")

    except Exception as e:
        print(f"Error loading model: {e}")


@app.route('/generate_question')
def generate_question():
    if LLM_INSTANCE is None:
        print("Model not loaded - Loading in progress...")
        load_model()
    
    prompt = """<|im_start|>system
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
La plage et la montagne offrent des paysages contrastés. Sur la plage, il y a du sable doré, des vagues qui déferlent et des parasols colorés. Tandis qu'à la montagne, l'air est frais, les cimes sont enneigées et les sentiers sinueux.
<|im_end|>
<|im_start|>assistant
"""

    output = LLM_INSTANCE(prompt, max_tokens=200, stream=True)

    full_response = ""
    for chunk in output:
        full_response += chunk["choices"][0]["text"]
        print(chunk["choices"][0]["text"], end="", flush=True)

    return full_response

@app.route('/correct_answer')
def correct_answer():
    if LLM_INSTANCE is None:
        print("Model not loaded - Loading in progress...")
        load_model()

    # This should ideally come from the generated question, but for now it's hardcoded
    texte = """La plage et la montagne offrent des paysages contrastés. 
    Sur la plage, il y a du sable doré, des vagues qui déferlent et des parasols colorés. 
    Tandis qu'à la montagne, l'air est frais, les cimes sont enneigées et les sentiers sinueux."""

    reponse_eleve = "Les paysages de la plage sont typiques avec des plages vert."
    if not reponse_eleve.strip():
        reponse_eleve = "L’élève ne répond pas !"

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

    output = LLM_INSTANCE(prompt, max_tokens=300, stream=True)

    full_response = ""
    for chunk in output:
        full_response += chunk["choices"][0]["text"]
        print(chunk["choices"][0]["text"], end="", flush=True)

    return full_response

if __name__ == '__main__':
    app.run(debug=True)
