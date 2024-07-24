import sys
import spacy
from sentence_transformers import SentenceTransformer, util
import torch
from rapidfuzz import fuzz, process
import asyncio
import textwrap

# Load models
nlp = spacy.load('en_core_web_sm')
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Load and preprocess text data
with open('info.txt', 'r', encoding='utf-8') as file:
    text = file.read()

# Split text into chunks based on the section markers
chunks = text.split('[SECTION:')
chunks = ['[SECTION:' + chunk.strip() for chunk in chunks if chunk.strip()]

# Precompute embeddings and NER entities for each chunk
chunk_embeddings = model.encode(chunks, convert_to_tensor=True)
chunk_entities = [[(ent.text.lower(), ent.label_) for ent in nlp(chunk).ents] for chunk in chunks]

MAX_RESULTS = 1
MAX_CHUNK_LENGTH = sys.maxsize  # Maximum length of each returned chunk

def summarize_chunk(chunk):
    if len(chunk) > MAX_CHUNK_LENGTH:
        return textwrap.shorten(chunk, width=MAX_CHUNK_LENGTH, placeholder="...")
    return chunk

async def search_text_with_fuzzy(query):
    results = process.extract(query, chunks, limit=MAX_RESULTS, scorer=fuzz.partial_ratio)
    return [result[0] for result in results if result[1] > 70]

async def search_text_with_ner(query):
    doc = nlp(query)
    query_entities = set((ent.text.lower(), ent.label_) for ent in doc.ents)
    return [chunk for chunk, entities in zip(chunks, chunk_entities) if query_entities.intersection(entities)][:MAX_RESULTS]

async def search_text_with_bert(query):
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(query_embedding, chunk_embeddings)[0]
    top_k = min(MAX_RESULTS, len(chunks))
    top_results = torch.topk(similarities, k=top_k)
    return [chunks[idx] for idx in top_results[1]]

async def get_response(message):
    message = message.lower()
    if '?' in message or len(message.split()) > 2:
        query = message
        fuzzy_results, ner_results, bert_results = await asyncio.gather(
            search_text_with_fuzzy(query),
            search_text_with_ner(query),
            search_text_with_bert(query)
        )

        combined_results = list(set(fuzzy_results + ner_results + bert_results))[:MAX_RESULTS]
        if combined_results:
            summarized_results = [summarize_chunk(chunk) for chunk in combined_results]
            return f'The information related to "{query}" is as follows:\n' + '\n\n'.join(summarized_results)
        else:
            return f'I could not find information related to "{query}".'
    else:
        return 'I didn\'t understand that. Please provide more details or ask a question.'

async def main():
    print('Welcome to the chat! Type "quit" to exit.')
    while True:
        message = input('You: ')
        if message.lower() == 'quit':
            break
        response = await get_response(message)
        print('ChatBot:', response)

if __name__ == "__main__":
    asyncio.run(main())
