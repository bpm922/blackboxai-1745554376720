"""
Demonstration of the article scraper with defense and strategic news articles.
"""
from src.scraper import ArticleScraper
from src.processor import TextProcessor
from src.summarizer import ArticleSummarizer
from src.storage import DataStorage

def process_article(url, scraper, processor, summarizer, storage):
    """Process a single article."""
    print(f"\nProcessing article from: {url}")
    print("-" * 70)
    
    try:
        # Scrape article
        print("\n1. Scraping article...")
        article = scraper.scrape(url)
        print(f"Title: {article.title}")
        print(f"Author: {article.author or 'Unknown'}")
        print(f"Date: {article.date or 'Unknown'}")
        
        # Clean content
        print("\n2. Processing content...")
        cleaned_content = processor.clean(article.content)
        
        # Get text statistics
        stats = processor.get_text_stats(cleaned_content)
        print("\nArticle Statistics:")
        print(f"- Words: {stats['num_words']}")
        print(f"- Sentences: {stats['num_sentences']}")
        print(f"- Reading time: {stats['reading_time']} minutes")
        
        # Generate summary
        print("\n3. Generating summary...")
        summary = summarizer.summarize(cleaned_content, ratio=0.3)
        
        # Get summary statistics
        summary_stats = summarizer.get_summary_stats(cleaned_content, summary)
        print("\nSummary Statistics:")
        print(f"- Original length: {summary_stats['original_length']} words")
        print(f"- Summary length: {summary_stats['summary_length']} words")
        print(f"- Compression ratio: {summary_stats['compression_ratio']:.1%}")
        
        print("\nGenerated Summary:")
        print("-" * 70)
        print(summary)
        print("-" * 70)
        
        # Store results
        print("\n4. Storing results...")
        article_dict = article.__dict__
        article_dict['content'] = cleaned_content
        storage.save_article(article_dict, summary)
        print("Results stored successfully")
        
    except Exception as e:
        print(f"\nError processing article: {str(e)}")

def main():
    """Run article scraping and summarization demo."""
    # Example URLs from defense and strategic news websites
    urls = [
        "https://idrw.org/india-to-get-first-rafale-maritime-fighter-jet-in-2026/",
        "https://www.strategicstudyindia.com/2024/04/indias-defence-exports-cross-rs-21000.html"
    ]
    
    # Initialize components with careful rate limiting
    scraper = ArticleScraper(
        min_delay=3.0,  # Increased delay between requests
        max_delay=5.0,
        max_retries=3
    )
    processor = TextProcessor()
    summarizer = ArticleSummarizer()
    storage = DataStorage()
    
    print("Defense News Article Scraper Demo")
    print("=" * 70)
    
    # Process each article
    for url in urls:
        process_article(url, scraper, processor, summarizer, storage)
    
    # Display final storage statistics
    stats = storage.get_stats()
    print("\nFinal Storage Statistics:")
    print(f"Total articles: {stats['total_articles']}")
    print(f"Articles with summaries: {stats['articles_with_summary']}")
    print(f"Latest article: {stats.get('latest_article', 'None')}")

if __name__ == "__main__":
    main()
