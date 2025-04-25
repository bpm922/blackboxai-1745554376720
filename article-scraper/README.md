# Defense News Analyzer

A Python tool for scraping, analyzing, and comparing defense news articles from multiple sources.

## Features

- Automated scraping of recent articles from defense news websites
- Text cleaning and preprocessing
- Article summarization using extractive techniques
- Keyword extraction and analysis
- Cross-article comparison and similarity analysis
- Detailed statistics and reporting

## Project Structure

```
article-scraper/
├── analyzer.py         # Main script
├── requirements.txt    # Project dependencies
├── README.md          # Documentation
└── src/
    ├── scraper.py     # Web scraping functionality
    ├── processor.py   # Text cleaning and analysis
    └── summarizer.py  # Article summarization
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

Run the analyzer:
```bash
python analyzer.py
```

This will:
1. Scrape recent articles from configured defense news websites
2. Process and analyze each article
3. Generate summaries and extract keywords
4. Perform cross-article comparison
5. Save results in organized directories:
   - `analysis/articles/` - Individual article data
   - `analysis/analysis/` - Site-specific analysis
   - `analysis/comparison/` - Cross-site comparison results

## Supported Websites

Currently supports:
- IDRW (Indian Defence Research Wing) - https://idrw.org
- Strategic Study India - https://www.strategicstudyindia.com
- E-International Relations - https://www.e-ir.info

## Output Structure

### Article Data
Each article is saved with:
- Original URL and metadata
- Cleaned content
- Generated summary
- Extracted keywords
- Author and date information

### Analysis Data
Site-specific analysis includes:
- Total articles processed
- Average article length
- Common keywords and themes
- Summary statistics

### Comparison Data
Cross-site comparison includes:
- Similar article pairs with similarity scores
- Common themes across sites
- Content similarity metrics

## Features in Detail

### Web Scraping
- Polite scraping with configurable delays
- Automatic retry on failure
- Smart content extraction
- Metadata collection

### Text Processing
- HTML cleanup
- Content normalization
- Keyword extraction
- Reading time estimation

### Analysis
- Extractive summarization
- Cross-article comparison
- Theme identification
- Similarity scoring

## Dependencies

- Web Scraping:
  * requests
  * beautifulsoup4
  * lxml

- Text Processing:
  * nltk
  * scikit-learn

- Analysis:
  * numpy
  * pandas

- Utilities:
  * loguru
  * validators

## Notes

- The tool implements polite scraping with configurable delays between requests
- Articles are saved separately for easy access and reference
- Comparison analysis helps identify related stories across different sources
- All data is stored locally in organized directories

## Example Output

```json
{
  "similar_pairs": [
    {
      "article1": "Article Title 1",
      "article2": "Article Title 2",
      "similarity": 0.35
    }
  ],
  "common_themes": [
    ["defense", 10],
    ["military", 8],
    ["technology", 6]
  ]
}
```

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

MIT License
