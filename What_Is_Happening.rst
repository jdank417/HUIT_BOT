========================
The Optimistic Optimizer
========================

Overview
========
This program is a Python-based chatbot application that uses Natural Language Processing (NLP) techniques to retrieve and respond to user queries. The application features a graphical user interface (GUI) built using the `customtkinter` library, and it leverages several advanced NLP models and techniques for understanding and responding to text-based inputs. The chatbot is capable of fuzzy searching, semantic searching using BERT embeddings, and named entity recognition (NER) based search. Additionally, the application allows users to add new knowledge, which is stored and used in future interactions.

Key Components
==============
1. Imports and Setup
---------------------
The program imports a variety of libraries to handle different aspects of its functionality:

* **os, sys**: For file handling and system operations.
* **spacy**: For NLP tasks, particularly named entity recognition.
* **SentenceTransformer, util**: For semantic search using BERT embeddings.
* **torch**: For tensor operations related to embeddings.
* **rapidfuzz**: For fuzzy string matching.
* **asyncio**: For asynchronous operations.
* **textwrap**: For text formatting.
* **customtkinter, tkinter**: For GUI creation and management.
* **PIL**: For image handling in the GUI.
* **random**: For generating random elements such as response openers.
* **re**: For regular expression operations, particularly in text processing.
* **logging**: For logging and debugging purposes.
* **json**: For reading and writing configuration files.
* **matplotlib**: For potential future data visualization (though not actively used in this program).

Logging is configured at the start of the program to capture important events, errors, and warnings.

2. Configuration Loading
-------------------------
The program reads configuration settings from a `config.json` file using the `load_config()` function. The configuration contains key parameters such as:

* **MAX_RESULTS**: The maximum number of results to return from searches.
* **MAX_CHUNK_LENGTH**: The maximum length of a text chunk before it gets summarized.
* **CONVERSATION_HISTORY_LIMIT**: Limits the number of conversation history items stored.
* **MODEL_NAME**: The name of the BERT model used for embeddings.
* **TEXT_FILE**: The path to the file containing text data for the chatbot.
* **LOGO_FILE**: The path to the logo image for the GUI.

The function handles errors such as missing or improperly formatted configuration files and exits the program if critical errors are encountered.

3. Model Validation and Loading
-------------------------------
* **SpaCy Model Validation**:
  The `validate_spacy()` function ensures that the required SpaCy model (`en_core_web_sm`) is loaded. If the model is not found, it attempts to download and load it.
  This ensures that the application has the necessary NLP tools for tasks like named entity recognition.

* **SentenceTransformer Model Loading**:
  The program loads the SentenceTransformer model specified in the configuration file using `SentenceTransformer(MODEL_NAME)`.
  This model is used for generating embeddings for semantic search.

4. Text Data Processing
-----------------------
The program reads text data from a file specified by `TEXT_FILE` in the configuration. This data is preprocessed into chunks, each associated with:

* **Text Content**: The raw text divided into chunks based on sections.
* **Embeddings**: BERT embeddings for each chunk, allowing for semantic similarity search.
* **Named Entities**: Entities recognized in each chunk by the SpaCy model.

The `load_text_data()` function handles this process, splitting the text into chunks using a predefined section marker (`[SECTION:]`). These chunks are then embedded and tagged with named entities for later search operations.

5. Search and Response Functions
--------------------------------
* **Summarization**:
  The `summarize_chunk()` function summarizes text chunks that exceed a certain length, as defined by `MAX_CHUNK_LENGTH`. This prevents overly long responses from cluttering the chat.

* **Response Processing**:
  The `process_response()` function formats responses by adding a random opener from a predefined list. This makes the chatbot's responses appear more conversational and less robotic.

* **Search Operations**:
  The program supports three types of search:
  - **Fuzzy Search**: Using the `rapidfuzz` library to match user queries against chunks with partial ratio scoring.
  - **NER-based Search**: Using SpaCy to match entities in the user query with entities in the text chunks.
  - **Semantic Search**: Using BERT embeddings to find the most semantically similar text chunks to the user query.

The search functions (`search_text_with_fuzzy`, `search_text_with_ner`, and `search_text_with_bert`) are asynchronous, allowing them to be executed in parallel to improve performance.

* **Response Generation**:
  The `get_response()` function determines which search method(s) to use based on the user query. It then combines the results, summarizes them, and formats the final response.
  The program maintains a conversation history to avoid repetitive responses and to provide continuity in the conversation.

6. GUI Setup
------------
* **Appearance and Theme**:
  The GUI is set up using `customtkinter`, which allows for a more modern look and feel compared to standard `tkinter`.
  The application window (`root`) is configured with a title, dimensions, and resizability options.

* **Header and Logo**:
  A header frame is created at the top of the window, which includes the application logo and a button for adding new information. If the logo file is missing, a warning is logged, but the application continues running.

* **Chat Log**:
  The main area of the GUI is a chat log where messages from both the user and the chatbot are displayed. This is implemented using a `tk.Text` widget.
  A scrollbar is attached to the chat log for easy navigation.
  The chat log is configured to display messages in different styles depending on the sender (user or chatbot).

* **User Input**:
  Below the chat log, there is a text input field where users can type their messages. A "Send" button is provided to submit the message.
  The input field is linked to the `send_message()` function, which handles message submission and processing.

* **Loading Indicator**:
  A loading label is included to inform the user when the chatbot is processing a request. This label is shown or hidden based on the application's state.

7. Interactivity and User Functions
-----------------------------------
* **Message Sending and Processing**:
  The `send_message()` function captures the user's message, displays it in the chat log, and triggers the processing functions.
  `process_user_message()` handles the logic for processing the message, including searching the text data and generating a response.
  The response is then displayed in the chat log, and the loading indicator is hidden.

* **Adding New Information**:
  Users can add new knowledge to the chatbot via the "Add Knowledge" button. This opens a new window where the user can input a title and details for the new information.
  The new information is appended to the text file, and the text data is reloaded to include the new content in future interactions.

* **Conversation Context**:
  The program maintains a conversation context, which stores the history of recent interactions. This helps the chatbot to avoid repeating itself and provides a sense of continuity in the conversation.

8. Error Handling and Logging
-----------------------------
Throughout the program, various `try-except` blocks are used to handle potential errors, such as missing files, invalid inputs, or issues with model loading.
Logging is used extensively to track the program's execution and capture any errors or warnings. This is crucial for debugging and ensuring the program's reliability.

9. Future Considerations
------------------------
* **Performance Optimization**:
  In the future I plan on ditching the info.txt file for somthing more efficient that I can iterate through like a dictionary or ultimately a SQL Database.

* **Security**:
  Ensure that user inputs are sanitized to prevent injection attacks or other security vulnerabilities.

* **Extensibility**:
  The program is designed to be modular, which makes it easier to extend with new features or integrate with other systems.

10. Conclusion
--------------
The Optimistic Optimizer chatbot application demonstrates the power of NLP techniques in creating interactive and engaging user experiences. By leveraging advanced models like BERT and SpaCy, the chatbot can understand user queries, retrieve relevant information, and provide meaningful responses. The combination of fuzzy searching, semantic search, and named entity recognition enhances the chatbot's capabilities and makes it more versatile in handling a wide range of user inputs. With a user-friendly GUI and robust error handling, the chatbot offers a seamless experience for users while maintaining reliability and performance.

@author
-------
* Jason Dank
