import os
import json
from Agents.llm import generate as llm_generate
from Agents.parse_agent import parse_question

def generate_and_parse_question(input_text: str, model_name: str, focus_text: str = ""): # Added focus_text
    """
    Generates a question using the LLM and then parses it into a JSON format.

    Args:
        input_text (str): The text from which to generate the question.
        model_name (str): The path to the GGUF model file for question generation.
        focus_text (str, optional): A specific part of the text to focus the question on. Defaults to "".

    Returns:
        str: A JSON string containing the parsed question, or an error message.
    """
    generated_question_chunks = []
    try:
        for chunk in llm_generate(input_text, model_name, focus_text): # Pass focus_text
            generated_question_chunks.append(chunk)
        
        full_generated_question = "".join(generated_question_chunks)
        
        # Parse the generated question
        parsed_json = parse_question(full_generated_question)
        return parsed_json
    except Exception as e:
        return json.dumps({"error": f"Error in generation or parsing: {e}"}, ensure_ascii=False)

if __name__ == "__main__":
    # Example usage:
    test_text = "Le soleil est une étoile au centre de notre système solaire. Il est composé principalement d'hydrogène et d'hélium."
    test_focus_text = "hydrogène et d'hélium" # Added focus text for example
    # Ensure this path is correct relative to where generator.py is executed, or absolute.
    # Given the structure, it's likely relative to the project root.
    model_file = "models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf" 
    
    print(f"Attempting to generate and parse with model: {model_file}")
    
    # Get the absolute path for the model file for the generate function
    # This is important because llm.py uses os.getcwd()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir) # Go up one level from Gen-Update to the project root
    absolute_model_path = os.path.join(project_root, model_file)

    # Correcting the model path to be relative to the current working directory
    # as specified in the environment details: /home/med/Windows-Desktop/Git/Generation-question-ouvert/Gen-Update
    # The model is in models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf
    # So the path should be directly 'models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf'
    # if the script is run from Gen-Update.
    # However, llm.py uses os.path.join(os.getcwd(), model_name)
    # So if model_name is 'models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf'
    # and os.getcwd() is '/home/med/Windows-Desktop/Git/Generation-question-ouvert/Gen-Update'
    # then the path becomes '/home/med/Windows-Desktop/Git/Generation-question-ouvert/Gen-Update/models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf'
    # This is correct.

    parsed_result = generate_and_parse_question(test_text, model_file, test_focus_text) # Pass focus_text
    print("\nParsed Result:")
    print(parsed_result)
