import streamlit as st
import os
import json
from generator import generate_and_parse_question # Import the new function
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

# Define the path to your GGUF model file
MODEL_PATH = os.getenv('MODEL_PATH', "models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf")

st.set_page_config(page_title="Générateur de Questions Streamlit", layout="centered")

st.title("Générateur de Questions par IA (Streamlit)")

st.write("Entrez du texte pour générer une question basée sur celui-ci à l'aide d'un LLM local.")

# Input field for main text
input_text = st.text_area(
    "Texte d'entrée :",
    "Le soleil est une étoile au centre de notre système solaire. Il est composé principalement d'hydrogène et d'hélium.",
    height=250,
    help="Fournissez le texte à partir duquel générer une question."
)

# Input field for focus text
focus_text = st.text_area(
    "Partie du texte sur laquelle se concentrer (Facultatif) :",
    "hydrogène et d'hélium",
    height=100,
    help="Spécifiez une partie du texte sur laquelle la question doit se concentrer."
)

if st.button("Générer la question"):
    if not input_text:
        st.error("Veuillez fournir un texte en entrée.")
    else:
        # Check if the model file exists
        if not os.path.exists(MODEL_PATH):
            st.error(f"Erreur : Fichier modèle introuvable à {MODEL_PATH}")
            st.warning("Veuillez vous assurer que 'models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf' existe dans le répertoire de votre projet.")
        else:
            with st.spinner("Génération de la question..."):
                try:
                    parsed_result = generate_and_parse_question(input_text, MODEL_PATH, focus_text) # Pass focus_text
                    
                    if isinstance(parsed_result, str):
                        try:
                            parsed_data = json.loads(parsed_result)
                        except json.JSONDecodeError:
                            st.error(f"Le générateur a renvoyé un JSON invalide : {parsed_result}")
                            parsed_data = {"error": "Réponse JSON invalide du générateur."}
                    else:
                        parsed_data = parsed_result # Assume it's already a dict/json object

                    if "error" in parsed_data:
                        st.error(f"Erreur du générateur : {parsed_data['error']}")
                    elif "Question" in parsed_data: # Changed to "Question" (capital Q)
                        st.subheader("Question générée :")
                        st.success(parsed_data["Question"]) # Access with capital Q
                    else:
                        st.error("Question générée introuvable dans la réponse.")

                except Exception as e:
                    st.error(f"Une erreur est survenue pendant la génération : {e}")

st.markdown(
    """
    ---
    *Cette application utilise un LLM local (Llama-CPP) pour générer des questions.*
    """
)
