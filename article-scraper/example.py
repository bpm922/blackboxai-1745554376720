"""
Example script demonstrating the usage of the article scraper.
"""
from src.scraper import ArticleScraper
from src.processor import TextProcessor
from src.summarizer import ArticleSummarizer
from src.storage import DataStorage

def main():
    """Run example article scraping and summarization."""
    # Sample URLs (these are example URLs, replace with actual article URLs)
    urls = [
        "https://example.com/article1",
        "https://example.com/article2"
    ]
    
    # Initialize components
    scraper = ArticleScraper()
    processor = TextProcessor()
    summarizer = ArticleSummarizer()
    storage = DataStorage()
    
    print("Article Scraper Example\n")
    
    for url in urls:
        try:
            print(f"\nProcessing: {url}")
            print("-" * 50)
            
            # Scrape article
            article = scraper.scrape(url)
            print(f"Title: {article.title}")
            print(f"Author: {article.author or 'Unknown'}")
            print(f"Date: {article.date or 'Unknown'}")
            
            # Clean content
            cleaned_content = processor.clean(article.content)
            
            # Get text statistics
            stats = processor.get_text_stats(cleaned_content)
            print(f"\nArticle Statistics:")
            print(f"- Words: {stats['num_words']}")
            print(f"- Sentences: {stats['num_sentences']}")
            print(f"- Reading time: {stats['reading_time']} minutes")
            
            # Generate summary
            summary = summarizer.summarize(cleaned_content, ratio=0.3)
            
            # Get summary statistics
            summary_stats = summarizer.get_summary_stats(cleaned_content, summary)
            print(f"\nSummary Statistics:")
            print(f"- Original length: {summary_stats['original_length']} words")
            print(f"- Summary length: {summary_stats['summary_length']} words")
            print(f"- Compression ratio: {summary_stats['compression_ratio']:.1%}")
            
            # Store results
            article_dict = article.__dict__
            article_dict['content'] = cleaned_content
            storage.save_article(article_dict, summary)
            
            print("\nSummary:")
            print("-" * 50)
            print(summary)
            print("-" * 50)
            
        except Exception as e:
            print(f"\nError processing {url}: {str(e)}")
            continue
    
    # Display storage statistics
    stats = storage.get_stats()
    print("\nStorage Statistics:")
    print(f"Total articles: {stats['total_articles']}")
    print(f"Articles with summaries: {stats['articles_with_summary']}")
    print(f"Unique authors: {stats['unique_authors']}")
    
    # Export data
    try:
        storage.export_data(format='json')
        print("\nData exported to JSON format in the data directory")
    except Exception as e:
        print(f"\nError exporting data: {str(e)}")

if __name__ == "__main__":
    main()
