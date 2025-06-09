from llama_cpp import Llama
import os

def generate(input_text: str, model_name: str, focus_text: str = ""): # Added focus_text parameter
    """
    Generates text using a Llama-CPP model with streaming output.

    Args:
        input_text (str): The text to generate a question from.
        model_name (str): The path to the GGUF model file.
        focus_text (str, optional): A specific part of the text to focus the question on. Defaults to "".

    Yields:
        str: Chunks of the generated text.
    """
    try:
        # Ensure the model path is absolute or correctly relative to the current working directory
        model_path = os.path.join(os.getcwd(), model_name)
        
        # Initialize the Llama model
        llm = Llama(model_path=model_path, n_ctx=2048, n_gpu_layers=0, verbose=False) # n_gpu_layers=0 to use CPU only

        # Define the instruction for the model
        system_instruction = """<|im_start|>system
You are an expert question-generation assistant.
When the user gives you a block of text, you must:
1. Generate exactly one relevant question in French based solely on the provided text.
2. Never add any comments, explanations, or additional questions.
3. Use the exact output format:

**Question :** [votre question]

Always follow this layout strictly, with no extra lines or sections.
<|im_end|>
"""
        user_instruction = """<|im_start|>user
**Instruction :**
À partir *uniquement* du texte fourni, génère une seule question pertinente en français.
Ne dépasse pas une seule question. N’ajoute aucun commentaire ni explication.
"""
        if focus_text:
            user_instruction += f"La question doit se concentrer spécifiquement sur la partie du texte suivante : \"{focus_text}\"\n"

        user_instruction += """
Le format de sortie doit être strictement le suivant :
**Question :** [question générée]

**Texte :**
{input_text}
<|im_end|>
<|im_start|>assistant
"""

        # Create the full prompt
        full_prompt = system_instruction + user_instruction.format(input_text=input_text)

        # Generate completion with streaming
        for chunk in llm.create_completion(
            full_prompt,
            max_tokens=512,  # Adjust as needed
            stop=["<|im_end|>"],  # Stop generation at the end of the assistant's turn
            echo=False,
            stream=True, # Enable streaming
            temperature=0.7, # Adjust as needed
            top_p=0.95, # Adjust as needed
        ):
            yield chunk["choices"][0]["text"]
    except Exception as e:
        yield f"Error during LLM generation: {e}"

if __name__ == "__main__":
    # Example usage (for testing purposes)
    # Make sure models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf exists for this to work
    test_text = "Le soleil est une étoile au centre de notre système solaire. Il est composé principalement d'hydrogène et d'hélium."
    test_focus_text = "hydrogène et d'hélium"
    model_file = "/home/med/Windows-Desktop/Git/Generation-question-ouvert/Gen-Update/models/finetuned-qwen2.5-0.5B_instruct_finetuned_fr.q8_0.gguf" 
    
    print(f"Attempting to generate with model: {model_file}")
    print("\nGenerated Question (streaming):")
    for chunk in generate(test_text, model_file, test_focus_text): # Pass focus_text
        print(chunk, end="", flush=True)
    print()
