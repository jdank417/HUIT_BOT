import tkinter as tk
from tkinter import scrolledtext, PhotoImage
import tkinter.font as tkFont
import google.generativeai as genai
import os
import threading

# ----------------------------------------------------------------
#  CONFIG / LOADING
# ----------------------------------------------------------------

genai.configure(api_key="AIzaSyDFR1QyWkrFkMKMHj-pL_vv8qUIJyJhNqE")
model_name = "gemini-1.5-flash"

script_dir = os.path.dirname(os.path.abspath(__file__))
info_file_path = os.path.join(script_dir, "info.txt")

with open(info_file_path, "r", encoding="utf-8") as file:
    knowledge_base = file.read()

# ----------------------------------------------------------------
#  LOGIC
# ----------------------------------------------------------------

def display_message(message, sender):
    """Appends a message in the chat window with distinct styling."""
    chat_box.config(state=tk.NORMAL)

    if sender == "User":
        tag = "user"
        prefix = "User: "
    else:
        tag = "assistant"
        prefix = "Assistant: "

    chat_box.insert(tk.END, prefix + message + "\n\n", (tag,))
    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)  # Auto-scroll

def process_user_message(message):
    """Generate a response from Gemini using the preloaded knowledge base."""
    prompt = (
        f"Here is some prior information:\n{knowledge_base}\n\n"
        f"User: {message}\nAssistant:"
    )
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        generated_text = response.text.strip()
    except Exception as e:
        generated_text = "I couldn’t find an answer based on the information provided."
        print("Error:", e)

    display_message(generated_text, "Assistant")

def send_message(*args):
    """Handle sending the user's message (start a background thread)."""
    user_message = user_input.get().strip()
    if not user_message:
        return

    display_message(user_message, "User")
    user_input.delete(0, tk.END)

    thread = threading.Thread(target=process_user_message, args=(user_message,))
    thread.start()

# ----------------------------------------------------------------
#  GUI SETUP
# ----------------------------------------------------------------

root = tk.Tk()
root.title("Knowledge Assistant (Powered by Gemini)")

# Use a larger default window size
root.geometry("900x700")

# Main background in light gray
root.configure(bg="#636363")

# Harvard Crimson color
HARVARD_CRIMSON = "#A51C30"

# 1. HEADER FRAME (Crimson background)
header_frame = tk.Frame(root, bg="#636363")
header_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)

# Logo (if it exists)
logo_image_path = os.path.join(script_dir, "HUITLogo.png")
if os.path.exists(logo_image_path):
    logo_img = PhotoImage(file=logo_image_path)
    logo_label = tk.Label(header_frame, image=logo_img, bg="#636363")
    logo_label.pack(side=tk.LEFT, padx=(0, 10))


#CHAT FRAME (middle)
chat_frame = tk.Frame(root, bg="#636363")
chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

# Larger font for conversation
chat_font = tkFont.Font(family="Helvetica", size=16)

chat_box = scrolledtext.ScrolledText(
    chat_frame,
    wrap=tk.WORD,
    font=chat_font,
    bg="#FFFFFF",        # White for chat background
    fg="#000000",        # Black text for good readability
    bd=0,
    padx=15,
    pady=15,
    highlightthickness=0
)
chat_box.pack(fill=tk.BOTH, expand=True)
chat_box.config(state=tk.DISABLED)

# Define color tags for user and assistant
chat_box.tag_config("user", foreground=HARVARD_CRIMSON, font=("Helvetica", 16, "bold"))
chat_box.tag_config("assistant", foreground="#000000", font=("Helvetica", 16))

# 3. INPUT FRAME (bottom)
input_frame = tk.Frame(root, bg="#636363")
input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)

# Larger font for the user input
user_input = tk.Entry(
    input_frame,
    font=("Helvetica", 16),
    bg="#FFFFFF",
    fg="#000000",
    bd=1,
    relief="flat"
)
user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
user_input.bind("<Return>", send_message)

# Send button in Crimson with white text
send_button = tk.Button(
    input_frame,
    text="Send",
    command=send_message,
    bg=HARVARD_CRIMSON,
    fg="#636363",
    activebackground="#7F1523",  # Slightly darker for active state
    activeforeground="#636363",
    font=("Helvetica", 14, "bold"),
    bd=0,
    padx=20,
    pady=8
)
send_button.pack(side=tk.RIGHT)

# Give focus to the input field
user_input.focus_set()

root.mainloop()
