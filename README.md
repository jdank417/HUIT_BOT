**The Optimistic Optimizer**

This project implements a chatbot that provides information based on text search using various techniques: fuzzy matching, Named Entity Recognition (NER), and BERT embeddings. The bot can process user queries to find relevant lines from a text file and return the most pertinent information.

This project utilizes en_core_web_sm a CNN for natural Language processing by Assigning context-specific token vectors, POS tags, dependency parse, and named entities
**Features**

Fuzzy Matching: Uses the rapidfuzz library to find lines similar to the query text.
Named Entity Recognition: Leverages spaCy to extract entities from both the query and text lines, matching entities for relevant results.
Semantic Search with BERT: Utilizes the sentence-transformers library to compute semantic embeddings for improved relevance matching.
Asynchronous Processing: Uses asyncio for efficient query handling and response generation.

**Requirements**

Python 3.7+
spacy
sentence-transformers
torch
rapidfuzz
Installation


**Prepare Your Data:** Create a text file named info.txt in the same directory as the script. This file should contain the lines of text that the chatbot will search through.

