# IMDb Scraper

This is a simple Python web scraper that retrieves movie details from IMDb based on specified search keywords. It uses the `requests` and `BeautifulSoup` libraries to make HTTP requests and parse HTML content, as well as handle JSON-LD data.

## Features

- Searches for movies on IMDb using provided keywords.
- Extracts detailed movie information such as name, description, ratings, actors, directors, and writers.
- Stores the extracted data in a CSV file for further analysis.

## Installation

To run this project, ensure you have Python 3.x installed. Then, you can install the required packages by following these steps:

1. Clone this repository:
   ```bash
   git clone https://github.com/paras9498/imdb-data-extractor.git
   cd imdb-data-extractor
   ```

2. Install required pakages:
   ```bash
   pip install -r requirements.txt
   ```

4. To run the scraper, execute the following command
   ```bash
   python imdb.py
   ```
