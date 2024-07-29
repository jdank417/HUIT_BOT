import os
import sys
import spacy
from sentence_transformers import SentenceTransformer, util
import torch
from rapidfuzz import fuzz, process
import asyncio
import textwrap
import customtkinter as ctk
from PIL import Image
import random
import re
import tkinter as tk
from customtkinter import CTkToplevel, CTkTextbox
import logging
from typing import List, Tuple
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration
def load_config(config_path='config.json') -> dict:
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON configuration file: {config_path}")
        sys.exit(1)

config = load_config()

# Constants from config
MAX_RESULTS = config["max_results"]
MAX_CHUNK_LENGTH = config["max_chunk_length"]
CONVERSATION_HISTORY_LIMIT = config["conversation_history_limit"]
MODEL_NAME = config["model_name"]
TEXT_FILE = config["text_file"]
LOGO_FILE = config["logo_file"]

# Load models
def validate_spacy():
    try:
        nlp = spacy.load('en_core_web_sm')
        print("SpaCy model loaded successfully.")
        return nlp
    except Exception:
        print("SpaCy model not found. Downloading...")
        try:
            os.system("python -m spacy download en_core_web_sm")
            nlp = spacy.load('en_core_web_sm')
            print("SpaCy model loaded successfully after download.")
            return nlp
        except Exception as e:
            print(f"Error loading SpaCy model: {e}")
            return None

nlp = validate_spacy()
model = SentenceTransformer(MODEL_NAME)

# Load and preprocess text data
def load_text_data() -> Tuple[str, List[str], torch.Tensor, List[List[Tuple[str, str]]]]:
    """Read and process text data from file."""
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

text, chunks, chunk_embeddings, chunk_entities = load_text_data()
conversation_context = []

# Utility functions
def summarize_chunk(chunk: str) -> str:
    """Summarize text chunk."""
    chunk = re.sub(r'\[SECTION:[^\]]*\]', '', chunk).strip()
    return textwrap.shorten(chunk, width=MAX_CHUNK_LENGTH, placeholder="...") if len(chunk) > MAX_CHUNK_LENGTH else chunk

def process_response(response: str) -> str:
    """Format response with a random opener."""
    response = '. '.join(sentence.capitalize() for sentence in response.split('. '))
    response = re.sub(' +', ' ', response)
    openers = ["Take a look at this!\n\n", "Check this out:\n\n", "Hmmm, this might just do the trick:\n\n"]
    return random.choice(openers) + response

async def search_text_with_fuzzy(query: str) -> List[str]:
    """Perform fuzzy search on text chunks."""
    if chunks:
        results = process.extract(query, chunks, limit=MAX_RESULTS, scorer=fuzz.partial_ratio)
        return [result[0] for result in results if result[1] > 70]
    return []

async def search_text_with_ner(query: str) -> List[str]:
    """Search text chunks using named entity recognition."""
    doc = nlp(query)
    query_entities = set((ent.text.lower(), ent.label_) for ent in doc.ents)
    return [chunk for chunk, entities in zip(chunks, chunk_entities) if query_entities.intersection(entities)][:MAX_RESULTS]

async def search_text_with_bert(query: str) -> List[str]:
    """Perform semantic search using BERT embeddings."""
    if chunk_embeddings.size(0) > 0:
        query_embedding = model.encode(query, convert_to_tensor=True)
        similarities = util.pytorch_cos_sim(query_embedding, chunk_embeddings)[0]
        top_k = min(MAX_RESULTS, len(chunks))
        top_results = torch.topk(similarities, k=top_k)
        return [chunks[idx] for idx in top_results[1]]
    return []

async def get_response(message: str) -> str:
    """Generate response based on user message."""
    global conversation_context

    query = message.lower()
    if '?' in query or len(query.split()) > 2:
        fuzzy_results, ner_results, bert_results = await asyncio.gather(
            search_text_with_fuzzy(query),
            search_text_with_ner(query),
            search_text_with_bert(query)
        )

        combined_results = list(set(fuzzy_results + ner_results + bert_results))[:MAX_RESULTS]
        if combined_results:
            summarized_results = [summarize_chunk(chunk) for chunk in combined_results]
            info = ' '.join(summarized_results)

            if info in conversation_context:
                response = "I think I've mentioned this before, but to reiterate: " + info
            else:
                response = process_response(info)
                conversation_context.append(info)

            conversation_context = conversation_context[-CONVERSATION_HISTORY_LIMIT:]
            return response

    return ("I'm here to help! Could you please ask a more specific question or provide more details? "
            "If I seem to be having trouble answering, would you please add information related to it to my Knowledge "
            "Base?")

def validate_input(input_text: str) -> str:
    """Sanitize and validate user input."""
    sanitized = input_text.replace('<', '').replace('>', '')
    return sanitized


