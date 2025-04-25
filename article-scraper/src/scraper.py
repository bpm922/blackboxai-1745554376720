"""
Web scraping module for defense news websites.
"""
import time
import random
from dataclasses import dataclass
from typing import Optional, Dict, List
import requests
from bs4 import BeautifulSoup
from loguru import logger
import validators

@dataclass
class Article:
    """Data class to store article information."""
    url: str
    title: str
    content: str
    author: Optional[str] = None
    date: Optional[str] = None
    metadata: Dict = None

class DefenseNewsScraper:
    """Scraper for defense news websites."""
    
    def __init__(self, 
                 min_delay: float = 3.0,
                 max_delay: float = 5.0,
                 max_retries: int = 3):
        """Initialize the scraper with configuration."""
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.session = self._create_session()
        
        # Configure logging
        logger.add("scraper.log", rotation="500 MB")

    def _create_session(self) -> requests.Session:
        """Create and configure requests session."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        return session

    def _random_delay(self):
        """Implement random delay between requests."""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)

    def get_recent_articles(self, website: str, num_articles: int = 10) -> List[Dict]:
        """Get recent articles from a website."""
        try:
            # Get homepage content
            response = self.session.get(website)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            articles = []
            
            # Different selectors for different websites
            if "idrw.org" in website:
                for article in soup.select('article.post')[:num_articles]:
                    title_elem = article.select_one('h2.entry-title a')
                    if title_elem:
                        articles.append({
                            "title": title_elem.get_text().strip(),
                            "url": title_elem.get("href")
                        })
                        
            elif "strategicstudyindia.com" in website:
                for article in soup.select('div.post')[:num_articles]:
                    title_elem = article.select_one('h3.post-title a')
                    if title_elem:
                        articles.append({
                            "title": title_elem.get_text().strip(),
                            "url": title_elem.get("href")
                        })
                        
            elif "e-ir.info" in website:
                for article in soup.select('article.post')[:num_articles]:
                    title_elem = article.select_one('h2.entry-title a')
                    if title_elem:
                        articles.append({
                            "title": title_elem.get_text().strip(),
                            "url": title_elem.get("href")
                        })
            
            return articles
            
        except Exception as e:
            logger.error(f"Error getting articles from {website}: {str(e)}")
            return []

    def scrape_article(self, url: str) -> Article:
        """Scrape article content from the given URL."""
        if not validators.url(url):
            raise ValueError(f"Invalid URL: {url}")

        logger.info(f"Scraping article from: {url}")
        
        for attempt in range(self.max_retries):
            try:
                self._random_delay()
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Extract content
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
        """Extract article title."""
        title_selectors = [
            ('h1', {'class': ['post-title', 'entry-title', 'article-title']}),
            ('h1', None),
            ('meta', {'property': 'og:title'}),
            ('title', None)
        ]
        
        for tag, attrs in title_selectors:
            element = soup.find(tag, attrs)
            if element:
                if tag == 'meta':
                    return element.get('content', '').strip()
                return element.get_text().strip()
        
        return "Untitled Article"

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article content."""
        # Remove unwanted elements
        for unwanted in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            unwanted.decompose()
        
        content_selectors = [
            ('article', None),
            ('div', {'class': ['post-content', 'entry-content', 'article-content']}),
            ('div', {'class': ['post-body', 'entry-body', 'article-body']}),
            ('div', {'itemprop': 'articleBody'}),
            ('div', {'role': 'main'})
        ]
        
        for tag, attrs in content_selectors:
            content = soup.find(tag, attrs)
            if content:
                paragraphs = []
                for p in content.find_all(['p', 'h2', 'h3', 'h4', 'blockquote']):
                    text = p.get_text().strip()
                    if text and not any(skip in text.lower() for skip in ['advertisement', 'subscribe', 'newsletter']):
                        paragraphs.append(text)
                
                return '\n\n'.join(paragraphs)
        
        return ""

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article author."""
        author_selectors = [
            ('meta', {'name': 'author'}),
            ('meta', {'property': 'article:author'}),
            ('a', {'class': ['author', 'writer', 'byline']}),
            ('span', {'class': ['author', 'writer', 'byline']}),
            ('p', {'class': ['author', 'writer', 'byline']})
        ]
        
        for tag, attrs in author_selectors:
            element = soup.find(tag, attrs)
            if element:
                if tag == 'meta':
                    return element.get('content', '').strip()
                return element.get_text().strip()
        
        return None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article date."""
        date_selectors = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'name': 'publication_date'}),
            ('time', None),
            ('span', {'class': ['date', 'published', 'post-date']}),
            ('p', {'class': ['date', 'published', 'post-date']})
        ]
        
        for tag, attrs in date_selectors:
            element = soup.find(tag, attrs)
            if element:
                if tag == 'meta':
                    return element.get('content', '').strip()
                return element.get_text().strip()
        
        return None

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract article metadata."""
        metadata = {}
        
        meta_properties = [
            'og:type', 'og:site_name', 'article:section',
            'article:tag', 'twitter:card', 'twitter:site'
        ]
        
        for prop in meta_properties:
            element = soup.find('meta', {'property': prop})
            if element:
                metadata[prop] = element.get('content', '')
        
        # Extract article tags/categories
        tags = []
        for tag_element in soup.find_all(['a', 'span'], {'class': ['tag', 'category']}):
            tag_text = tag_element.get_text().strip()
            if tag_text:
                tags.append(tag_text)
        
        if tags:
            metadata['tags'] = tags
        
        return metadata
