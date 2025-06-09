import re
import json

def parse_question(text):
    """
    Parses a question from a given text string.
    Expected format: "**Question :** Your question here"
    or "**Question : ** Your question here"
    Returns a JSON string: {"Question": "Your question here"}
    """
    # Regex to match "**Question :" followed by an optional space, then "**", then the question.
    # "\*\*Question :" - matches the literal string "**Question :" (note space before colon)
    # " ?"           - matches an optional space (zero or one occurrence of a space)
    # "\*\*"          - matches the literal string "**"
    # "(.*)"         - captures any characters that follow, as the question.
    match = re.match(r"\*\*Question : ?\*\*(.*)", text)
    if match:
        question = match.group(1).strip()
        return json.dumps({"Question": question}, ensure_ascii=False)
    else:
        # If the expected format is not found, return the original text in the "Question" field
        return json.dumps({"Question": text.strip()}, ensure_ascii=False)

if __name__ == "__main__":
    # Example usage:
    text1 = "**Question :** Quelle est la capitale de la France ?" # No space between : and **
    parsed_json1 = parse_question(text1)
    print(f"Parsed text1: {parsed_json1}") # Expected: {"Question": "Quelle est la capitale de la France ?"}

    text2 = "Ceci est un texte sans le format attendu."
    parsed_json2 = parse_question(text2)
    print(f"Parsed text2: {parsed_json2}") # Expected: {"Question": "Ceci est un texte sans le format attendu."}

    # New test case from original snippet
    test_text_no_space_after_colon = "**Question :** Quels sont les deux composants clés de l'hydrogène et de l'hélium ?"
    parsed_json_test_no_space = parse_question(test_text_no_space_after_colon)
    print(f"Parsed test_text_no_space_after_colon: {parsed_json_test_no_space}") # Expected: {"Question": "Quels sont les deux composants clés de l'hydrogène et de l'hélium ?"}

    # Test case demonstrating the specific fix requested
    print("\nVerification of the specific test case (text1 from prompt):")
    input_str_from_prompt = "**Question :** Quelle est la capitale de la France ?"
    expected_output_str_prompt = json.dumps({"Question": "Quelle est la capitale de la France ?"}, ensure_ascii=False)
    actual_output_str_prompt = parse_question(input_str_from_prompt)
    print(f"Input string: '{input_str_from_prompt}'")
    print(f"Expected JSON: {expected_output_str_prompt}")
    print(f"Actual JSON  : {actual_output_str_prompt}")
    if actual_output_str_prompt == expected_output_str_prompt:
        print("Test case PASSED.")
    else:
        print("Test case FAILED.")

    # Test case with a space between ':' and '**'
    # This format was handled by the original regex in the problem description,
    # but not by the intermediate fix if it was too specific.
    # The new regex r"\*\*Question : ?\*\*(.*)" should handle this.
    text_with_space_after_colon = "**Question : ** This question has a space after the colon before **."
    parsed_json_with_space = parse_question(text_with_space_after_colon)
    print(f"\nTesting a format with space between ':' and '**':")
    print(f"Input: '{text_with_space_after_colon}'")
    print(f"Parsed: {parsed_json_with_space}") # Expected: {"Question": "This question has a space after the colon before **."}

    # Test case with no space after the final '**'
    text_no_leading_space_in_q = "**Question :**What is love?"
    parsed_json_no_leading_space = parse_question(text_no_leading_space_in_q)
    print(f"\nInput: '{text_no_leading_space_in_q}'")
    print(f"Parsed: {parsed_json_no_leading_space}") # Expected: {"Question": "What is love?"}
    
    text_no_leading_space_in_q_variant = "**Question : **What is love now?"
    parsed_json_no_leading_space_variant = parse_question(text_no_leading_space_in_q_variant)
    print(f"\nInput: '{text_no_leading_space_in_q_variant}'")
    print(f"Parsed: {parsed_json_no_leading_space_variant}") # Expected: {"Question": "What is love now?"}

    text_empty_question1 = "**Question :** "
    parsed_empty1 = parse_question(text_empty_question1)
    print(f"\nInput: '{text_empty_question1}'")
    print(f"Parsed: {parsed_empty1}") # Expected: {"Question": ""}

    text_empty_question2 = "**Question : ** "
    parsed_empty2 = parse_question(text_empty_question2)
    print(f"\nInput: '{text_empty_question2}'")
    print(f"Parsed: {parsed_empty2}") # Expected: {"Question": ""}