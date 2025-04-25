"""
Simple text processing module that doesn't rely on complex NLTK features.
"""
import re
from typing import List, Dict
from collections import Counter

class TextProcessor:
    """Handles text cleaning and preprocessing operations."""
    
    def __init__(self):
        """Initialize the text processor with basic stopwords."""
        self.stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with'
        }

    def clean(self, text: str) -> str:
        """Clean and preprocess the input text."""
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove HTML entities
        text = re.sub('&nbsp;', ' ', text)
        text = re.sub('&amp;', '&', text)
        text = re.sub('<', '<', text)
        text = re.sub('>', '>', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters while keeping punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text.strip()

    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using simple rules."""
        # Split on common sentence endings
        text = text.replace('!', '.')
        text = text.replace('?', '.')
        
        # Split on periods and filter empty sentences
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        return sentences

    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """Extract key words from the text using frequency analysis."""
        # Split into words and convert to lowercase
        words = text.lower().split()
        
        # Remove stopwords and non-alphabetic words
        words = [word for word in words 
                if word.isalpha() and word not in self.stopwords]
        
        # Count word frequencies
        word_counts = Counter(words)
        
        # Get most common words
        return [word for word, _ in word_counts.most_common(num_keywords)]

    def get_text_stats(self, text: str) -> Dict:
        """Get statistics about the text."""
        sentences = self.split_into_sentences(text)
        words = text.split()
        
        # Calculate reading time (assuming 200 words per minute)
        reading_time = max(1, round(len(words) / 200))
        
        return {
            'num_sentences': len(sentences),
            'num_words': len(words),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'reading_time': reading_time
        }
