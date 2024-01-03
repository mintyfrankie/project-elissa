import pytest
from urllib.parse import urlencode
from scraping.utils import CustomDriver
from mongodb.client import DatabaseClient

PRODUCT_ASIN_LIST = ["B082VVRKTP", "B07YV42X6F", "B07YQFZ3JD", "B09WYHCCSM"]
REVIEW_URLS = [
    "https://www.amazon.fr/SUPVOX-serviettes-hygi%C3%A9niques-pochettes-menstruelle/product-reviews/B07XLKC4WZ/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews",
    "https://www.amazon.fr/Always-ProFresh-Serviettes-Pochettes-Individuelles/product-reviews/B082VVRKTP/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews",
]


@pytest.fixture(scope="module")
def driver():
    """Create a headless Chrome driver."""
    with CustomDriver() as driver:
        yield driver
    driver.quit()


@pytest.fixture(scope="module", params=PRODUCT_ASIN_LIST, ids=PRODUCT_ASIN_LIST)
def product_page(request, driver):
    """Set up the product page."""
    product_page_url = "https://www.amazon.fr/dp/" + request.param
    driver.get(product_page_url)
    return driver


@pytest.fixture(
    scope="module", params=REVIEW_URLS, ids=[i.split("/")[-2] for i in REVIEW_URLS]
)
def review_page(driver, request):
    """Set up the review page."""
    review_page_url = "https://www.amazon.fr/Always-Prot%C3%A8ge-Slips-Incontinence-Protection-Int%C3%A9grale/product-reviews/B00QTJ23IS/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
    driver.get(review_page_url)
    return driver


@pytest.fixture(scope="module")
def search_page(driver):
    """Set up the search page."""

    URL = "https://www.amazon.fr/s?" + urlencode({"k": "tampon+femme"})
    driver.get(URL)
    return driver


@pytest.fixture(scope="module")
def db_client():
    """Create a MongoDB client."""

    return DatabaseClient()


@pytest.fixture(scope="module")
def product():
    """Create a product."""

    return {
        "asin": "B07YQFH15Y",
        "title": "Nana Maxi Goodnight Serviettes Hygiéniques pour la Nuit, 12 Serviettes",
        "image": "https://m.media-amazon.com/images/I/81mY2rB96VL._AC_UL320_.jpg",
    }
