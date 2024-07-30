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


Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.


Acknowledgments
Special thanks to the creators of SpaCy, SentenceTransformer, and customTkinter for their excellent tools and libraries.
