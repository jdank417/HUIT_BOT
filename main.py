import spacy
from sentence_transformers import SentenceTransformer, util
import torch
from fuzzywuzzy import fuzz


# Load the text file
with open('info.txt', 'r', encoding='utf-8') as file:
    text_data = file.read()

# Load SpaCy and BERT models
nlp = spacy.load('en_core_web_sm')
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Precompute embeddings for text data
lines = text_data.splitlines()
line_embeddings = model.encode(lines, convert_to_tensor=True)

# Define a function to search for information with fuzzy matching
def search_text_with_fuzzy(query):
    query = query.lower()
    results = []
    for line in lines:
        if fuzz.partial_ratio(query, line.lower()) > 70:  # Adjust the threshold as needed
            results.append(line)
    return results

# Define a function to search for information with NER
def search_text_with_ner(query):
    doc = nlp(query)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    results = []
    for line in lines:
        if any(ent[0].lower() in line.lower() for ent in entities):
            results.append(line)
    return results

# Define a function to search for information with BERT
def search_text_with_bert(query):
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(query_embedding, line_embeddings)[0]
    top_k = min(5, len(lines))
    top_results = torch.topk(similarities, k=top_k)
    results = [lines[idx] for idx in top_results[1]]
    return results

# Define a function to get a response
def get_response(message):
    message = message.lower()
    if message.startswith('search '):
        query = message.replace('search ', '')
        fuzzy_results = search_text_with_fuzzy(query)
        ner_results = search_text_with_ner(query)
        bert_results = search_text_with_bert(query)

        combined_results = list(set(fuzzy_results + ner_results + bert_results))
        if combined_results:
            return '\n'.join(combined_results)
        else:
            return 'No results found.'
    elif message.startswith('find '):
        query = message.replace('find ', '')
        fuzzy_results = search_text_with_fuzzy(query)
        ner_results = search_text_with_ner(query)
        bert_results = search_text_with_bert(query)

        combined_results = list(set(fuzzy_results + ner_results + bert_results))
        if combined_results:
            return '\n'.join(combined_results)
        else:
            return 'No results found.'
    else:
        return 'I didn\'t understand that. Try searching with "search" or "find".'

# Start the chat
print('Welcome to the chat! Type "quit" to exit.')
while True:
    message = input('You: ')
    if message.lower() == 'quit':
        break
    response = get_response(message)
    print('ChatBot:', response)
