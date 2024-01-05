"""
Test the SearchPageSpider.
"""


from urllib.parse import urlencode

from scraping.spiders.search_page import (
    SearchItemScraper,
    SearchPageSpiderWorker,
    get_asin_cards,
    get_mainframe,
    get_nextpage,
    parse_asin_card,
)
from scraping.utils.constants import QUERY_KEYWORDS


class TestSearchPageFunctions:
    """Test the SearchPageSpider."""

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


def test_SearchItemScraper(search_page):
    """Test the SearchItemScraper."""
    scraper = SearchItemScraper(
        driver=search_page,
        starting_url="https://www.amazon.fr/s?" + urlencode({"k": "tampon+femme"}),
        max_page=1,
    )
    scraper.run()
    data = scraper.dump()
    assert len(data) > 0, "No data is scraped"
    assert scraper.validate(), "Data is not validated"


def test_SearchPageSpiderWorker(driver):
    """Test the SearchPageSpiderWorker."""
    try:
        with SearchPageSpiderWorker(
            driver=driver,
            action_type="Testing - pytest test_SearchPageSpiderWorker",
            queue=list(QUERY_KEYWORDS)[0],
            max_page=1,
        ) as worker:
            worker.run()
    except Exception as e:
        assert False, f"Exception raised: {e}"
