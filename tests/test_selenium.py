"""
For testing the Selenium scrapers.
"""

from urllib.parse import urlencode

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from scraping.spiders.product_page import (
    get_avg_rating,
    get_brand,
    get_feature_bullets,
    get_num_reviews,
    get_price,
    get_review_url,
    get_title,
    get_unities,
)
from scraping.spiders.search_page import (
    SearchPageSpider,
    get_asin_cards,
    get_mainframe,
    get_nextpage,
    parse_asin_card,
)
from scraping.utils.common import is_antirobot


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


def get_random_asins():
    """Return a list of random ASINs."""
    from mongodb.client import DatabaseClient

    client = DatabaseClient()
    pipeline = [
        {"$match": {"metadata.product_page_scraped": False}},
        {"$sample": {"size": 5}},
        {"$project": {"asin": 1, "_id": 0}},
    ]
    random_documents = list(client.collection.aggregate(pipeline))
    for doc in random_documents:
        yield doc["asin"]
    client.close()


@pytest.fixture(scope="class", params=get_random_asins(), ids=range(5))
def product_page(request, driver):
    """Set up the product page."""
    product_page_url = "https://www.amazon.fr/dp/" + request.param
    driver.get(product_page_url)
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


# FIXME: find ways to set pass criteria to a total of 50% of the test cases
class TestProductPageSpider:
    """Test the ProductPageSpider."""

    def test_antirobot(self, product_page):
        """Test if the anti-robot page is displayed."""
        antirobot = is_antirobot(product_page)
        assert not antirobot, "Anti-robot page is displayed"

    def test_get_price(self, product_page):
        """Test if the price is found."""
        price = get_price(product_page)
        assert price, "Price is not found"
        assert price > 0, "Price is not positive"

    def test_get_title(self, product_page):
        """Test if the title is found."""
        title = get_title(product_page)
        assert title, "Title is not found"
        assert len(title) > 0, "Title is empty"

    def test_get_brand(self, product_page):
        """Test if the brand is found."""
        brand = get_brand(product_page)
        assert brand, "Brand is not found"
        assert len(brand) > 0, "Brand is empty"

    def test_get_avg_rating(self, product_page):
        """Test if the average rating is found."""
        avg_rating = get_avg_rating(product_page)
        assert avg_rating, "Average rating is not found"
        assert 0 <= avg_rating <= 5, "Average rating is not in [0, 5]"

    def test_get_feature_bullets(self, product_page):
        """Test if the feature bullets are found."""
        feature_bullets = get_feature_bullets(product_page)
        assert feature_bullets, "Feature bullets are not found"
        assert len(feature_bullets) > 0, "Feature bullets are empty"

    def test_get_num_reviews(self, product_page):
        """Test if the number of reviews is found."""
        num_reviews = get_num_reviews(product_page)
        assert num_reviews, "Number of reviews is not found"
        assert num_reviews > 0, "Number of reviews is not positive"

    def test_get_review_url(self, product_page):
        """Test if the review URL is found."""
        review_url = get_review_url(product_page)
        assert review_url, "Review URL is not found"
        assert len(review_url) > 0, "Review URL is empty"

    def test_get_unities(self, product_page):
        """Test if the unities are found."""
        unities = get_unities(product_page)
        assert unities, "Unities are not found"
        assert unities > 0, "Unities are not positive"
