"""
Live demonstration of the article scraper with a real news article.
"""
from src.scraper import ArticleScraper
from src.processor import TextProcessor
from src.summarizer import ArticleSummarizer
from src.storage import DataStorage

def main():
    """Run article scraping and summarization demo."""
    # Using a technology news article from The Verge
    url = "https://www.theverge.com/2024/4/25/24134521/ai-regulation-european-union-parliament-vote"
    
    # Initialize components with careful rate limiting
    scraper = ArticleScraper(
        min_delay=2.0,  # Increase delay between requests
        max_delay=4.0,
        max_retries=3
    )
    processor = TextProcessor()
    summarizer = ArticleSummarizer()
    storage = DataStorage()
    
    print(f"\nProcessing article from: {url}")
    print("-" * 50)
    
    try:
        # Scrape article
        print("\n1. Scraping article...")
        article = scraper.scrape(url)
        print(f"Title: {article.title}")
        print(f"Author: {article.author or 'Unknown'}")
        print(f"Date: {article.date or 'Unknown'}")
        
        # Clean content
        print("\n2. Processing content...")
