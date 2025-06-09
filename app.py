import streamlit as st
import os
import json
from generator import generate_and_parse_question # Import the new function
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

# Define the path to your GGUF model file
MODEL_PATH = os.getenv('MODEL_PATH', "models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf")

st.set_page_config(page_title="Streamlit Question Generator", layout="centered")

st.title("AI Question Generator (Streamlit)")

st.write("Enter text to generate a question based on it using a local LLM.")

# Input field for main text
input_text = st.text_area(
    "Input Text:",
    "Le soleil est une étoile au centre de notre système solaire. Il est composé principalement d'hydrogène et d'hélium.",
    height=250,
    help="Provide the text from which to generate a question."
)

# Input field for focus text
focus_text = st.text_area(
    "Part of Text to Focus On (Optional):",
    "hydrogène et d'hélium",
    height=100,
    help="Specify a part of the text for the question to focus on."
)

if st.button("Generate Question"):
    if not input_text:
        st.error("Please provide text input.")
    else:
        # Check if the model file exists
        if not os.path.exists(MODEL_PATH):
            st.error(f"Error: Model file not found at {MODEL_PATH}")
            st.warning("Please ensure 'models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf' exists in your project directory.")
        else:
            with st.spinner("Generating question..."):
                try:
                    parsed_result = generate_and_parse_question(input_text, MODEL_PATH, focus_text) # Pass focus_text
                    
                    if isinstance(parsed_result, str):
                        try:
                            parsed_data = json.loads(parsed_result)
                        except json.JSONDecodeError:
                            st.error(f"Generator returned invalid JSON: {parsed_result}")
                            parsed_data = {"error": "Invalid JSON response from generator."}
                    else:
                        parsed_data = parsed_result # Assume it's already a dict/json object

                    if "error" in parsed_data:
                        st.error(f"Error from generator: {parsed_data['error']}")
                    elif "Question" in parsed_data: # Changed to "Question" (capital Q)
                        st.subheader("Generated Question:")
                        st.success(parsed_data["Question"]) # Access with capital Q
                    else:
                        st.error("Generated question not found in response.")

                except Exception as e:
                    st.error(f"An error occurred during generation: {e}")

st.markdown(
    """
    ---
    *This application uses a local LLM (Llama-CPP) to generate questions.*
    """
)
