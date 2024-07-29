import subprocess
import sys

def download_spacy_model():
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])

if __name__ == "__main__":
    download_spacy_model()
