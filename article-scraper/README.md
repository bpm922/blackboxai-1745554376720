# Article Scraper and Summarizer

A powerful tool for scraping, analyzing, and summarizing articles from news websites.

## Features

- Web scraping with automatic rate limiting and retry mechanisms
- Text cleaning and preprocessing
- Keyword extraction
- Article summarization
- Multiple storage formats (JSON, CSV, SQLite)
- Detailed statistics and reporting

## Project Structure

```
article-scraper/
├── requirements.txt      # Project dependencies
├── README.md            # Documentation
├── scraper_cli.py       # Command-line interface
└── src/
    ├── enhanced_scraper.py   # Web scraping functionality
    ├── text_processor.py     # Text cleaning and analysis
    ├── text_summarizer.py    # Article summarization
    └── storage.py           # Data storage handling
```

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

### Command Line Interface

Process one or more URLs:
```bash
python scraper_cli.py -u https://example.com/article1 https://example.com/article2
```

Process URLs from a file:
```bash
python scraper_cli.py -f urls.txt
```

Generate a JSON report:
```bash
python scraper_cli.py -u https://example.com/article --report report.json
```

### Command Line Options

- `-u, --urls`: One or more URLs to process
- `-f, --file`: File containing URLs (one per line)
- `-o, --output-dir`: Output directory for data files (default: data)
- `--report`: Generate JSON report with given filename

### Python API

```python
from src.enhanced_scraper import EnhancedScraper
from src.text_processor import TextProcessor
from src.text_summarizer import TextSummarizer
from src.storage import DataStorage

# Initialize components
scraper = EnhancedScraper()
processor = TextProcessor()
summarizer = TextSummarizer()
storage = DataStorage()

# Process an article
article = scraper.scrape("https://example.com/article")
cleaned_text = processor.clean(article.content)
summary = summarizer.summarize(cleaned_text)
storage.save_article(article.__dict__, summary)
```

## Output

The tool provides:
- Article content and metadata
- Text statistics (word count, reading time, etc.)
- Key topics/keywords
- Article summary
- Summary statistics (compression ratio, etc.)

Results are stored in:
- JSON files for detailed reports
- SQLite database for persistent storage
- CSV files for data analysis

## Example Output

```
Title: Example Article
Author: John Doe
Date: 2024-04-25

Article Statistics:
- Words: 1500
- Sentences: 75
- Reading time: 8 minutes

Key Topics:
technology, innovation, research, development, future

Summary:
[Generated summary of the article...]

Summary Statistics:
- Compression ratio: 30.0%
- Original length: 1500 words
- Summary length: 450 words
```

## Storage

Data is stored in the following locations:
- `data/`: Default storage directory
- `reports/`: JSON reports directory
- `data/articles.db`: SQLite database

## Dependencies

- requests: Web scraping
- beautifulsoup4: HTML parsing
- nltk: Text processing
- loguru: Logging
- pandas: Data handling
