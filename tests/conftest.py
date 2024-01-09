"""
Contains fixtures for the tests.
"""

from urllib.parse import urlencode

import pytest

from mongodb.client import DatabaseClient
from scraping.common import SeleniumDriver, get_driver

ASIN_LIST = [
    "B08BX8TTVS",
    "B082VVDS19",
    "B07YQFH15Y",
]

REVIEW_URLS = [
    "https://www.amazon.fr/Vania-Kotydia-Protege-slips-Confort-Normal/product-reviews/B07SC8SH6W/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews",  # pylint: disable=line-too-long
    "https://www.amazon.fr/Love-Green-Prot%C3%A8ge-slips-Flexi-28/product-reviews/B082VVDS19/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews",  # pylint: disable=line-too-long
    "https://www.amazon.fr/Vania-Kotydia-Protege-slips-Protect-Large/product-reviews/B07YQFYH3V/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews",  # pylint: disable=line-too-long
]

### Selenium-related fixtures


@pytest.fixture(scope="module")
def test_driver() -> SeleniumDriver:
    """Create a Selenium Driver."""
    with get_driver(driver_type="Chrome") as x:
        yield x
    x.quit()


@pytest.fixture(scope="module", params=ASIN_LIST, ids=ASIN_LIST)
def product_page(request, test_driver) -> SeleniumDriver:  # pylint: disable=redefined-outer-name
    """Set up the product page."""

    product_page_url = "https://www.amazon.fr/dp/" + request.param
    test_driver.get(product_page_url)
    return test_driver


@pytest.fixture(
    scope="module", params=REVIEW_URLS, ids=[i.split("/")[-2] for i in REVIEW_URLS]
)
def review_page(request, test_driver) -> SeleniumDriver:  # pylint: disable=redefined-outer-name
    """Set up the review page."""
    review_page_url = request.param
    test_driver.get(review_page_url)
    return test_driver


@pytest.fixture(scope="module")
def search_page(test_driver) -> SeleniumDriver:  # pylint: disable=redefined-outer-name
    """Set up the search page."""
    url = "https://www.amazon.fr/s?" + urlencode({"k": "tampon+femme"})
    test_driver.get(url)
    return test_driver


### MongoDB-related fixtures


@pytest.fixture(scope="module")
def db_client() -> DatabaseClient:
    """Create a MongoDB client."""

    with DatabaseClient(action_type="Test") as client:
        yield client
    client.close()


@pytest.fixture(scope="module")
def product() -> dict:
    """Create a product."""

    return {
        "asin": "B07YQFH15Y",
        "title": "Nana Maxi Goodnight Serviettes Hygiéniques pour la Nuit, 12 Serviettes",
        "image": "https://m.media-amazon.com/images/I/81mY2rB96VL._AC_UL320_.jpg",
    }
