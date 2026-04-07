"""
Setup script to download required NLTK data
"""
import nltk

print("Downloading NLTK data...")

# Download required datasets
datasets = [
    'punkt',
    'stopwords',
    'wordnet',
    'omw-1.4',
    'averaged_perceptron_tagger'
]

for dataset in datasets:
    try:
        nltk.download(dataset, quiet=False)
        print(f"✓ Downloaded {dataset}")
    except Exception as e:
        print(f"✗ Error downloading {dataset}: {e}")

print("\nNLTK data download complete!")
