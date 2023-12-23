"""
For testing the Selenium scrapers
"""

from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from scraping.spiders.search_page import SearchPageSpider
from scraping.utils.common import is_antirobot
from scraping.utils.constants import QUERY_KEYWORDS


class TestSearchPageSpider:
    """Test the search page spider."""

    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    urls = [
        urljoin("https://www.amazon.fr/s?k=", keyword) for keyword in QUERY_KEYWORDS
    ]

    def test_antirobot(self):
        """Test if the anti-robot page is displayed."""

        for url in self.urls:
            self.driver.get(url)
            antirobot = is_antirobot(self.driver)

            assert antirobot is False, "Anti-robot page is displayed"

    def test_parse(self):
        """Test the parse method."""

        spider = SearchPageSpider(driver=self.driver, urls=self.urls)

        for url in self.urls:
            parse_output = spider.parse(url=url)
            print(parse_output)

            assert parse_output, "No output was found"
            assert parse_output["next_page"] is not None, "No next page was found"
            assert parse_output["items"] != [], "No items were found"
