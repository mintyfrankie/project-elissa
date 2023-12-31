"""
A test module for check if we see antirobot pages across all spiders.
"""

from scraping.utils import is_antirobot


def test_search_antirobot(search_page):
    """Test if the anti-robot page is displayed."""
    antirobot = is_antirobot(search_page)
    assert not antirobot, "Anti-robot page is displayed for search page"


def test_product_antirobot(product_page):
    """Test if the anti-robot page is displayed."""
    antirobot = is_antirobot(product_page)
    assert not antirobot, "Anti-robot page is displayed for product page"


def test_review_antirobot(review_page):
    """Test if the anti-robot page is displayed."""
    antirobot = is_antirobot(review_page)
    assert not antirobot, "Anti-robot page is displayed for review page"
