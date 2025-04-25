"""
Defense News Analyzer
--------------------
Main script for scraping and analyzing defense news articles.
"""
import os
from datetime import datetime
from pathlib import Path
import json
from typing import List, Dict
from collections import defaultdict
import numpy as np
from loguru import logger
from src.news_scraper import DefenseNewsScraper
from src.processor import TextProcessor
from src.summarizer import TextSummarizer

class DefenseNewsAnalyzer:
    """Main class for analyzing defense news articles."""
    
    def __init__(self, base_dir: str = "analysis"):
        """Initialize the analyzer with storage directories."""
        self.base_dir = Path(base_dir)
        self.articles_dir = self.base_dir / "articles"
        self.analysis_dir = self.base_dir / "analysis"
        self.comparison_dir = self.base_dir / "comparison"
        
        # Create directories
        for directory in [self.articles_dir, self.analysis_dir, self.comparison_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.scraper = DefenseNewsScraper()
        self.processor = TextProcessor()
        self.summarizer = TextSummarizer()
        
        # Configure logging
        logger.add(
            self.base_dir / "analyzer.log",
            rotation="500 MB",
            level="INFO"
        )

    def process_website(self, website: str, num_articles: int = 10) -> List[Dict]:
        """Process articles from a website."""
        logger.info(f"Processing articles from: {website}")
        
        # Create website-specific directory
        site_name = website.split("//")[1].split("/")[0]
        site_dir = self.articles_dir / site_name
        site_dir.mkdir(exist_ok=True)
        
        # Get recent articles
        articles = self.scraper.get_recent_articles(website, num_articles)
        processed_articles = []
        
        for i, article in enumerate(articles, 1):
            try:
                logger.info(f"Processing article {i}/{len(articles)}: {article['title']}")
                
                # Scrape and process article
                scraped = self.scraper.scrape_article(article['url'])
                cleaned_content = self.processor.clean(scraped.content)
                summary = self.summarizer.summarize(cleaned_content)
                keywords = self.processor.extract_keywords(cleaned_content)
                
                # Save article data
                article_data = {
                    "url": article['url'],
                    "title": scraped.title,
                    "author": scraped.author,
                    "date": scraped.date,
                    "content": cleaned_content,
                    "summary": summary,
                    "keywords": keywords
                }
                
                # Save to file
                filename = f"article_{i}_{datetime.now().strftime('%Y%m%d')}.json"
                with open(site_dir / filename, 'w', encoding='utf-8') as f:
                    json.dump(article_data, f, indent=2, ensure_ascii=False)
                
                processed_articles.append(article_data)
                logger.success(f"Successfully processed article: {article['title']}")
                
            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
        
        return processed_articles

    def analyze_articles(self, articles: List[Dict]) -> Dict:
        """Analyze a collection of articles."""
        if not articles:
            return {}
            
        # Collect statistics
        stats = {
            "total_articles": len(articles),
            "avg_length": np.mean([len(a["content"].split()) for a in articles]),
            "avg_summary_length": np.mean([len(a["summary"].split()) for a in articles]),
            "common_keywords": self._get_common_keywords(articles)
        }
        
        return stats

    def compare_articles(self, articles: List[Dict]) -> Dict:
        """Compare articles and find similarities."""
        if not articles:
            return {}
            
        # Find similar articles
        similar_pairs = []
        for i, article1 in enumerate(articles):
            for j, article2 in enumerate(articles[i+1:], i+1):
                similarity = self.processor.calculate_similarity(
                    article1["content"],
                    article2["content"]
                )
                if similarity > 0.3:  # Similarity threshold
                    similar_pairs.append({
                        "article1": article1["title"],
                        "article2": article2["title"],
                        "similarity": similarity
                    })
        
        # Get common themes
        all_keywords = [kw for a in articles for kw in a["keywords"]]
        keyword_freq = defaultdict(int)
        for kw in all_keywords:
            keyword_freq[kw] += 1
        
        common_themes = sorted(
            [(k, v) for k, v in keyword_freq.items() if v > 1],
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "similar_pairs": similar_pairs,
            "common_themes": common_themes
        }

    def _get_common_keywords(self, articles: List[Dict]) -> List[tuple]:
        """Get common keywords across articles."""
        keyword_freq = defaultdict(int)
        for article in articles:
            for keyword in article["keywords"]:
                keyword_freq[keyword] += 1
        
        return sorted(
            [(k, v) for k, v in keyword_freq.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]

def main():
    """Main execution function."""
    websites = [
        "https://idrw.org",
        "https://www.strategicstudyindia.com",
        "https://www.e-ir.info"
    ]
    
    analyzer = DefenseNewsAnalyzer()
    all_articles = []
    
    # Process each website
    for website in websites:
        articles = analyzer.process_website(website)
        if articles:
            all_articles.extend(articles)
            
            # Save site-specific analysis
            site_name = website.split("//")[1].split("/")[0]
            analysis = analyzer.analyze_articles(articles)
            
            with open(analyzer.analysis_dir / f"{site_name}_analysis.json", 'w') as f:
                json.dump(analysis, f, indent=2)
    
    # Generate cross-site comparison
    if all_articles:
        comparison = analyzer.compare_articles(all_articles)
        with open(analyzer.comparison_dir / "cross_site_comparison.json", 'w') as f:
            json.dump(comparison, f, indent=2)
        
        logger.info("\nAnalysis Complete")
        logger.info(f"Total articles processed: {len(all_articles)}")
        logger.info(f"Results saved in: {analyzer.base_dir}")
        
        # Display most similar articles
        logger.info("\nMost similar articles:")
        for pair in comparison["similar_pairs"][:5]:
            logger.info(f"\n{pair['article1']} <-> {pair['article2']}")
            logger.info(f"Similarity: {pair['similarity']:.2%}")

if __name__ == "__main__":
    main()
