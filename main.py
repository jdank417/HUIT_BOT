import spacy
from sentence_transformers import SentenceTransformer, util
import torch
from rapidfuzz import fuzz, process
import asyncio

# Load models
nlp = spacy.load('en_core_web_sm')
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Load and preprocess text data
with open('info.txt', 'r', encoding='utf-8') as file:
    lines = file.read().splitlines()

# Precompute embeddings and NER entities
line_embeddings = model.encode(lines, convert_to_tensor=True)
line_entities = [[(ent.text.lower(), ent.label_) for ent in nlp(line).ents] for line in lines]


async def search_text_with_fuzzy(query):
    results = process.extract(query, lines, limit=5, scorer=fuzz.partial_ratio)
    return [result[0] for result in results if result[1] > 70]


async def search_text_with_ner(query):
    doc = nlp(query)
    query_entities = set((ent.text.lower(), ent.label_) for ent in doc.ents)
    return [line for line, entities in zip(lines, line_entities) if query_entities.intersection(entities)]


async def search_text_with_bert(query):
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(query_embedding, line_embeddings)[0]
    top_k = min(5, len(lines))
    top_results = torch.topk(similarities, k=top_k)
    return [lines[idx] for idx in top_results[1]]


async def get_response(message):
    message = message.lower()
    if '?' in message or len(message.split()) > 2:
        query = message
        fuzzy_results, ner_results, bert_results = await asyncio.gather(
            search_text_with_fuzzy(query),
            search_text_with_ner(query),
            search_text_with_bert(query)
        )

        combined_results = list(set(fuzzy_results + ner_results + bert_results))
        if combined_results:
            return f'The information related to "{query}" is as follows:\n' + '\n'.join(combined_results)
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