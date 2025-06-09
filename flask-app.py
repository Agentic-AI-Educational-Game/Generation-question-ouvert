from flask import Flask, render_template, request, jsonify
import os
import json # Import the json module
import re # Import the re module for regex
from generator import generate_and_parse_question # Import the new function
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

app = Flask(__name__, template_folder='templates')

# MongoDB connection
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongo_uri) # Connect to your MongoDB instance
db_name = os.getenv('MONGO_DB_NAME', 'question_app')
db = client[db_name] # Choose a database name
collection_name = os.getenv('MONGO_COLLECTION_NAME', 'questions')
questions_collection = db[collection_name] # Choose a collection name

# Define the path to your GGUF model file
MODEL_PATH = os.getenv('MODEL_PATH', "models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_question', methods=['POST'])
def generate_question():
    data = request.get_json() # Get JSON data
    if not data:
        return jsonify({"error": "Invalid JSON or missing data."}), 400
    
    input_text = data.get('text') # Get main text input
    focus_text = data.get('focus_text', '') # Get optional focus text input

    if not input_text:
        return jsonify({"error": "Text input is required."}), 400

    try:
        parsed_result = generate_and_parse_question(input_text, MODEL_PATH, focus_text) # Pass focus_text
        
        print(f"DEBUG: parsed_result from generator: {parsed_result}, type: {type(parsed_result)}") # Debug print

        # Check if parsed_result is a string (JSON string) and load it
        if isinstance(parsed_result, str):
            parsed_data = json.loads(parsed_result)
        else:
            parsed_data = parsed_result # Assume it's already a dict/json object

        if "error" in parsed_data:
            return jsonify({"error": parsed_data["error"]}), 500
        elif "Question" in parsed_data: # Changed to "Question" (capital Q)
            question_text = parsed_data["Question"]
            
            # Clean the question text using regex
            # This removes "Question : \n" or "Question:\n" or "Question: " or "Question : " from the beginning
            question_text = re.sub(r"^[Qq]uestion\s*:\s*\n*", "", question_text).strip()

            # Save to MongoDB
            try:
                timestamp = datetime.utcnow()
                result = questions_collection.insert_one({
                    "input_text": input_text,
                    "question": question_text,
                    "timestamp": timestamp
                })
                print("DEBUG: Data saved to MongoDB successfully.")
                
                # Prepare the response with the desired format
                response_data = {
                    "_id": str(result.inserted_id), # Convert ObjectId to string
                    "input_text": input_text,
                    "question": question_text,
                    "timestamp": timestamp.isoformat() + "Z" # ISO 8601 format with 'Z' for UTC
                }
                return jsonify(response_data)
            except Exception as mongo_e:
                print(f"ERROR: Failed to save to MongoDB: {mongo_e}")
                return jsonify({"error": f"Failed to save question: {mongo_e}"}), 500
        else:
            return jsonify({"error": "Generated question not found in response."}), 500
    except json.JSONDecodeError:
        return jsonify({"error": f"Generator returned invalid JSON: {parsed_result}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Check if the model file exists
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file not found at {MODEL_PATH}")
        print("Please ensure 'models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf' exists in your project directory.")
    else:
        app.run(debug=True)
