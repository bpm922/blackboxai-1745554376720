"""
Article Scraper and Summarizer CLI
--------------------------------
A command-line tool for scraping, analyzing, and summarizing articles from news websites.

Usage:
    python scraper_cli.py -u URL [URL ...]  # Process one or more URLs
    python scraper_cli.py -f urls.txt       # Process URLs from a file
    python scraper_cli.py --report report.json  # Generate a JSON report
"""
import argparse
import json
from pathlib import Path
from src.enhanced_scraper import EnhancedScraper
from src.text_processor import TextProcessor
from src.text_summarizer import TextSummarizer
from src.storage import DataStorage

class ArticleAnalyzer:
    """Main class for article analysis operations."""
    
    def __init__(self, output_dir="data"):
        """Initialize the article analyzer."""
        self.scraper = EnhancedScraper(
            min_delay=3.0,
            max_delay=5.0,
            max_retries=3
        )
        self.processor = TextProcessor()
        self.summarizer = TextSummarizer()
        self.storage = DataStorage(output_dir)

    def process_article(self, url):
        """Process a single article."""
        print(f"\nProcessing: {url}")
        print("-" * 70)
        
        try:
            # Scrape article
            article = self.scraper.scrape(url)
            
            # Process content
            cleaned_content = self.processor.clean(article.content)
            stats = self.processor.get_text_stats(cleaned_content)
            keywords = self.processor.extract_keywords(cleaned_content, num_keywords=5)
            summary = self.summarizer.summarize(cleaned_content, ratio=0.3)
            summary_stats = self.summarizer.get_summary_stats(cleaned_content, summary)
            
            # Store results
            article_dict = article.__dict__
            article_dict.update({
                'cleaned_content': cleaned_content,
                'keywords': keywords,
                'summary': summary,
                'stats': stats,
                'summary_stats': summary_stats
            })
            
            self.storage.save_article(article_dict, summary)
            self._print_article_summary(article_dict)
            
            return article_dict
            
        except Exception as e:
            print(f"Error processing article: {str(e)}")
            return None

    def process_urls(self, urls):
        """Process multiple URLs."""
        results = []
        for url in urls:
            result = self.process_article(url)
            if result:
                results.append(result)
        return results

    def save_report(self, articles, output_file="report.json"):
        """Save processed articles to a JSON report."""
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        with open(reports_dir / output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)

    def _print_article_summary(self, article):
        """Print a formatted summary of an article."""
        print("\n" + "=" * 70)
        print(f"Title: {article['title']}")
        print(f"Author: {article['author'] or 'Unknown'}")
        print(f"Date: {article['date'] or 'Unknown'}")
        print("-" * 70)
        
        print("Article Statistics:")
        print(f"- Words: {article['stats']['num_words']}")
        print(f"- Sentences: {article['stats']['num_sentences']}")
        print(f"- Reading time: {article['stats']['reading_time']} minutes")
        
        if article['keywords']:
            print("\nKey Topics:")
            print(", ".join(article['keywords']))
        
        print("\nSummary:")
        print("-" * 70)
        print(article['summary'])
        print("-" * 70)
        
        print("Summary Statistics:")
        print(f"- Compression ratio: {article['summary_stats']['compression_ratio']:.1%}")
        print(f"- Original length: {article['summary_stats']['original_length']} words")
        print(f"- Summary length: {article['summary_stats']['summary_length']} words")

def main():
    """Main entry point for the article scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape and analyze articles from news websites"
    )
    
    parser.add_argument(
        '-u', '--urls',
        nargs='+',
        help='One or more URLs to process'
    )
    parser.add_argument(
        '-f', '--file',
        help='File containing URLs (one per line)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        default='data',
        help='Output directory for data files'
    )
    parser.add_argument(
        '--report',
        help='Generate JSON report with given filename'
    )
    
    args = parser.parse_args()
    
    # Get URLs to process
    urls = []
    if args.urls:
        urls.extend(args.urls)
    if args.file:
        try:
            with open(args.file) as f:
                urls.extend(line.strip() for line in f if line.strip())
        except Exception as e:
            print(f"Error reading URL file: {str(e)}")
            return
    
    if not urls:
        # Default URLs if none provided
        urls = [
            "https://www.strategicstudyindia.com/2025/04/how-uk-deal-on-diego-garcia-could.html",
            "https://www.strategicstudyindia.com/2025/04/se-asia-keeps-peace-50-years-after.html"
        ]
        print("No URLs provided. Using default examples...")
    
    # Process articles
    analyzer = ArticleAnalyzer(args.output_dir)
    results = analyzer.process_urls(urls)
    
    # Generate report if requested
    if args.report:
        analyzer.save_report(results, args.report)
        print(f"\nReport saved to: reports/{args.report}")
    
    # Display final statistics
    stats = analyzer.storage.get_stats()
    print("\nProcessing Complete")
    print("=" * 70)
    print(f"Articles processed: {len(results)}")
    print(f"Total articles in storage: {stats['total_articles']}")
    print(f"Articles with summaries: {stats['articles_with_summary']}")

if __name__ == "__main__":
    main()
