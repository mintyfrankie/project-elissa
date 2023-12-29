from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from scraping.spiders.search_page import SearchPageSpider
from scraping.utils.constants import QUERY_KEYWORDS

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)


def scrape_search_page():
    with SearchPageSpider(driver, QUERY_KEYWORDS) as spider:
        spider.run()
        spider.log()


if __name__ == "__main__":
    scrape_search_page()
