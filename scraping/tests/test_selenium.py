"""
For testing the Selenium scrapers
"""

from urllib.parse import urlencode

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

    def test_antirobot(self):
        """Test if the anti-robot page is displayed."""

        urls = [
            "https://www.amazon.fr/s?" + urlencode({"k": keyword})
            for keyword in QUERY_KEYWORDS
        ]

        for url in urls:
            self.driver.get(url)
            antirobot = is_antirobot(self.driver)

            assert not antirobot, "Anti-robot page is displayed"

    def test_parse(self):
        """Test the parse method."""

        keywords = list(QUERY_KEYWORDS)
        spider = SearchPageSpider(driver=self.driver, keywords=keywords)

        for url in spider.urls:
            parse_output = spider.parse(url=url)

            assert parse_output, "Method returns empty dict, mainframe not found"
            assert parse_output["next_page"] is not None, "No next page was found"
            assert parse_output["items"] != [], "No items were found"
