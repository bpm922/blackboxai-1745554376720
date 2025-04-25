"""
Main script demonstrating the usage of the article scraper and summarizer.
"""
import sys
from pathlib import Path
from typing import List, Optional
import argparse
from loguru import logger

from src.scraper import ArticleScraper
from src.processor import TextProcessor
from src.summarizer import ArticleSummarizer
from src.storage import DataStorage

def setup_logger():
    """Configure logging settings."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <white>{message}</white>",
        level="INFO"
    )
    logger.add(
        "logs/article_scraper.log",
        rotation="500 MB",
        retention="10 days",
        level="DEBUG"
    )

def process_url(url: str,
               storage: DataStorage,
               ratio: float = 0.3,
               word_count: Optional[int] = None) -> bool:
    """
    Process a single URL: scrape, summarize, and store.
    
    Args:
        url: URL to process
        storage: DataStorage instance
        ratio: Summary length ratio
        word_count: Target summary word count
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        # Initialize components
        scraper = ArticleScraper()
        processor = TextProcessor()
        summarizer = ArticleSummarizer()
        
        # Scrape article
        logger.info(f"Scraping article from: {url}")
        article = scraper.scrape(url)
        
        # Clean content
        cleaned_content = processor.clean(article.content)
        article_dict = article.__dict__
        article_dict['content'] = cleaned_content
        
        # Generate summary
        logger.info("Generating summary...")
        summary = summarizer.summarize(
            cleaned_content,
            ratio=ratio,
            word_count=word_count
        )
        
        # Get statistics
        stats = summarizer.get_summary_stats(cleaned_content, summary)
        logger.info(
            f"Summary generated: {stats['compression_ratio']:.1%} of original length "
            f"({stats['summary_length']} words)"
        )
        
        # Store results
        logger.info("Storing results...")
        storage.save_article(article_dict, summary)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to process URL {url}: {str(e)}")
        return False

def process_file(file_path: str,
                storage: DataStorage,
                ratio: float = 0.3,
                word_count: Optional[int] = None) -> tuple:
    """
    Process URLs from a file.
    
    Args:
        file_path: Path to file containing URLs (one per line)
        storage: DataStorage instance
        ratio: Summary length ratio
        word_count: Target summary word count
        
    Returns:
        tuple: (successful_count, failed_count)
    """
    successful = 0
    failed = 0
    
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
            
        total = len(urls)
        logger.info(f"Processing {total} URLs from {file_path}")
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing URL {i}/{total}: {url}")
            if process_url(url, storage, ratio, word_count):
                successful += 1
            else:
                failed += 1
                
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        
    return successful, failed

def main():
    """Main function to run the article scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape and summarize articles from URLs"
    )
    
    # Add arguments
    parser.add_argument(
        '-u', '--url',
        help='URL of the article to scrape'
    )
    parser.add_argument(
        '-f', '--file',
        help='File containing URLs (one per line)'
    )
    parser.add_argument(
        '-r', '--ratio',
        type=float,
        default=0.3,
        help='Summary length as ratio of original text (default: 0.3)'
    )
    parser.add_argument(
        '-w', '--words',
        type=int,
        help='Target summary word count (overrides ratio if specified)'
    )
    parser.add_argument(
        '-o', '--output',
        default='data',
        help='Output directory for stored data (default: data)'
    )
    parser.add_argument(
        '--export',
        choices=['json', 'csv'],
        help='Export format for processed articles'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logger()
    
    # Initialize storage
    storage = DataStorage(args.output)
    
    if args.url:
        # Process single URL
        success = process_url(
            args.url,
            storage,
            ratio=args.ratio,
            word_count=args.words
        )
        if success:
            logger.info("URL processed successfully")
        else:
            logger.error("Failed to process URL")
            
    elif args.file:
        # Process URLs from file
        successful, failed = process_file(
            args.file,
            storage,
            ratio=args.ratio,
            word_count=args.words
        )
        logger.info(
            f"Processing complete: {successful} successful, {failed} failed"
        )
        
    else:
        logger.error("No URL or file specified")
        parser.print_help()
        sys.exit(1)
        
    # Export data if requested
    if args.export:
        try:
            storage.export_data(format=args.export)
            logger.info(f"Data exported in {args.export} format")
        except Exception as e:
            logger.error(f"Failed to export data: {str(e)}")
    
    # Display final statistics
    stats = storage.get_stats()
    logger.info("\nStorage Statistics:")
    logger.info(f"Total articles: {stats['total_articles']}")
    logger.info(f"Articles with summaries: {stats['articles_with_summary']}")
    logger.info(f"Unique authors: {stats['unique_authors']}")
    if stats.get('latest_article'):
        logger.info(f"Latest article: {stats['latest_article']}")

if __name__ == "__main__":
    main()
