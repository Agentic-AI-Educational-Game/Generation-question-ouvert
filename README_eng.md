# 🧠 AI-Powered Question Generation System

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![LLM](https://img.shields.io/badge/LLM-FF69B4?style=for-the-badge&logo=tensorflow&logoColor=white) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

## Project Overview

This project presents a robust AI-powered system designed to generate open-ended questions in French from provided text, leveraging a local Large Language Model (LLM). It offers dual interfaces for flexibility: a user-friendly Streamlit application for rapid prototyping and testing, and a Flask web application integrated with MongoDB for persistent storage and a more traditional web experience. The system is capable of focusing question generation on specific parts of the input text, making it highly adaptable for various educational or analytical purposes.

![Arch](screenshots/gen-question.png)

## ✨ Features

*   **Local LLM Integration:** Utilizes a local GGUF-formatted Large Language Model for question generation, ensuring privacy and offline capability.
*   **Dual User Interfaces:**
    *   **Streamlit App:** A simple, interactive web interface for quick text input and question generation.
    *   **Flask Web App:** A more comprehensive web application with a dedicated frontend (`index.html`) and backend for question generation and storage.
*   **MongoDB Integration:** The Flask application seamlessly integrates with MongoDB to store generated questions, original input text, and timestamps for historical tracking and analysis.
*   **Contextual Question Generation:** Ability to focus question generation on specific segments of the input text, allowing for precise and relevant questions.
*   **Structured Output:** LLM output is parsed into a structured JSON format for easy consumption and integration.
*   **Dockerized MongoDB:** Includes a Docker Compose setup for easy deployment of MongoDB and Mongo Express (a web-based MongoDB administration interface).

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)
*   Docker and Docker Compose (for MongoDB setup)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Gen-Update.git
cd Gen-Update
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory of the project based on the `.env-example` file:

```bash
cp .env-example .env
```

Edit the `.env` file with your specific configurations:

```
MONGO_URI=mongodb://root:example@localhost:27017/
MONGO_DB_NAME=question_db
MONGO_COLLECTION_NAME=generated_questions
MODEL_PATH=./models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf
```

*   `MONGO_URI`: Connection string for your MongoDB instance.
*   `MONGO_DB_NAME`: Name of the database to use.
*   `MONGO_COLLECTION_NAME`: Name of the collection for storing questions.
*   `MODEL_PATH`: Relative path to your GGUF model file.

### 3. Download the LLM Model

The project uses a local GGUF model. You need to download the `finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf` model and place it in the `models/` directory.

*(Provide a link to download the model here if available, or instructions on how to obtain it)*

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```
*(Note: A `requirements.txt` file is assumed. If not present, I would create one.)*

### 5. Run MongoDB with Docker Compose

Navigate to the project root and start the MongoDB and Mongo Express services:

```bash
docker-compose -f mongo.yml up -d
```

This will start MongoDB on `localhost:27017` and Mongo Express (web UI for MongoDB) on `localhost:8081`. You can access Mongo Express in your browser at `http://localhost:8081` using the credentials defined in `mongo.yml` (e.g., `root`/`example`).

![Mongo Express Interface](screenshots/mongo.png)

## 💡 Usage

### Streamlit Application

To run the Streamlit application:

```bash
streamlit run app.py
```

Open your web browser and navigate to the address provided by Streamlit (usually `http://localhost:8501`).

*   Enter your text in the "Input Text" area.
*   Optionally, specify a "Focus Text" to guide the question generation.
*   Click "Generate Question".

![Streamlit App Initial State/Success](screenshots/streamlit-1.png)
![Streamlit App Another View/Error](screenshots/streamlit-2.png)

### Flask Web Application

To run the Flask web application:

```bash
python flask-app.py
```

The application will be available at `http://127.0.0.1:5000/`.

*   Access the main page to input text and generate questions.
*   The generated questions will be stored in your configured MongoDB collection.

![Flask App UI](screenshots/flask-app.png)
![Flask App Command Line](screenshots/flask-cmd.png)
