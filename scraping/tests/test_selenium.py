"""
For testing the Selenium scrapers
"""

from urllib.parse import urlencode

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from scraping.spiders.search_page import (
    get_asin_cards,
    get_mainframe,
    get_nextpage,
    parse_asin_card,
)
from scraping.utils.common import is_antirobot


@pytest.fixture
def driver():
    """Create a headless Chrome driver."""

    options = Options()
    options.add_argument("--headless")
    with webdriver.Chrome(options=options) as driver:
        yield driver


@pytest.fixture
def setup_page(driver):
    """Set up the search page."""

    URL = "https://www.amazon.fr/s?" + urlencode({"k": "tampon+femme"})
    driver.get(URL)
    return driver


class TestSearchPageSpider:
    """Test the SearchPageSpider."""

    def test_antirobot(self, setup_page):
        """Test if the anti-robot page is displayed."""
        antirobot = is_antirobot(setup_page)
        assert not antirobot, "Anti-robot page is displayed"

    def test_get_mainframe(self, setup_page):
        """Test if the main frame is found."""
        main_frame = get_mainframe(setup_page)
        assert main_frame, "Main frame is not found"

    def test_get_asin_cards(self, setup_page):
        """Test if the ASIN cards are found."""
        main_frame = get_mainframe(setup_page)
        asin_cards = get_asin_cards(main_frame)
        assert asin_cards, "ASIN cards are not found"

    def test_parse_asin_card(self, setup_page):
        """Test if the ASIN card is parsed."""
        NUM_ASIN_CARDS_TO_TEST = 10
        MIN_AVAILABLE_ASIN_CARDS = 5

        main_frame = get_mainframe(setup_page)
        asin_cards = get_asin_cards(main_frame)

        assert len(asin_cards) >= NUM_ASIN_CARDS_TO_TEST, "Not enough ASIN cards"

        asin_count = 0
        title_count = 0

        for asin_card in asin_cards[:NUM_ASIN_CARDS_TO_TEST]:
            item = parse_asin_card(asin_card)
            assert item, "ASIN card is not parsed"
            asin_count += 1
            if item["title"]:
                title_count += 1

        assert title_count >= MIN_AVAILABLE_ASIN_CARDS, "Not enough titles are parsed"

    def test_get_nextpage(self, setup_page):
        """Test if the page is turned."""

        next_page = get_nextpage(setup_page)
        assert next_page, "Page is not turned"
