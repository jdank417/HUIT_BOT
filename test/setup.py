# main.py
import subprocess
import sys
import os

def download_spacy_model():
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])

# Call the function if the model is not found
model_name = "en_core_web_sm"
try:
    import spacy
    spacy.load(model_name)
except OSError:
    download_spacy_model()
    spacy.load(model_name)

# Your main application code here
def main():
    print("Your main application code here.")

if __name__ == "__main__":
    main()
