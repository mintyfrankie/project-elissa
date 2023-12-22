"""
For testing the Selenium scrapers
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class TestSearchPageSpider:
    """Test the search page spider."""

    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    url = "https://www.amazon.fr/s?k=tampon+femme"

    driver.get(url)

    def test_antirobot(self):
        """Test if the anti-robot page is displayed."""

        assert (
            "toutes nos excuses" not in self.driver.title.lower()
        ), "Anti-bot detected"
