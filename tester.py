import spacy

try:
    nlp = spacy.load('en_core_web_sm')
    print("SpaCy model loaded successfully.")
except Exception as e:
    print(f"Error loading SpaCy model: {e}")
