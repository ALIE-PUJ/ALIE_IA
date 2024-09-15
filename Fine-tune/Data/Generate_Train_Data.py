from pymongo import MongoClient
import os
import json
import unicodedata
from deep_translator import GoogleTranslator

# Function to normalize text and remove accents
def normalize_text(text):
    if isinstance(text, str):
        # Normalize text to NFD form
        normalized = unicodedata.normalize('NFD', text)
        # Remove accents and diacritics
        no_accent_text = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
        return no_accent_text
    return text

# Function to translate text to English
def translate_to_english(text):
    if not text.strip():
        return text
    translator = GoogleTranslator(source='auto', target='en')
    translation = translator.translate(text)
    print(f"Translating: {text}, Translated: {translation}")
    return translation

# Function to generate JSONL file with both original and translated data
def generate_combined_jsonl_file():
    # Obtain the MongoDB URI from environment variables
    mongo_uri = os.getenv('MONGO_URI')

    # Build the URI if it's not found
    if not mongo_uri:
        print("URI de conexión no encontrada. Construyendo URI de conexión...")
        user = os.getenv('MONGO_USER', 'admin')
        password = os.getenv('MONGO_PASS', 'admin123')
        host = os.getenv('MONGO_HOST', 'localhost')
        mongo_uri = f"mongodb://{user}:{password}@{host}:27017"

    # Initialize the MongoDB Python client
    client = MongoClient(mongo_uri)

    # Select the database (replace 'ALIE_DB' with your actual database name)
    db = client['ALIE_DB']

    # Combine documents from both collections
    combined_documents = []

    # Retrieve documents from 'InformacionPrivada_QA'
    private_collection = db['InformacionPrivada_QA']
    private_documents = private_collection.find()

    # Append and normalize all documents from 'InformacionPrivada_QA'
    for doc in private_documents:
        normalized_doc = {key: normalize_text(value) for key, value in doc.items()}
        combined_documents.append(normalized_doc)

    # Retrieve documents from 'InformacionPublica_QA'
    public_collection = db['InformacionPublica_QA']
    public_documents = public_collection.find()

    # Append and normalize all documents from 'InformacionPublica_QA'
    for doc in public_documents:
        normalized_doc = {key: normalize_text(value) for key, value in doc.items()}
        combined_documents.append(normalized_doc)

    # Prepare combined JSONL output
    script_dir = os.path.dirname(os.path.abspath(__file__))
    jsonl_output_file = 'combined_output.jsonl'
    jsonl_output_path = os.path.join(script_dir, jsonl_output_file)

    with open(jsonl_output_path, 'w', encoding='utf-8') as jsonl_file:
        for doc in combined_documents:
            # Extract category
            category = normalize_text(doc.get('category') or doc.get('Category', ''))
            if 'categories' in doc:
                for cat in doc['categories']:
                    cat_name = normalize_text(cat.get('category') or cat.get('Category', ''))
                    questions = cat.get('questions') or cat.get('Questions', [])
                    
                    for question in questions:
                        # Extract question and answer
                        query = normalize_text(question.get('question') or question.get('Question', ''))
                        answer = normalize_text(question.get('answer') or question.get('Answer', ''))
                        link = question.get('Link') or question.get('link')
                        
                        # Prepare original record
                        if query and answer:
                            record = {
                                "Topic": cat_name,
                                "Query": query,
                                "Answer": answer,
                                "Link": link,  # Add the link field here
                                "Interaction": f"###Human:\n{query}\n\n###Assistant:\n{answer}"
                            }
                            jsonl_file.write(json.dumps(record, ensure_ascii=False) + '\n')

                            # Process subquestions if they exist
                            subquestions = question.get('subquestions') or question.get('Subquestions', [])
                            for subquestion in subquestions:
                                subquery = normalize_text(subquestion)
                                record = {
                                    "Topic": cat_name,
                                    "Query": subquery,
                                    "Answer": answer,
                                    "Link": link,  # Add the link field here
                                    "Interaction": f"###Human:\n{subquery}\n\n###Assistant:\n{answer}"
                                }
                                jsonl_file.write(json.dumps(record, ensure_ascii=False) + '\n')

                        # Translate to English
                        translated_query = translate_to_english(query)
                        translated_answer = translate_to_english(answer)
                        
                        if link:
                            translated_answer += f" {link}"
                        
                        if translated_query and translated_answer:
                            translated_record = {
                                "Topic": cat_name,
                                "Query": translated_query,
                                "Answer": translated_answer,
                                "Link": link,  # Add the link field here
                                "Interaction": f"###Human:\n{translated_query}\n\n###Assistant:\n{translated_answer}"
                            }
                            jsonl_file.write(json.dumps(translated_record, ensure_ascii=False) + '\n')

                            # Process translated subquestions if they exist
                            for subquestion in subquestions:
                                translated_subquery = translate_to_english(subquestion)
                                record = {
                                    "Topic": cat_name,
                                    "Query": translated_subquery,
                                    "Answer": translated_answer,
                                    "Link": link,  # Add the link field here
                                    "Interaction": f"###Human:\n{translated_subquery}\n\n###Assistant:\n{translated_answer}"
                                }
                                jsonl_file.write(json.dumps(record, ensure_ascii=False) + '\n')

    print(f"Combined JSONL file generated at: {jsonl_output_path}")

if __name__ == "__main__":
    generate_combined_jsonl_file()
