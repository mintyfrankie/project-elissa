"""
Test the ReviewPageSpider.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from scraping.spiders.review_page import (
    get_body,
    get_metadata,
    get_next_page,
    get_rating,
    get_review_cards,
    get_title,
    parse_item,
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


REVIEW_URLS = [
    "https://www.amazon.fr/SUPVOX-serviettes-hygi%C3%A9niques-pochettes-menstruelle/product-reviews/B07XLKC4WZ/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews",
    "https://www.amazon.fr/Always-ProFresh-Serviettes-Pochettes-Individuelles/product-reviews/B082VVRKTP/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews",
]


@pytest.fixture(
    scope="class", params=REVIEW_URLS, ids=[i.split("/")[-2] for i in REVIEW_URLS]
)
def review_page(driver, request):
    """Set up the review page."""
    review_page_url = "https://www.amazon.fr/Always-Prot%C3%A8ge-Slips-Incontinence-Protection-Int%C3%A9grale/product-reviews/B00QTJ23IS/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
    driver.get(review_page_url)
    return driver


class TestReviewPageSpider:
    """Test the ReviewPageSpider."""

    def test_antirobot(self, review_page):
        """Test if the anti-robot page is displayed."""
        antirobot = is_antirobot(review_page)
        assert not antirobot, "Anti-robot page is displayed"

    def test_get_review_cards(self, review_page):
        """Test if the review cards are found."""
        review_cards = get_review_cards(review_page)
        assert review_cards, "Review cards are not found"
        return review_cards[0]

    def test_get_rating(self, review_page):
        """Test if the rating is found."""
        review_cards = get_review_cards(review_page)
        rating = get_rating(review_cards[0])
        assert rating, "Rating is not found"
        assert isinstance(rating, int), "Rating is not an integer"
        assert 1 <= rating <= 5, "Rating is not between 1 and 5"

    def test_get_title(self, review_page):
        """Test if the title is found."""
        review_cards = get_review_cards(review_page)
        title = get_title(review_cards[0])
        assert title, "Title is not found"
        assert isinstance(title, str), "Title is not a string"

    def test_get_metadata(self, review_page):
        """Test if the metadata is found."""
        review_cards = get_review_cards(review_page)
        metadata = get_metadata(review_cards[0])
        assert metadata, "Metadata is not found"
        assert isinstance(metadata, tuple), "Metadata is not a tuple"
        assert len(metadata) == 2, "Metadata is not of length 2"
        assert isinstance(metadata[0], str), "Country is not a string"
        assert isinstance(metadata[1], str), "Date is not a string"

    def test_get_body(self, review_page):
        """Test if the body is found."""
        review_cards = get_review_cards(review_page)
        body = get_body(review_cards[0])
        assert body, "Body is not found"
        assert isinstance(body, str), "Body is not a string"

    def test_get_next_page(self, review_page):
        """Test if the next page is found."""
        next_page = get_next_page(review_page)
        assert next_page, "Next page is not found"
        assert isinstance(next_page, str), "Next page is not a string"
