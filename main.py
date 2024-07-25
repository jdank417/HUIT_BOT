import sys
import spacy
from sentence_transformers import SentenceTransformer, util
import torch
from rapidfuzz import fuzz, process
import asyncio
import textwrap
import customtkinter as ctk
from PIL import Image, ImageTk
import random
import re
import tkinter as tk
from customtkinter import CTkToplevel, CTkTextbox

# Load models
nlp = spacy.load('en_core_web_sm')
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Load and preprocess text data
try:
    with open('info.txt', 'r', encoding='utf-8') as file:
        text = file.read().strip()
except FileNotFoundError:
    text = ""

# Split text into chunks based on the section markers
if text:
    chunks = text.split('[SECTION:')
    chunks = ['[SECTION:' + chunk.strip() for chunk in chunks if chunk.strip()]
else:
    chunks = []

# Precompute embeddings and NER entities for each chunk
if chunks:
    chunk_embeddings = model.encode(chunks, convert_to_tensor=True)
    chunk_entities = [[(ent.text.lower(), ent.label_) for ent in nlp(chunk).ents] for chunk in chunks]
else:
    chunk_embeddings = torch.tensor([])
    chunk_entities = []

MAX_RESULTS = 1
MAX_CHUNK_LENGTH = sys.maxsize  # Maximum length of each returned chunk

conversation_context = []

def summarize_chunk(chunk):
    if len(chunk) > MAX_CHUNK_LENGTH:
        return textwrap.shorten(chunk, width=MAX_CHUNK_LENGTH, placeholder="...")
    return chunk

def process_response(response):
    # Capitalize the first letter of each sentence
    response = '. '.join(sentence.capitalize() for sentence in response.split('. '))

    # Remove multiple spaces
    response = re.sub(' +', ' ', response)

    # Add a friendly opener
    openers = ["I hope this helps! ", "Here's what I found: ", "Let me share this with you: "]
    response = random.choice(openers) + response

    return response

async def search_text_with_fuzzy(query):
    if chunks:
        results = process.extract(query, chunks, limit=MAX_RESULTS, scorer=fuzz.partial_ratio)
        return [result[0] for result in results if result[1] > 70]
    return []

async def search_text_with_ner(query):
    doc = nlp(query)
    query_entities = set((ent.text.lower(), ent.label_) for ent in doc.ents)
    return [chunk for chunk, entities in zip(chunks, chunk_entities) if query_entities.intersection(entities)][:MAX_RESULTS]

async def search_text_with_bert(query):
    if chunk_embeddings.size(0) > 0:
        query_embedding = model.encode(query, convert_to_tensor=True)
        similarities = util.pytorch_cos_sim(query_embedding, chunk_embeddings)[0]
        top_k = min(MAX_RESULTS, len(chunks))
        top_results = torch.topk(similarities, k=top_k)
        return [chunks[idx] for idx in top_results[1]]
    return []

async def get_response(message):
    global conversation_context

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
            info = ' '.join(summarized_results)

            # Check if this information was already provided
            if info in conversation_context:
                response = "I've mentioned this before, but just to reiterate: " + info
            else:
                response = process_response(info)
                conversation_context.append(info)

            # Limit the context to the last 5 exchanges
            conversation_context = conversation_context[-5:]

            return response
        else:
            return "I'm afraid I don't have any new information about that. Is there something else you'd like to know?"
    else:
        return "I'm here to help! Could you please ask a more specific question or provide more details?"

def send_message(event=None):
    user_message = user_input.get()
    if user_message:
        display_message(user_message, "user")
        user_input.set("")
        asyncio.run(process_user_message(user_message))

async def process_user_message(message):
    global conversation_context
    conversation_context.append(f"User: {message}")
    response = await get_response(message)
    conversation_context.append(f"Bot: {response}")
    display_message(response, "bot")

