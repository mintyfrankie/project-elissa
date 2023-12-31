"""
Test the ProductPageSpider.
"""


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
from scraping.utils.common import is_antirobot

ASIN_LIST = ["B082VVRKTP", "B07YV42X6F", "B07YQFZ3JD", "B09WYHCCSM"]


@pytest.fixture(scope="module")
def driver():
    """Create a headless Chrome driver."""

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--lang=fr")
    with webdriver.Chrome(options=options) as driver:
        yield driver
    driver.quit()


@pytest.fixture(scope="module", params=ASIN_LIST, ids=ASIN_LIST)
def product_page(request, driver):
    """Set up the product page."""
    product_page_url = "https://www.amazon.fr/dp/" + request.param
    driver.get(product_page_url)
    return driver


def test_antirobot(product_page):
    """Test if the anti-robot page is displayed."""
    antirobot = is_antirobot(product_page)
    assert not antirobot, "Anti-robot page is displayed"


class TestProductPageFunctions:
    """Test the ProductPageSpider parsing functions."""

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
