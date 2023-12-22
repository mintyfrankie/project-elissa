"""
For testing the Selenium scrapers
"""

from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
            assert (
                "toutes nos excuses" not in self.driver.title.lower()
            ), "Anti-bot detected"
