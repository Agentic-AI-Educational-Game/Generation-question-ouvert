import os
import json
from flask import Flask, request, jsonify
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure GROQ_API_KEY is set
if not os.getenv("GROQ_API_KEY"):
    print("Error: GROQ_API_KEY environment variable not set.")
    print("Please set it in a .env file or as an environment variable.")
    exit(1)

app = Flask(__name__)

# Global variables for RAG components
qa_chain = None
llm = None # Keep a reference to the LLM for direct use

# 1. Load data from data.jsonl
def load_data(file_path="data.jsonl"):
    texts = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            texts.append(data.get("text", ""))
    return texts

# 2. Generate embeddings and create FAISS vector store
def create_vector_store(texts):
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    print("Creating FAISS vector store...")
    vectorstore = FAISS.from_texts(texts, embeddings)
    print("Vector store created.")
    return vectorstore

# 3. Set up Groq LLM and RetrievalQA chain
def setup_rag_chain(vectorstore):
    global llm # Assign to global llm
    llm = ChatGroq(temperature=0.2, model_name="deepseek-r1-distill-llama-70b") # Increased temperature slightly
    
    qa_chain_instance = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )
    return qa_chain_instance

# Initialize RAG components when the app starts
with app.app_context():
    print("Loading data from data.jsonl...")
    texts = load_data()
    if not texts:
        print("No text data found in data.jsonl. The RAG functionality will be limited.")
    else:
        vectorstore = create_vector_store(texts)
        qa_chain = setup_rag_chain(vectorstore)
        print("\n--- RAG Application Ready ---")

@app.route('/')
def home():
    return "RAG Flask App is running. Use /evaluate_answer endpoint."

@app.route('/evaluate_answer', methods=['POST'])
def evaluate_answer():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    text = data.get("text")
    question = data.get("question")
    student_answer = data.get("student_answer")

    if not all([text, question, student_answer]):
        return jsonify({"error": "Missing text, question, or student_answer in request"}), 400

    if qa_chain is None or llm is None:
        return jsonify({"error": "RAG components not initialized. Check data.jsonl and API key."}), 500

    try:
        # 1. Get the correct answer using the RAG chain
        rag_response = qa_chain.invoke({"query": question + " based on the following text: " + text})
        correct_answer = rag_response.get("result", "No correct answer found.")

        # 2. Use the LLM to evaluate the student's answer
        evaluation_prompt = f"""
        You are an AI assistant specialized in evaluating student answers.
        Given a context text, a question, a correct answer, and a student's answer,
        you need to provide a correction, identify if there's an error, and give an evaluation.
        Note: "réviser mes leçons" (revising my lessons) is considered equivalent to "faire ses devoirs" (doing homework).

        Context: {text}
        Question: {question}
        Correct Answer: {correct_answer}
        Student Answer: {student_answer}

        Please provide your response in a JSON format with the following keys:
        "correction": A detailed correction if the student's answer is wrong or incomplete. If the student's answer is correct, state that it is correct.
        "error": An explanation of the error the student made. If there is no error, state "No error.".
        "evaluation": A score from 0 to 10 in the format (x/10), representing the accuracy of the student's answer.
        """
        
        # Invoke the LLM directly for evaluation
        llm_response = llm.invoke(evaluation_prompt)
        
        # Attempt to parse the LLM's response as JSON
        try:
            # Use regex to extract the JSON part from the LLM's response
            import re
            json_match = re.search(r'\{.*\}', llm_response.content, re.DOTALL)
            if json_match:
                json_string = json_match.group(0)
                evaluation_result = json.loads(json_string)
            else:
                raise ValueError("No JSON object found in LLM response.")
        except (json.JSONDecodeError, ValueError) as e:
            # If LLM doesn't return perfect JSON or no JSON found, return a structured error
            evaluation_result = {
                "correction": "Failed to parse LLM's structured response.",
                "error": f"Parsing error: {e}. Raw LLM output: {llm_response.content}",
                "evaluation": "N/A"
            }

        response_data = {
            "text": text,
            "question": question,
            "student_answer": student_answer,
            "correction": evaluation_result.get("correction", "N/A"),
            "error": evaluation_result.get("error", True),
            "evaluation": evaluation_result.get("evaluation", "N/A")
        }
        return jsonify(response_data)

    except Exception as e:
        print(f"An error occurred during evaluation: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
