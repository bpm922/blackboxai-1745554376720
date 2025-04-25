# Article Scraper and Summarizer

A powerful and flexible tool for scraping web articles, processing their content, and generating summaries.

## Features

- Robust web scraping with automatic rate limiting and retry mechanisms
- Smart content extraction focusing on main article content
- Advanced text preprocessing and cleaning
- Multiple summarization options using Gensim
- Flexible storage options (JSON, CSV, SQLite)
- Detailed logging and error handling
- Progress tracking for bulk operations

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```python
from src.scraper import ArticleScraper
from src.processor import TextProcessor
from src.summarizer import ArticleSummarizer

# Initialize components
scraper = ArticleScraper()
processor = TextProcessor()
summarizer = ArticleSummarizer()

# Scrape and process an article
url = "https://example.com/article"
article = scraper.scrape(url)
cleaned_text = processor.clean(article.content)
summary = summarizer.summarize(cleaned_text)

# Print results
print(f"Title: {article.title}")
print(f"Summary: {summary}")
```

## Configuration

The system can be configured through environment variables or a config file. See the documentation for available options.

## License

MIT License
