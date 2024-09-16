# json_checker.py

import json
import re

def contains_json(text):
    """
    Verifies if the text contains a valid JSON object.

    Args:
        text (str): The text to analyze.

    Returns:
        bool: True if a valid JSON object is found in the text, False otherwise.
    """
    # Adjusted regex pattern to capture potential JSON blocks
    json_pattern = r'\{(?:[^{}"\'\r\n]+|"[^"]*"|\'[^\']*\')*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)

    for match in matches:
        try:
            # Attempt to parse the JSON
            json.loads(match)
            return True
        except json.JSONDecodeError:
            continue

    return False

# THIS CAN BE USED AS A LIBRARY FUNCTION, AND BE CALLED FROM ANOTHER FILE

if __name__ == "__main__":

    '''
    # Example without JSON
    texto_sin_json = "Hola, este es un texto normal sin JSON."
    print(f"Texto sin JSON: {contains_json(texto_sin_json)}")  # Expected: False

    # Example with JSON within the text as if an agent is speaking
    texto_con_json = """
    Soy un agente inteligente, y creo que veo algo... Sí, aquí está: 
    {"action": "function_call", "function": "start_process", "parameters": {"process_id": 12345}}. 
    Eso es lo que veo, espero que funcione.
    """
    print(f"Texto con JSON: {contains_json(texto_con_json)}")  # Expected: True
    '''