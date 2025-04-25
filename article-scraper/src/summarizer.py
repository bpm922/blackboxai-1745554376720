"""
Text summarization module using extractive summarization techniques.
"""
from typing import List, Dict
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from loguru import logger
from .processor import TextProcessor

class TextSummarizer:
    """Handles article summarization using extractive methods."""
    
    def __init__(self):
        """Initialize the summarizer."""
        self.processor = TextProcessor()
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def summarize(self, 
                 text: str, 
                 ratio: float = 0.3,
                 min_sentences: int = 3) -> str:
        """
        Generate a summary of the input text.
        
        Args:
            text: Text to summarize
            ratio: Summary length as proportion of original text (0.0 to 1.0)
            min_sentences: Minimum number of sentences in summary
            
        Returns:
            str: Generated summary
        """
        if not text:
            return ""

        # Clean the text
        cleaned_text = self.processor.clean(text)
        
        # Split into sentences
        sentences = self.processor.split_into_sentences(cleaned_text)
        if not sentences:
            return ""
            
        # Score sentences
        scored_sentences = self._score_sentences(sentences)
        
        # Determine number of sentences for summary
        num_sentences = max(
            min_sentences,
            round(len(sentences) * ratio)
        )
        num_sentences = min(num_sentences, len(sentences))
        
        # Select top sentences while preserving order
        selected_indices = sorted([
            i for i, _ in sorted(
                enumerate(scored_sentences),
                key=lambda x: x[1],
                reverse=True
            )[:num_sentences]
        ])
        
        # Combine sentences into summary
        summary = '. '.join(sentences[i] for i in selected_indices)
        
        return summary + ('.' if not summary.endswith('.') else '')

    def _score_sentences(self, sentences: List[str]) -> List[float]:
        """Score sentences based on various features."""
        scores = []
        
        # Get word frequencies across all sentences
        all_words = ' '.join(sentences).lower().split()
        word_freq = Counter(all_words)
        
        # Calculate TF-IDF matrix
        try:
            tfidf_matrix = self.vectorizer.fit_transform(sentences)
            sentence_importance = tfidf_matrix.sum(axis=1).A1
        except:
            # Fallback to simple word frequency if TF-IDF fails
            sentence_importance = [1.0] * len(sentences)
        
        # Score each sentence
        for i, sentence in enumerate(sentences):
            score = 0.0
            
            # TF-IDF based importance
            score += sentence_importance[i] * 0.4
            
            # Word frequency score
            words = sentence.lower().split()
            word_score = sum(word_freq[word] for word in words) / len(words) if words else 0
            score += word_score * 0.3
            
            # Position score - prefer sentences at start/end
            if i < len(sentences) * 0.2:
                score += 0.2  # Boost early sentences
            elif i > len(sentences) * 0.8:
                score += 0.1  # Boost late sentences
            
            scores.append(score)
        
        return scores

    def get_summary_stats(self, original_text: str, summary: str) -> Dict:
        """
        Calculate statistics comparing the summary to the original text.
        
        Args:
            original_text: Original text
            summary: Generated summary
            
        Returns:
            dict: Dictionary containing summary statistics
        """
        original_stats = self.processor.get_text_stats(original_text)
        summary_stats = self.processor.get_text_stats(summary)
        
        compression_ratio = (
            summary_stats['num_words'] / original_stats['num_words']
            if original_stats['num_words'] > 0 else 0
        )
        
        return {
            'original_length': original_stats['num_words'],
            'summary_length': summary_stats['num_words'],
            'compression_ratio': compression_ratio,
            'original_reading_time': original_stats['reading_time'],
            'summary_reading_time': summary_stats['reading_time']
        }

    def compare_summaries(self, summary1: str, summary2: str) -> float:
        """Calculate similarity between two summaries."""
        return self.processor.calculate_similarity(summary1, summary2)
