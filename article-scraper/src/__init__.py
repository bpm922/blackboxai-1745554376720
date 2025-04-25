"""
Defense News Analyzer package.
"""
from .news_scraper import DefenseNewsScraper
from .processor import TextProcessor
from .summarizer import TextSummarizer

__all__ = ["DefenseNewsScraper", "TextProcessor", "TextSummarizer"]
