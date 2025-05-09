import os
from huggingface_hub import hf_hub_download

from flask import Flask, render_template
from llama_cpp import Llama

app = Flask(__name__)



MODEL_LOADED = False
LLM_INSTANCE = None
GGUF_PATH = None

def load_model():
    global MODEL_LOADED, LLM_INSTANCE, GGUF_PATH
    if MODEL_LOADED:
        return

    print("Checking if model is already downloaded...")
    try:
        # Define target path and model file name
        target_dir = os.path.expanduser("./models")
        os.makedirs(target_dir, exist_ok=True)
        model_filename = "qwen2_5_1.5B_instruct_finetuned_fr.q8_0.gguf"
        model_path = os.path.join(target_dir, model_filename)

        # Check if model already exists
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

        # Load the model
        LLM_INSTANCE = Llama(
            model_path=model_path,
            # n_gpu_layers=-1, # Uncomment to use GPU acceleration
            # seed=1337, # Uncomment to set a specific seed
            # n_ctx=2048, # Uncomment to increase the context window
        )

        MODEL_LOADED = True
        print("Model loaded successfully.")

    except Exception as e:
        print(f"Error loading model: {e}")


load_model()

global model_path
global response1

@app.route('/generate_question')
def generate_question():
    output = LLM_INSTANCE("""**Instruction :**
    À partir *uniquement* du texte fourni, génère une seule question pertinente en français.
    Ne dépasse pas une seule question. N’ajoute aucun commentaire ni explication.

    Le format de sortie doit être strictement le suivant :
    **Question :** \[question générée]

    **Texte :**
    La plage et la montagne offrent des paysages contrastés. Sur la plage, il y a du sable doré, des vagues qui déferlent et des parasols colorés. Tandis qu'à la montagne, l'air est frais, les cimes sont enneigées et les sentiers sinueux.
    **Question :**""", max_tokens=200, stream=True)

    # print(output["choices"][0]["text"])

    response1 = ""

    for chunk in output:
        print(chunk["choices"][0]["text"], end="", flush=True)
        response1 += chunk["choices"][0]["text"]

    return response1   



@app.route('/correct_answer')
def correct_answer():
    text = """
    La plage et la montagne offrent des paysages contrastés. Sur la plage, il y a du sable doré, des vagues qui déferlent et des parasols colorés. Tandis qu'à la montagne, l'air est frais, les cimes sont enneigées et les sentiers sinueux.
    """

    reponse = "Les paysages de la plage sont typiques avec des plages vert."

    if reponse == "":
        reponse = "l'eleve ne repond pas ! "

   

    # Run inference
    output = LLM_INSTANCE(f"""<|im_start|>system
    Tu es un professeur de français expérimenté. Ton rôle est d’évaluer les réponses des élèves en te basant sur la correction orthographique, la justesse du contenu, la pertinence de la réponse, ainsi que la qualité de l’expression écrite. Sois précis, pédagogique et objectif dans tes corrections.<|im_end|>
    <|im_start|>user
    Corrige la réponse de l'élève uniquement à partir du texte fourni.

    Évalue la réponse en termes de justesse et de pertinence.

    Indique ensuite ce qui est incorrect, puis donne la version corrigée.

    Ne répète pas le texte fourni.

    Arrête-toi directement après la correction.

    Le format de sortie doit être :

    Note : ?/10
    Erreur : Ce qui est incorrect dans la réponse
    Correction : Réponse corrigée

    Texte : {response1}
    Réponse de l’élève : {reponse}<|im_end|>
    <|im_start|>assistant
    """, max_tokens=300, stream=True)
    # print(output["choices"][0]["text"])
    response2 = ""
    for chunk in output:
        print(chunk["choices"][0]["text"], end="", flush=True)
        response2 += chunk["choices"][0]["text"]

    return response2


if __name__ == '__main__':
    app.run(debug=True)
