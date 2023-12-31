"""
Test the SearchPageSpider.
"""


from scraping.spiders.search_page import (
    get_asin_cards,
    get_mainframe,
    get_nextpage,
    parse_asin_card,
)


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
