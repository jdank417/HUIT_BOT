**Optimistic Optimizer**

The Optimistic Optimizer is an intelligent text-based assistant built using customTkinter for the GUI, integrated with advanced NLP and semantic search capabilities. It leverages SpaCy for named entity recognition and the SentenceTransformer for semantic text search, offering a rich and interactive user experience.

**Features**
Interactive GUI: A sleek and responsive interface built with customTkinter.
Natural Language Processing: Utilizes SpaCy for named entity recognition and preprocessing.
Semantic Search: Integrates SentenceTransformer to perform semantic text searches.
Fuzzy Search: Employs rapidfuzz for efficient fuzzy matching.
Configurable Settings: Easily adjustable settings through a JSON configuration file.
Dynamic Text Handling: Processes and manages large text datasets efficiently, splitting them into manageable chunks and summarizing them.
Conversation History: Maintains a context-aware conversation history.
User-Friendly Input: Provides functionality to add new information to the text dataset dynamically.

**Installation**
Prerequisites
Python 3.7 or higher
Required Python packages (listed in requirements.txt)


**Usage**
Run the application:

bash
Copy code
python main.py
Using the GUI:

Send Messages: Type your message in the input box and press Enter or click the "Send" button.
Add Knowledge: Click the "Add Knowledge" button to open a new window where you can add new information to the text dataset.

**Code Overview**

Main Components
Configuration and Constants:

Loads configuration settings from config.json.
Sets up logging and constant parameters.
Model Initialization:

Validates and loads the SpaCy model.
Loads the SentenceTransformer model specified in the configuration.
Text Data Processing:

Loads and preprocesses text data, splitting it into chunks and computing embeddings.
Extracts named entities from each chunk.
Utility Functions:

Summarizes text chunks and formats responses.
Implements fuzzy search, NER-based search, and BERT-based semantic search.
GUI Functions:

Handles user inputs and displays messages in the chat log.
Provides functionality to add new information to the text dataset dynamically.
Example Code Snippets

**Loading Configuration:**
def load_config(config_path='config.json') -> dict:
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON configuration file: {config_path}")
        sys.exit(1)
        
**Loading and Preprocessing Text Data:**
def load_text_data() -> Tuple[str, List[str], torch.Tensor, List[List[Tuple[str, str]]]]:
    try:
        with open(TEXT_FILE, 'r', encoding='utf-8') as file:
            text = file.read().strip()
    except FileNotFoundError:
        logging.warning("Text file not found.")
        text = ""

    chunks = ['[SECTION:' + chunk.strip() for chunk in text.split('[SECTION:') if chunk.strip()]

    if chunks:
        chunk_embeddings = model.encode(chunks, convert_to_tensor=True)
        chunk_entities = [[(ent.text.lower(), ent.label_) for ent in nlp(chunk).ents] for chunk in chunks]
    else:
        chunk_embeddings = torch.tensor([])
        chunk_entities = []

    return text, chunks, chunk_embeddings, chunk_entities


**Performing Semantic Search:**
async def search_text_with_bert(query: str) -> List[str]:
    if chunk_embeddings.size(0) > 0:
        query_embedding = model.encode(query, convert_to_tensor=True)
        similarities = util.pytorch_cos_sim(query_embedding, chunk_embeddings)[0]
        top_k = min(MAX_RESULTS, len(chunks))
        top_results = torch.topk(similarities, k=top_k)
        return [chunks[idx] for idx in top_results[1]]
    return []


Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.


Acknowledgments
Special thanks to the creators of SpaCy, SentenceTransformer, and customTkinter for their excellent tools and libraries.