# GUI Functions
def send_message(event=None):
    """Handle sending of user messages."""
    user_message = user_input.get("1.0", tk.END).strip()
    if user_message:
        display_message(user_message, "user")
        user_input.delete("1.0", tk.END)
        show_loading()
        asyncio.run(process_user_message(user_message))

async def process_user_message(message: str):
    """Process user message and update chat log."""
    global conversation_context
    conversation_context.append(f"User: {message}")
    try:
        response = await get_response(message)
    except Exception as e:
        response = "Sorry, there was an error retrieving the response. Please try again."
        logging.error(f"Error: {e}")
    conversation_context.append(f"Big O: {response}")
    display_message(response, "Big O")
    hide_loading()

def display_message(message: str, sender: str):
    """Display message in chat log."""
    chat_log_text.config(state=tk.NORMAL)
    tag = "user" if sender == "user" else "Big O"
    chat_log_text.insert(tk.END, f"{sender}: {message}\n\n", tag)
    chat_log_text.config(state=tk.DISABLED)
    chat_log_text.yview(tk.END)

def add_new_information():
    """Open a window to add new information."""
    def save_info():
        title = title_entry.get().strip()
        details = details_text.get("1.0", tk.END).strip()
        if title and details:
            try:
                with open(TEXT_FILE, 'a', encoding='utf-8') as file:
                    file.write(f"\n[SECTION: {title}]\n{details}\n")
                new_window.destroy()
                reload_text_data()
            except Exception as e:
                logging.error(f"Error saving new information: {e}")

    new_window = CTkToplevel(root)
    new_window.title("Add New Information")
    new_window.geometry("500x500")

    title_label = ctk.CTkLabel(new_window, text="Title:")
    title_label.pack(pady=(10, 0), padx=10, anchor="w")

    title_entry = ctk.CTkEntry(new_window, width=380)
    title_entry.pack(pady=(0, 10), padx=10)

    details_label = ctk.CTkLabel(new_window, text="Details:")
    details_label.pack(pady=(10, 0), padx=10, anchor="w")

    details_text = CTkTextbox(new_window, width=380, height=250)
    details_text.pack(pady=(0, 10), padx=10)

    save_button = ctk.CTkButton(new_window, text="Save", command=save_info)
    save_button.pack(pady=10)

def reload_text_data():
    """Reload text data from file."""
    global text, chunks, chunk_embeddings, chunk_entities
    text, chunks, chunk_embeddings, chunk_entities = load_text_data()

def show_loading():
    """Show loading indicator."""
    loading_label.pack(side="right", padx=10, pady=10)

def hide_loading():
    """Hide loading indicator."""
    loading_label.pack_forget()

# GUI Setup
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Optimistic Optimizer")
root.geometry("700x600")
root.resizable(True, True)

header_frame = ctk.CTkFrame(root, height=100, bg_color="#780606")
header_frame.pack(fill="x")

try:
    logo_image = Image.open(LOGO_FILE).resize((500, 80), Image.LANCZOS)
    logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(500, 80))
except FileNotFoundError:
    logging.warning("Logo file not found.")
    logo_photo = None

if logo_photo:
    logo_label = ctk.CTkLabel(header_frame, image=logo_photo, text="", font=("Helvetica", 16, "bold"))
    logo_label.pack(side="left", pady=10, padx=10)

teach_button = ctk.CTkButton(header_frame, text="Add Knowledge", width=100, height=30, command=add_new_information)
teach_button.pack(side="right", padx=10, pady=10)

chat_frame = ctk.CTkFrame(root, width=600, height=500, corner_radius=10)
chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

chat_log_text = tk.Text(chat_frame, wrap=tk.WORD, state=tk.DISABLED, bg="#f5f5f5", fg="#333", font=("Helvetica", 12))
chat_log_text.pack(pady=10, padx=10, fill="both", expand=True, side="left")

chat_log_scrollbar = ctk.CTkScrollbar(chat_frame, command=chat_log_text.yview)
chat_log_scrollbar.pack(side="right", fill="y")

loading_label = ctk.CTkLabel(chat_frame, text="Loading...", font=("Helvetica", 12), text_color="#007acc")

chat_log_text.config(yscrollcommand=chat_log_scrollbar.set)
chat_log_text.tag_configure("user", foreground="#0000ff", font=("Helvetica", 12, "bold"))
chat_log_text.tag_configure("Big O", foreground="#333333", font=("Helvetica", 12))

user_input = ctk.CTkTextbox(root, height=50, font=("Helvetica", 12))
user_input.pack(pady=(0, 10), padx=10, fill="x")
user_input.bind("<Return>", send_message)

send_button = ctk.CTkButton(root, text="Send", command=send_message)
send_button.pack(pady=10)

root.mainloop()
