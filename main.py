import sys
import spacy
from sentence_transformers import SentenceTransformer, util
import torch
from rapidfuzz import fuzz, process
import asyncio
import textwrap
import customtkinter as ctk
from PIL import Image, ImageTk  # Correct import for resizing

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
    return [chunk for chunk, entities in zip(chunks, chunk_entities) if query_entities.intersection(entities)][
           :MAX_RESULTS]


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


def send_message(event=None):
    user_message = user_input.get()
    if user_message:
        display_message(user_message, "user")
        user_input.set("")
        asyncio.run(process_user_message(user_message))


async def process_user_message(message):
    response = await get_response(message)
    display_message(response, "bot")


def display_message(message, sender):
    bubble_frame = ctk.CTkFrame(chat_log_frame, corner_radius=10, fg_color="#DDDDDD" if sender == "bot" else "#780606")
    bubble_label = ctk.CTkLabel(bubble_frame, text=message, wraplength=400, justify="left", anchor="w",
                                text_color="black" if sender == "bot" else "white")
    bubble_label.pack(padx=5, pady=5, fill="both", expand=True)

    # Determine where to pack the bubble_frame
    if sender == "user":
        bubble_frame.pack(anchor="e", padx=5, pady=5, fill="x", expand=True)
    else:
        bubble_frame.pack(anchor="w", padx=5, pady=5, fill="x", expand=True)

    chat_log_frame.update_idletasks()  # Update layout after packing
    chat_log_canvas.yview_moveto(1.0)  # Scroll to the bottom


# Set up the GUI
ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

root = ctk.CTk()
root.title("ChatBot")
root.geometry("600x600")

# Load and set the logo
logo_image = Image.open('HUITLogo.png')  # Path to your logo image
logo_image = logo_image.resize((500, 80), Image.LANCZOS)  # Resize using LANCZOS resampling
logo_photo = ImageTk.PhotoImage(logo_image)

header_frame = ctk.CTkFrame(root, height=100, bg_color="#780606")
header_frame.pack(fill="x")

logo_label = ctk.CTkLabel(header_frame, image=logo_photo, text="")
logo_label.pack(pady=10)

chat_frame = ctk.CTkFrame(root, width=600, height=500)
chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

chat_log_canvas = ctk.CTkCanvas(chat_frame)
chat_log_canvas.pack(side="left", fill="both", expand=True)

chat_log_scrollbar = ctk.CTkScrollbar(chat_frame, orientation="vertical", command=chat_log_canvas.yview)
chat_log_scrollbar.pack(side="right", fill="y")

chat_log_frame = ctk.CTkFrame(chat_log_canvas)
chat_log_canvas.create_window((0, 0), window=chat_log_frame, anchor="nw")
chat_log_frame.bind("<Configure>", lambda e: chat_log_canvas.configure(scrollregion=chat_log_canvas.bbox("all")))

input_frame = ctk.CTkFrame(root)
input_frame.pack(pady=10, padx=10, fill="x")

user_input = ctk.StringVar()
entry_box = ctk.CTkEntry(input_frame, textvariable=user_input, width=450)
entry_box.pack(side="left", padx=(0, 10), pady=10, fill="x", expand=True)
entry_box.bind("<Return>", send_message)

send_button = ctk.CTkButton(input_frame, text="Send", command=send_message)
send_button.pack(side="left", pady=10)

root.mainloop()
