# pip install spacy
# python -m spacy download en_core_web_sm

import spacy
import re

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

def is_natural_language(text):
    # Process the text with spaCy
    doc = nlp(text)
    
    # Check for patterns typical of technical or code text
    code_patterns = re.compile(r'\bfunction\b|\bcall\b|\bargs\b|\[\d*\]|\breturned\b', re.IGNORECASE)
    
    # If the text matches known code or technical patterns, return False
    if code_patterns.search(text):
        return False
    
    # Otherwise, check if the text has a basic grammatical structure
    has_noun = any(token.pos_ == 'NOUN' for token in doc)
    has_verb = any(token.pos_ == 'VERB' for token in doc)
    
    return has_noun and has_verb

# Example texts
text1 = "Data structures course is 4196"
text2 = "Function calling args[123] returned an invalid response"

print(f"Text 1 ('{text1}') is natural language: {is_natural_language(text1)}")
print(f"Text 2 ('{text2}') is natural language: {is_natural_language(text2)}")