def display_message(message, sender):
    chat_log_text.config(state=tk.NORMAL)  # Enable editing to insert new messages

    if sender == "user":
        chat_log_text.insert(tk.END, f"User: {message}\n\n", "user")
    else:
        chat_log_text.insert(tk.END, f"Bot: {message}\n\n", "bot")

    chat_log_text.config(state=tk.DISABLED)  # Disable editing to make it read-only
    chat_log_text.yview(tk.END)  # Scroll to the bottom

def add_new_information():
    def save_info():
        title = title_entry.get().strip()
        details = details_text.get("1.0", tk.END).strip()
        if title and details:
            with open('info.txt', 'a', encoding='utf-8') as file:
                file.write(f"\n[SECTION: {title}]\n{details}\n")
            new_window.destroy()
            # Reload the text data and update embeddings
            reload_text_data()

    new_window = CTkToplevel(root)
    new_window.title("Add New Information")
    new_window.geometry("400x400")

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
    global text, chunks, chunk_embeddings, chunk_entities
    with open('info.txt', 'r', encoding='utf-8') as file:
        text = file.read().strip()
    chunks = text.split('[SECTION:')
    chunks = ['[SECTION:' + chunk.strip() for chunk in chunks if chunk.strip()]
    chunk_embeddings = model.encode(chunks, convert_to_tensor=True)
    chunk_entities = [[(ent.text.lower(), ent.label_) for ent in nlp(chunk).ents] for chunk in chunks]

# Set up the GUI
ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

root = ctk.CTk()
root.title("Optimistic Optimizer")
root.geometry("600x600")
root.resizable(False, False)  # Prevent resizing to maintain layout

# Load and set the logo using CTkImage
try:
    logo_image = Image.open('HUITLogo.png')  # Path to your logo image
    logo_image = logo_image.resize((500, 80), Image.LANCZOS)  # Resize using LANCZOS resampling
    logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(500, 80))
except FileNotFoundError:
    logo_photo = None

header_frame = ctk.CTkFrame(root, height=100, bg_color="#780606")
header_frame.pack(fill="x")

if logo_photo:
    logo_label = ctk.CTkLabel(header_frame, image=logo_photo, text="", font=("Helvetica", 16, "bold"))
    logo_label.pack(side="left", pady=10, padx=10)

# In the main part of the code, update the button command
plus_button = ctk.CTkButton(header_frame, text="+", width=30, height=30, command=add_new_information)
plus_button.pack(side="right", padx=10, pady=10)

chat_frame = ctk.CTkFrame(root, width=600, height=500, corner_radius=10)
chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

# Use tkinter Text widget for better scrolling
chat_log_text = tk.Text(chat_frame, wrap=tk.WORD, state=tk.DISABLED, bg="#f5f5f5", fg="#333", font=("Helvetica", 12))
chat_log_text.pack(side="left", fill="both", expand=True)

chat_log_scrollbar = tk.Scrollbar(chat_frame, orient="vertical", command=chat_log_text.yview)
chat_log_scrollbar.pack(side="right", fill="y")

chat_log_text.config(yscrollcommand=chat_log_scrollbar.set)

# Add tags to differentiate between user and bot messages
chat_log_text.tag_config("user", foreground="#0000FF", font=("Helvetica", 12, "bold"))
chat_log_text.tag_config("bot", foreground="#008000", font=("Helvetica", 12))

input_frame = ctk.CTkFrame(root, height=80)
input_frame.pack(pady=10, padx=10, fill="x")

user_input = ctk.StringVar()
entry_box = ctk.CTkEntry(input_frame, textvariable=user_input, width=450, placeholder_text="Type your message here...")
entry_box.pack(side="left", padx=(0, 10), pady=10, fill="x", expand=True)
entry_box.bind("<Return>", send_message)

send_button = ctk.CTkButton(input_frame, text="Send", command=send_message, width=100)
send_button.pack(side="left", pady=10)

root.mainloop()