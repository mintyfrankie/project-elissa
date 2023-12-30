"""
Test the SearchPageSpider.
"""

from urllib.parse import urlencode

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from scraping.utils.common import is_antirobot

from scraping.spiders.search_page import (
    SearchPageSpider,
    get_asin_cards,
    get_mainframe,
    get_nextpage,
    parse_asin_card,
)


@pytest.fixture(scope="class")
def driver():
    """Create a headless Chrome driver."""

    options = Options()
    options.add_argument("--headless")
    with webdriver.Chrome(options=options) as driver:
        yield driver
    driver.quit()


@pytest.fixture(scope="class")
def search_page(driver):
    """Set up the search page."""

    URL = "https://www.amazon.fr/s?" + urlencode({"k": "tampon+femme"})
    driver.get(URL)
    return driver


class TestSearchPageSpider:
    """Test the SearchPageSpider."""

    def test_antirobot(self, search_page):
        """Test if the anti-robot page is displayed."""
        antirobot = is_antirobot(search_page)
        assert not antirobot, "Anti-robot page is displayed"

    def test_get_mainframe(self, search_page):
        """Test if the main frame is found."""
        main_frame = get_mainframe(search_page)
        assert main_frame, "Main frame is not found"

    def test_get_asin_cards(self, search_page):
        """Test if the ASIN cards are found."""
        main_frame = get_mainframe(search_page)
        assert main_frame, "Main frame is not found"
        asin_cards = get_asin_cards(main_frame)
        assert asin_cards, "ASIN cards are not found"

    def test_parse_asin_card(self, search_page):
        """Test if the ASIN card is parsed."""
        NUM_ASIN_CARDS_TO_TEST = 10
        MIN_AVAILABLE_ASIN_CARDS = 5

        main_frame = get_mainframe(search_page)
        assert main_frame, "Main frame is not found"
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

    def test_get_nextpage(self, search_page):
        """Test if the page is turned."""

        next_page = get_nextpage(search_page)
        assert next_page, "Page is not turned"

    @pytest.mark.skip(reason="Too costly to run")
    def test_Spider(self, driver):
        """Test the Spider."""

        spider = SearchPageSpider(driver, keywords={"tampon femme"})
        data = spider.run()
        assert data, "Spider does not work"
        assert spider.meta is not None, "Meta data is not found"

        asins = [item["asin"] for item in data]
        assert len(asins) == len(set(asins)), "Duplicates ASINs are found"
