"""
Web scraping module for fetching articles from various sources.
"""
import time
import random
from dataclasses import dataclass
from typing import Optional, Dict, List
import requests
from bs4 import BeautifulSoup
from loguru import logger
import validators
from urllib.parse import urlparse

@dataclass
class Article:
    """Data class to store article information."""
    url: str
    title: str
    content: str
    author: Optional[str] = None
    date: Optional[str] = None
    metadata: Dict = None

class ArticleScraper:
    """Main scraper class for fetching articles from websites."""
    
    def __init__(self, 
                 min_delay: float = 1.0,
                 max_delay: float = 3.0,
                 max_retries: int = 3):
        """
        Initialize the scraper with configuration.
        
        Args:
            min_delay: Minimum delay between requests in seconds
            max_delay: Maximum delay between requests in seconds
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.session = self._create_session()
        
        # Configure logging
        logger.add("scraper.log", rotation="500 MB")

    def _create_session(self) -> requests.Session:
        """Create and configure requests session with rotating user agents."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        return session

    def _validate_url(self, url: str) -> bool:
        """
        Validate if the provided URL is valid.
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if URL is valid, False otherwise
        """
        return bool(validators.url(url))

    def _random_delay(self):
        """Implement random delay between requests to avoid rate limiting."""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)

    def scrape(self, url: str) -> Article:
        """
        Scrape article content from the given URL.
        
        Args:
            url: URL of the article to scrape
            
        Returns:
            Article: Article object containing scraped content
            
        Raises:
            ValueError: If URL is invalid
            RequestException: If scraping fails after max retries
        """
        if not self._validate_url(url):
            raise ValueError(f"Invalid URL: {url}")

        logger.info(f"Scraping article from: {url}")
        
        for attempt in range(self.max_retries):
            try:
                self._random_delay()
                response = self.session.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Extract article content
                title = self._extract_title(soup)
                content = self._extract_content(soup)
                author = self._extract_author(soup)
                date = self._extract_date(soup)
                metadata = self._extract_metadata(soup)
                
                article = Article(
                    url=url,
                    title=title,
                    content=content,
                    author=author,
                    date=date,
                    metadata=metadata
                )
                
                logger.success(f"Successfully scraped article: {title}")
                return article
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to scrape article after {self.max_retries} attempts")
                    raise

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title from the page."""
        # Try different common title elements
        title = soup.find('h1')
        if not title:
            title = soup.find('meta', property='og:title')
        if not title:
            title = soup.find('title')
            
        return title.get_text().strip() if title else "Untitled Article"

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content from the page."""
        # Try common article content containers
        content_tags = [
            soup.find('article'),
            soup.find('div', class_=['article-content', 'post-content', 'entry-content']),
            soup.find('div', {'role': 'main'}),
        ]
        
        for tag in content_tags:
            if tag:
                # Remove unwanted elements
                for unwanted in tag.find_all(['script', 'style', 'nav', 'header', 'footer']):
                    unwanted.decompose()
                    
                return tag.get_text(separator='\n').strip()
                
        return ""

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article author if available."""
        author = soup.find('meta', {'name': 'author'}) or \
                soup.find('a', rel='author') or \
                soup.find('span', class_='author')
                
        return author.get('content', author.get_text()).strip() if author else None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article publication date if available."""
        date = soup.find('meta', {'property': 'article:published_time'}) or \
               soup.find('time') or \
               soup.find('span', class_=['date', 'published'])
               
        return date.get('content', date.get_text()).strip() if date else None

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract additional metadata from the page."""
        metadata = {}
        
        # Extract meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name', tag.get('property', ''))
            content = tag.get('content', '')
            if name and content:
                metadata[name] = content
                
        return metadata

    def bulk_scrape(self, urls: List[str]) -> List[Article]:
        """
        Scrape multiple articles from a list of URLs.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List[Article]: List of scraped articles
        """
        articles = []
        for url in urls:
            try:
                article = self.scrape(url)
                articles.append(article)
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {str(e)}")
                continue
        return articles
