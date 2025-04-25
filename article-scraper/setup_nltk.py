"""
Script to download required NLTK data.
"""
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def download_nltk_data():
    """Download required NLTK data packages."""
    required_packages = [
        'punkt',           # For sentence tokenization
        'punkt_tab',       # Additional punkt data
        'stopwords',       # For stopwords removal
        'averaged_perceptron_tagger'  # For POS tagging
    ]
    
    print("Downloading required NLTK packages...")
    for package in required_packages:
        try:
            print(f"Downloading {package}...")
            nltk.download(package, quiet=True)
            print(f"Successfully downloaded {package}")
        except Exception as e:
            print(f"Error downloading {package}: {str(e)}")

if __name__ == "__main__":
    download_nltk_data()
    print("NLTK setup completed!")
