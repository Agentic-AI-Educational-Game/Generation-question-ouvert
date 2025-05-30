import streamlit as st
import requests
import json
from pypdf import PdfReader

st.title("Question Generation App")

# PDF Uploader
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

# Common input text area
if 'common_text_input_value' not in st.session_state:
    st.session_state.common_text_input_value = "Je m'appelle Salma. Je vais vous parler de la maison où j'habite avec ma famille. Dans ma maison, il y a plusieurs pièces, chacune avec un rôle important. Dans la cuisine, on prépare de délicieux repas. Dans le salon, toute la famille s'installe sur le canapé pour discuter et regarder la télévision. La salle de bain est l'endroit où je me lave, où je me brosse les dents et où je coiffe mes cheveux. Dans ma chambre, je révise mes leçons, je m'habille et je dors dans mon lit. Un jour, je t'inviterai à venir chez moi!"

if uploaded_file is not None:
    try:
        reader = PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() + "\n"
        st.session_state.common_text_input_value = pdf_text
        st.success("PDF content loaded into text area.")
    except Exception as e:
        st.error(f"Error reading PDF: {e}")

input_text = st.text_area(
    "Enter text:",
    value=st.session_state.common_text_input_value,
    height=200,
    key="common_text_input"
)

if st.button("Generate Question"):
    if input_text:
        url = "http://127.0.0.1:5000/generate_question"
        headers = {"Content-Type": "application/json"}
        payload = {"text": input_text}

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            
            result = response.json()

            st.subheader("Generated Question:")
            st.write(result.get("question", "No question found."))
            
            st.subheader("Raw Response:")
            st.code(result.get("raw", "No raw response found."))

        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Make sure the Flask server is running at http://127.00.1:5000")
        except requests.exceptions.Timeout:
            st.error("The request timed out.")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter some text to generate a question.")

st.subheader("Evaluate Student Answer")
evaluation_question = st.text_input(
    "Enter the question:",
    "Où Salma fait-elle ses devoirs?",
    key="evaluation_question"
)
student_answer = st.text_input(
    "Enter the student's answer:",
    "sa chambre  ",
    key="student_answer"
)

if st.button("Evaluate Answer"):
    if input_text and evaluation_question and student_answer:
        url = "http://127.0.0.1:5000/evaluate_answer" # Assuming a new endpoint for evaluation
        headers = {"Content-Type": "application/json"}
        payload = {
            "text": input_text, # Use the common input_text
            "question": evaluation_question,
            "student_answer": student_answer
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            
            result = response.json()

            st.subheader("Evaluation Result:")
            st.session_state.correction_result = result.get('correction', 'N/A')
            st.session_state.evaluation_result = result.get('evaluation', 'N/A')
            st.session_state.error_result = result.get('error', 'N/A')
            

            st.subheader("Raw Evaluation Response:")
            st.code(result)

        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Make sure the Flask server is running at http://127.00.1:5000")
            st.session_state.correction_result = 'N/A'
            st.session_state.evaluation_result = 'N/A'
            st.session_state.error_result = 'Connection Error'
        except requests.exceptions.Timeout:
            st.error("The request timed out.")
            st.session_state.correction_result = 'N/A'
            st.session_state.evaluation_result = 'N/A'
            st.session_state.error_result = 'Timeout Error'
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
            st.session_state.correction_result = 'N/A'
            st.session_state.evaluation_result = 'N/A'
            st.session_state.error_result = f"Request Error: {e}"
    else:
        st.warning("Please fill in all fields to evaluate the answer.")
        st.session_state.correction_result = 'N/A'
        st.session_state.evaluation_result = 'N/A'
        st.session_state.error_result = 'Missing fields'

# Initialize session state for evaluation results if not already present
if 'correction_result' not in st.session_state:
    st.session_state.correction_result = 'N/A'
if 'evaluation_result' not in st.session_state:
    st.session_state.evaluation_result = 'N/A'
if 'error_result' not in st.session_state:
    st.session_state.error_result = 'N/A'

st.subheader("Current Evaluation Results (Editable):")
st.text_input("Correction:", value=st.session_state.correction_result, key="correction_input")
st.text_input("Evaluation:", value=st.session_state.evaluation_result, key="evaluation_input")
st.text_input("Error:", value=st.session_state.error_result, key="error_input")
