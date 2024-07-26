from setuptools import setup

APP = ['OptimisticOptimizer.py']  # Replace 'your_script.py' with the name of your main Python script
DATA_FILES = ['info.txt', 'HUITLogo.png']  # Add other files if needed
OPTIONS = {
    'argv_emulation': True,
    'packages': ['spacy', 'sentence_transformers', 'torch', 'rapidfuzz', 'textwrap', 'PIL', 'random', 're', 'tkinter', 'customtkinter'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
