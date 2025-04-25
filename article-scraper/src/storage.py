"""
Storage module for managing scraped articles and summaries.
"""
import json
import csv
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Union, Optional
import pandas as pd
from loguru import logger

class DataStorage:
    """Handles storage and retrieval of scraped articles and summaries."""
    
    def __init__(self, base_dir: str = "data"):
        """
        Initialize the storage system.
        
        Args:
            base_dir: Base directory for storing data files
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize SQLite database
        self.db_path = self.base_dir / "articles.db"
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with required tables."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Create articles table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT UNIQUE NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        author TEXT,
                        date TEXT,
                        metadata TEXT,
                        summary TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def save_article(self, 
                    article: Dict, 
                    summary: Optional[str] = None, 
                    format: str = "all") -> None:
        """
        Save article data in specified format(s).
        
        Args:
            article: Article data dictionary
            summary: Optional article summary
            format: Storage format ('json', 'csv', 'sqlite', or 'all')
        """
        try:
            if format in ['json', 'all']:
                self._save_json(article, summary)
            
            if format in ['csv', 'all']:
                self._save_csv(article, summary)
            
            if format in ['sqlite', 'all']:
                self._save_sqlite(article, summary)
                
            logger.info(f"Article saved successfully: {article['title']}")
            
        except Exception as e:
            logger.error(f"Failed to save article: {str(e)}")
            raise

    def _save_json(self, article: Dict, summary: Optional[str]) -> None:
        """Save article data as JSON file."""
        file_path = self.base_dir / "articles.json"
        
        # Load existing data
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
        
        # Add new article
        article_data = {**article}
        if summary:
            article_data['summary'] = summary
        article_data['saved_at'] = datetime.now().isoformat()
        
        data.append(article_data)
        
        # Save updated data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_csv(self, article: Dict, summary: Optional[str]) -> None:
        """Save article data to CSV file."""
        file_path = self.base_dir / "articles.csv"
        
        # Prepare data row
        row = {
            'url': article['url'],
            'title': article['title'],
            'content': article['content'],
            'author': article.get('author', ''),
            'date': article.get('date', ''),
            'summary': summary or '',
            'saved_at': datetime.now().isoformat()
        }
        
        # Determine if file exists to write headers
        file_exists = file_path.exists()
        
        # Write to CSV
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

    def _save_sqlite(self, article: Dict, summary: Optional[str]) -> None:
        """Save article data to SQLite database."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Convert metadata to JSON string if present
            metadata = json.dumps(article.get('metadata', {})) if article.get('metadata') else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO articles 
                (url, title, content, author, date, metadata, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                article['url'],
                article['title'],
                article['content'],
                article.get('author'),
                article.get('date'),
                metadata,
                summary
            ))
            
            conn.commit()

    def load_articles(self, 
                     format: str = "sqlite", 
                     filters: Optional[Dict] = None) -> List[Dict]:
        """
        Load articles from storage with optional filtering.
        
        Args:
            format: Storage format to load from ('json', 'csv', or 'sqlite')
            filters: Optional dictionary of filter criteria
            
        Returns:
            List[Dict]: List of article dictionaries
        """
        try:
            if format == "json":
                return self._load_json(filters)
            elif format == "csv":
                return self._load_csv(filters)
            elif format == "sqlite":
                return self._load_sqlite(filters)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to load articles: {str(e)}")
            return []

    def _load_json(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Load articles from JSON file."""
        file_path = self.base_dir / "articles.json"
        
        if not file_path.exists():
            return []
            
        with open(file_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)
            
        if filters:
            return self._apply_filters(articles, filters)
        return articles

    def _load_csv(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Load articles from CSV file."""
        file_path = self.base_dir / "articles.csv"
        
        if not file_path.exists():
            return []
            
        df = pd.read_csv(file_path)
        articles = df.to_dict('records')
        
        if filters:
            return self._apply_filters(articles, filters)
        return articles

    def _load_sqlite(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Load articles from SQLite database."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM articles"
            params = []
            
            if filters:
                conditions = []
                for key, value in filters.items():
                    if key in ['url', 'title', 'author']:
                        conditions.append(f"{key} LIKE ?")
                        params.append(f"%{value}%")
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(query, params)
            articles = [dict(row) for row in cursor.fetchall()]
            
            # Parse metadata JSON
            for article in articles:
                if article['metadata']:
                    article['metadata'] = json.loads(article['metadata'])
                    
            return articles

    def _apply_filters(self, articles: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters to article list."""
        filtered = articles.copy()
        
        for key, value in filters.items():
            filtered = [
                article for article in filtered
                if str(value).lower() in str(article.get(key, '')).lower()
            ]
            
        return filtered

    def export_data(self, 
                    format: str = "json", 
                    output_path: Optional[str] = None) -> None:
        """
        Export all stored data to specified format.
        
        Args:
            format: Export format ('json' or 'csv')
            output_path: Optional custom output path
        """
        try:
            articles = self.load_articles(format="sqlite")
            
            if not output_path:
                output_path = self.base_dir / f"articles_export.{format}"
            
            if format == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(articles, f, indent=2, ensure_ascii=False)
                    
            elif format == "csv":
                df = pd.DataFrame(articles)
                df.to_csv(output_path, index=False, encoding='utf-8')
                
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
            logger.info(f"Data exported successfully to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export data: {str(e)}")
            raise

    def get_stats(self) -> Dict:
        """
        Get statistics about stored articles.
        
        Returns:
            Dict: Dictionary containing storage statistics
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                stats = {
                    'total_articles': cursor.execute(
                        "SELECT COUNT(*) FROM articles"
                    ).fetchone()[0],
                    'articles_with_summary': cursor.execute(
                        "SELECT COUNT(*) FROM articles WHERE summary IS NOT NULL"
                    ).fetchone()[0],
                    'unique_authors': cursor.execute(
                        "SELECT COUNT(DISTINCT author) FROM articles WHERE author IS NOT NULL"
                    ).fetchone()[0],
                    'latest_article': cursor.execute(
                        "SELECT created_at FROM articles ORDER BY created_at DESC LIMIT 1"
                    ).fetchone()[0] if cursor.execute(
                        "SELECT COUNT(*) FROM articles"
                    ).fetchone()[0] > 0 else None
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get storage stats: {str(e)}")
            return {}
