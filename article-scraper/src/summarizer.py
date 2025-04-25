"""
Article summarization module using various summarization techniques.
"""
from typing import List, Optional, Tuple
from nltk.corpus import stopwords
from collections import Counter
from loguru import logger
from .processor import TextProcessor

class ArticleSummarizer:
    """Handles article summarization using different methods."""
    
    def __init__(self):
        """Initialize the summarizer with text processor."""
        self.processor = TextProcessor()

    def summarize(self, 
                 text: str, 
                 ratio: float = 0.3, 
                 word_count: Optional[int] = None,
                 method: str = 'gensim') -> str:
        """
        Generate a summary of the input text.
        
        Args:
            text: Text to summarize
            ratio: Summary length as a proportion of original text (0.0 to 1.0)
            word_count: Target summary word count (overrides ratio if provided)
            method: Summarization method to use ('gensim' or 'extractive')
            
        Returns:
            str: Generated summary
            
        Raises:
            ValueError: If text is too short or invalid parameters
        """
        if not text:
            raise ValueError("Empty text provided for summarization")

        # Clean the text first
        cleaned_text = self.processor.clean(text)
        
        try:
            if method == 'gensim':
                return self._gensim_summarize(cleaned_text, ratio, word_count)
            elif method == 'extractive':
                return self._extractive_summarize(cleaned_text, ratio, word_count)
            else:
                raise ValueError(f"Unknown summarization method: {method}")
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            # Fallback to simple extractive summarization
            return self._fallback_summarize(cleaned_text, ratio)

    def _calculate_word_freq(self, text: str) -> Counter:
        """Calculate word frequencies in the text."""
        # Split into words and convert to lowercase
        words = text.lower().split()
        # Remove stopwords and punctuation
        stop_words = set(stopwords.words('english'))
        words = [word for word in words if word.isalnum() and word not in stop_words]
        return Counter(words)

    def _score_sentence(self, sentence: str, word_freq: Counter) -> float:
        """Score a sentence based on word frequencies."""
        words = sentence.lower().split()
        score = sum(word_freq[word] for word in words if word.isalnum())
        return score / len(words) if words else 0

    def _gensim_summarize(self, 
                         text: str, 
                         ratio: float, 
                         word_count: Optional[int]) -> str:
        """
        Summarize text using frequency-based extractive summarization.
        
        Args:
            text: Text to summarize
            ratio: Summary length ratio
            word_count: Target word count
            
        Returns:
            str: Generated summary
        """
        try:
            # Split text into sentences using processor
            sentences = self.processor.split_into_sentences(text)
            if not sentences:
                return ""

            # Calculate word frequencies
            word_freq = self._calculate_word_freq(text)
            
            # Score sentences
            scored_sentences = [
                (sentence, self._score_sentence(sentence, word_freq))
                for sentence in sentences
            ]
            
            # Sort sentences by score
            scored_sentences.sort(key=lambda x: x[1], reverse=True)
            
            # Determine number of sentences for summary
            if word_count:
                avg_words_per_sentence = len(text.split()) / len(sentences)
                num_sentences = min(
                    len(sentences),
                    round(word_count / avg_words_per_sentence)
                )
            else:
                num_sentences = max(1, round(len(sentences) * ratio))
            
            # Select top sentences while preserving order
            selected_indices = sorted([
                sentences.index(sentence)
                for sentence, _ in scored_sentences[:num_sentences]
            ])
            
            summary = ' '.join(sentences[i] for i in selected_indices)
            return summary if summary else self._fallback_summarize(text, ratio)
            
        except Exception as e:
            logger.warning(f"Summarization failed: {str(e)}")
            return self._fallback_summarize(text, ratio)

    def _extractive_summarize(self, 
                            text: str, 
                            ratio: float, 
                            word_count: Optional[int]) -> str:
        """
        Perform extractive summarization using sentence scoring.
        
        Args:
            text: Text to summarize
            ratio: Summary length ratio
            word_count: Target word count
            
        Returns:
            str: Generated summary
        """
        # Split into sentences
        sentences = self.processor.split_into_sentences(text)
        
        if not sentences:
            return ""

        # Score sentences
        scored_sentences = self._score_sentences(sentences)
        
        # Determine how many sentences to include
        if word_count:
            words_per_sentence = sum(len(s.split()) for s in sentences) / len(sentences)
            num_sentences = min(
                len(sentences),
                round(word_count / words_per_sentence)
            )
        else:
            num_sentences = max(1, round(len(sentences) * ratio))

        # Select top sentences while preserving order
        selected_sentences = self._select_sentences(
            sentences, scored_sentences, num_sentences
        )
        
        return ' '.join(selected_sentences)

    def _score_sentences(self, sentences: List[str]) -> List[Tuple[int, float]]:
        """
        Score sentences based on various heuristics.
        
        Args:
            sentences: List of sentences to score
            
        Returns:
            List[Tuple[int, float]]: List of (sentence_index, score) tuples
        """
        scores = []
        for i, sentence in enumerate(sentences):
            score = 0.0
            
            # Length score - prefer medium-length sentences
            words = len(sentence.split())
            if 5 <= words <= 25:
                score += 0.3
                
            # Position score - prefer sentences at start/end of text
            if i < len(sentences) * 0.2 or i > len(sentences) * 0.8:
                score += 0.3
                
            # Keyword score - prefer sentences with important keywords
            keywords = self.processor.extract_keywords(sentence)
            score += len(keywords) * 0.1
            
            scores.append((i, score))
            
        return scores

    def _select_sentences(self, 
                         sentences: List[str], 
                         scored_sentences: List[Tuple[int, float]], 
                         num_sentences: int) -> List[str]:
        """
        Select top-scoring sentences while preserving original order.
        
        Args:
            sentences: Original list of sentences
            scored_sentences: List of (sentence_index, score) tuples
            num_sentences: Number of sentences to select
            
        Returns:
            List[str]: Selected sentences in original order
        """
        # Sort by score and select top indices
        selected_indices = sorted(
            [i for i, _ in sorted(scored_sentences, 
                                key=lambda x: x[1], 
                                reverse=True)[:num_sentences]]
        )
        
        # Return sentences in original order
        return [sentences[i] for i in selected_indices]

    def _fallback_summarize(self, text: str, ratio: float) -> str:
        """
        Simple fallback summarization method.
        
        Args:
            text: Text to summarize
            ratio: Summary length ratio
            
        Returns:
            str: Generated summary
        """
        sentences = self.processor.split_into_sentences(text)
        if not sentences:
            return ""
            
        num_sentences = max(1, round(len(sentences) * ratio))
        return ' '.join(sentences[:num_sentences])

    def get_summary_stats(self, original_text: str, summary: str) -> dict:
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
