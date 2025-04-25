"""
Text processing module for cleaning and analyzing article content.
"""
import re
from typing import List
from collections import Counter
import nltk
from loguru import logger

class TextProcessor:
    """Handles text cleaning and analysis."""
    
    def __init__(self):
        """Initialize the text processor."""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.stopwords = set(nltk.corpus.stopwords.words('english'))
        except Exception as e:
            logger.warning(f"Failed to download NLTK data: {str(e)}")
            self.stopwords = set()

    def clean(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()
        
        # Remove HTML tags
        text = self._remove_html(text)
        
        # Remove extra whitespace
        text = self._normalize_whitespace(text)
        
        # Remove special characters while keeping punctuation
        text = self._remove_special_chars(text)
        
        # Normalize paragraph breaks
        text = self._normalize_paragraphs(text)
        
        return text.strip()

    def _remove_html(self, text: str) -> str:
        """Remove HTML tags and entities."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove HTML entities
        text = re.sub('&nbsp;', ' ', text)
        text = re.sub('&amp;', '&', text)
        text = re.sub('<', '<', text)
        text = re.sub('>', '>', text)
        
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text."""
        return re.sub(r'\s+', ' ', text)

    def _remove_special_chars(self, text: str) -> str:
        """Remove special characters while keeping punctuation."""
        return re.sub(r'[^\w\s.,!?-]', '', text)

    def _normalize_paragraphs(self, text: str) -> str:
        """Normalize paragraph breaks."""
        return re.sub(r'\n\s*\n', '\n\n', text)

    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Split on common sentence endings
        text = text.replace('!', '.')
        text = text.replace('?', '.')
        
        # Split and clean sentences
        sentences = []
        for sentence in text.split('.'):
            sentence = sentence.strip()
            if sentence and len(sentence.split()) > 3:  # Ignore very short segments
                sentences.append(sentence)
        
        return sentences

    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """Extract key words from text using frequency analysis."""
        # Split into words and convert to lowercase
        words = text.lower().split()
        
        # Remove stopwords and non-alphabetic words
        words = [word for word in words 
                if word.isalpha() and word not in self.stopwords]
        
        # Count word frequencies
        word_freq = Counter(words)
        
        # Get most common words
        return [word for word, _ in word_freq.most_common(num_keywords)]

    def get_text_stats(self, text: str) -> dict:
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

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using word overlap."""
        # Get word sets (excluding stopwords)
        words1 = {w.lower() for w in text1.split() 
                 if w.isalpha() and w.lower() not in self.stopwords}
        words2 = {w.lower() for w in text2.split() 
                 if w.isalpha() and w.lower() not in self.stopwords}
        
        # Calculate Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
