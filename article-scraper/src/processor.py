"""
Text processing module for cleaning and preprocessing article content.
"""
import re
from typing import List, Optional
import nltk
from loguru import logger

class TextProcessor:
    """Handles text cleaning and preprocessing operations."""
    
    def __init__(self):
        """Initialize the text processor and download required NLTK data."""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.stopwords = set(nltk.corpus.stopwords.words('english'))
        except Exception as e:
            logger.warning(f"Failed to download NLTK data: {str(e)}")
            self.stopwords = set()

    def clean(self, text: str) -> str:
        """
        Clean and preprocess the input text.
        
        Args:
            text: Raw text content to clean
            
        Returns:
            str: Cleaned and preprocessed text
        """
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()
        
        # Remove HTML tags
        text = self._remove_html(text)
        
        # Remove extra whitespace
        text = self._normalize_whitespace(text)
        
        # Remove special characters
        text = self._remove_special_chars(text)
        
        # Remove extra newlines while preserving paragraph structure
        text = self._normalize_paragraphs(text)
        
        return text.strip()

    def _remove_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        # Remove HTML tags
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', text)
        
        # Remove HTML entities
        text = re.sub('&nbsp;', ' ', text)
        text = re.sub('&amp;', '&', text)
        text = re.sub('<', '<', text)
        text = re.sub('>', '>', text)
        
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text."""
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        return text

    def _remove_special_chars(self, text: str) -> str:
        """Remove special characters while preserving meaningful punctuation."""
        # Keep meaningful punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text

    def _normalize_paragraphs(self, text: str) -> str:
        """Normalize paragraph breaks in text."""
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text

    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Text to split into sentences
            
        Returns:
            List[str]: List of sentences
        """
        # Simple sentence splitting based on common sentence endings
        sentences = []
        current = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                if current:
                    sentences.append(' '.join(current))
                    current = []
                continue
                
            words = line.split()
            for word in words:
                current.append(word)
                if word.endswith(('.', '!', '?')):
                    sentences.append(' '.join(current))
                    current = []
                    
        if current:
            sentences.append(' '.join(current))
            
        return [s.strip() for s in sentences if s.strip()]

    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """
        Extract key words from the text using frequency analysis.
        
        Args:
            text: Text to extract keywords from
            num_keywords: Number of keywords to extract
            
        Returns:
            List[str]: List of extracted keywords
        """
        # Tokenize text
        words = nltk.word_tokenize(text.lower())
        
        # Remove stopwords and non-alphabetic tokens
        words = [word for word in words 
                if word.isalpha() and word not in self.stopwords]
        
        # Calculate word frequencies
        freq_dist = nltk.FreqDist(words)
        
        # Get most common words
        keywords = [word for word, _ in freq_dist.most_common(num_keywords)]
        
        return keywords

    def get_reading_time(self, text: str, wpm: int = 200) -> int:
        """
        Calculate estimated reading time in minutes.
        
        Args:
            text: Text to calculate reading time for
            wpm: Words per minute reading speed (default: 200)
            
        Returns:
            int: Estimated reading time in minutes
        """
        words = len(text.split())
        minutes = round(words / wpm)
        return max(1, minutes)  # Return at least 1 minute

    def get_text_stats(self, text: str) -> dict:
        """
        Get various statistics about the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            dict: Dictionary containing text statistics
        """
        sentences = self.split_into_sentences(text)
        words = nltk.word_tokenize(text)
        
        stats = {
            'num_sentences': len(sentences),
            'num_words': len(words),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'reading_time': self.get_reading_time(text),
        }
        
        return stats
