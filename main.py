"""
Main entry of the program.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from scraping.spiders.search_page import SearchPageSpider
from scraping.utils.constants import QUERY_KEYWORDS

if __name__ == "__main__":
    options = Options()
    options.add_argument("--headless")

    with webdriver.Chrome(options=options) as driver:
        spider = SearchPageSpider(
            driver,
            keywords=QUERY_KEYWORDS,
        )
        spider.run()
