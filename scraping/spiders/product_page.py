"""
A spider for scraping the product pages of the website.
"""

from types import SimpleNamespace
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By

from scraping.base import BaseItemScraper, BaseSpiderWorker
from scraping.common import SeleniumDriver, is_antirobot
from scraping.interfaces import ItemMetadata

PATTERNS = SimpleNamespace(
    price_1="//span[contains(@class, 'apexPriceToPay')]//span[@class='a-offscreen']",
    price_2="//div[@data-feature-name='corePriceDisplay_desktop']//span[contains(@class, 'aok-offscreen')]",
    price_3="//div[@data-feature-name='corePriceDisplay_desktop']//span[contains(@class, 'a-offscreen')]",
    unities="//table[@id='productDetails_techSpec_section_1']//th[text()=' Unités ']/following-sibling::td",
    feature_bullets="//div[@id='feature-bullets']//span[@class='a-list-item']",
    review_url="//a[@data-hook='see-all-reviews-link-foot']",
    title_id="productTitle",
    brand_id="bylineInfo",
    rating_id="acrPopover",
    num_reviews_id="acrCustomerReviewText",
    category_id="wayfinding-breadcrumbs_feature_div",
    category_section=".//li[1]/a",
)


def check_category(driver: webdriver.Chrome) -> bool:
    """
    Check if the product is in the right category.
    """

    TARGET_CATEGORY = "Hygiène et Santé"
    category = driver.find_elements(By.XPATH, PATTERNS.category_id)
    if category:
        category = category[0].find_elements(By.XPATH, PATTERNS.category_section)
        if category:
            category = category[0].get_attribute("textContent")
            if category and TARGET_CATEGORY in category:
                return True
    return False


def get_price(driver: webdriver.Chrome) -> float | None:
    """
    Return the price of the product.
    """

    price = driver.find_elements(By.XPATH, PATTERNS.price_1)
    if price:
        price = price[0].get_attribute("textContent")
        price = float(
            str(price).split("&nbsp;", maxsplit=1)[0].replace(",", ".").replace("€", "")
        )
        return price

    price = driver.find_elements(By.XPATH, PATTERNS.price_2)
    if price:
        price = price[0].get_attribute("textContent")
        price = float(
            str(price)
            .strip()
            .replace("\xa0", " ")
            .split(" ", maxsplit=1)[0]
            .replace(",", ".")
        )
        return price

    price = driver.find_elements(By.XPATH, PATTERNS.price_3)
    if price:
        price = price[0].get_attribute("textContent")
        price = float(
            str(price)
            .strip()
            .replace("\xa0", " ")
            .split(" ", maxsplit=1)[0]
            .replace(",", ".")
            .replace("€", "")
        )
        return price

    return None


def get_title(driver: webdriver.Chrome) -> str | None:
    """
    Return the title of the product.
    """

    title = driver.find_elements(By.ID, PATTERNS.title_id)
    if title:
        title = title[0].get_attribute("textContent")
        if title:
            title = title.strip()
            return title

    return None


def get_brand(driver: webdriver.Chrome) -> str | None:
    """
    Return the brand of the product.
    """

    brand = driver.find_elements(By.ID, PATTERNS.brand_id)
    if brand:
        brand = brand[0].get_attribute("textContent")
        if brand:
            brand = brand.split(" ")[-1].strip()
            return brand

    return None


def get_avg_rating(driver: webdriver.Chrome) -> float | None:
    """
    Return the average rating of the product.
    """

    rating = driver.find_elements(By.ID, PATTERNS.rating_id)
    if rating:
        rating = rating[0].get_attribute("title")
        if rating:
            rating = float(rating.split(" ")[0].replace(",", "."))
            return rating

    return None


def get_num_reviews(driver: webdriver.Chrome) -> int | None:
    """
    Return the number of reviews of the product.
    """

    def split_num_reviews(num_reviews: str) -> int:
        num_reviews = num_reviews.strip().replace("\xa0", " ")
        elems = num_reviews.split(" ")[:-1]
        if len(elems) == 1:
            return int(elems[0])
        else:
            return int("".join(elems))

    num_reviews = driver.find_elements(By.ID, PATTERNS.num_reviews_id)
    if num_reviews:
        num_reviews = num_reviews[0].get_attribute("textContent")
        if num_reviews:
            num_reviews = split_num_reviews(num_reviews)
            return num_reviews

    return None


def get_feature_bullets(driver: webdriver.Chrome) -> list[str] | None:
    """
    Return the feature bullets of the product.
    """

    feature_bullets = driver.find_elements(By.XPATH, PATTERNS.feature_bullets)
    if feature_bullets:
        feature_bullets = [
            bullet.get_attribute("textContent") for bullet in feature_bullets
        ]
        feature_bullets = [bullet.strip() for bullet in feature_bullets if bullet]
        return feature_bullets

    return None


def get_unities(driver: webdriver.Chrome) -> int | None:
    """
    Return the unities of the product.
    """

    unities = driver.find_elements(By.XPATH, PATTERNS.unities)
    if unities:
        unities = unities[0].text
        if unities and "unité" in unities:
            unities = unities.split(" ")[0]
            unities = int(float(unities.replace(",", ".")))
            return unities
    return None


def get_review_url(driver: webdriver.Chrome) -> str | None:
    """
    Return the review url of the product.
    """

    review_url = driver.find_elements(By.XPATH, PATTERNS.review_url)
    if review_url:
        review_url = review_url[0].get_attribute("href")
        review_url = urljoin("https://www.amazon.fr", review_url)
        return review_url

    return None


class ProductItemScraper(BaseItemScraper):
    """A scraper for scraping a product pages for a specific ASIN."""

    def __init__(
        self,
        driver: SeleniumDriver,
        starting_url: str,
    ) -> None:
        super().__init__(driver, starting_url)
        self._url = starting_url

    def parse(self, url: str) -> dict:
        """
        Parses the product page and extracts relevant information.

        Args:
            url (str): The URL of the product page.

        Returns:
            dict: A dictionary containing the extracted information.
        """
        self.driver.get(url)

        if is_antirobot(self.driver):
            return {}

        item = {
            "price": get_price(self.driver),
            "brand": get_brand(self.driver),
            "avg_rating": get_avg_rating(self.driver),
            "num_reviews": get_num_reviews(self.driver),
            "feature_bullets": get_feature_bullets(self.driver),
            "unities": get_unities(self.driver),
            "review_url": get_review_url(self.driver),
        }

        return item

    def run(self) -> None:
        """
        Executes the spider and scrapes data from the starting URL.

        This method initializes the spider with the starting URL, prints the URL being updated,
        calls the `parse` method to scrape data from the URL, and extends the spider's data with the scraped item.

        Returns:
            None
        """
        url = self._starting_url
        print(f"Update {url}")
        item = self.parse(url)
        self._item = item

    def validate(self) -> bool:
        return True

    def dump(self) -> dict:
        """
        Returns the data stored in the object as a list of dictionaries.

        Returns:
            dict: The data stored in the object.
        """
        return self._item


# TODO : add test cases
class ProductPageSpiderWorker(BaseSpiderWorker):
    """
    Spider worker class for scraping product pages.

    It take a MongoDB pipeline as input for producing a list of ASINs to scrape.
    A default pipeline is provided querying all documents with status "SearchPage".

    This class inherits from the BaseSpiderWorker class and provides methods to execute the search and scraping process
    for a given query. It retrieves existing ASINs from the database, updates the internal ASIN set, constructs the search
    URL for each keyword, runs a scraper to extract ASINs and data, filters out duplicate ASINs, filters the data to include
    only the ASINs not already in the internal ASIN set, updates the database with the scraped product information, and
    prints the total number of items updated.

    Args:
        driver (SeleniumDriver): The Selenium driver instance.
        action_type (str): The type of action to perform.
        pipeline (list[dict] | None): The pipeline for querying the database collection. Defaults to None.
    """

    DEFAULT_PIPELINE = [
        {
            "$match": {
                "$and": [
                    {"_metadata.scrap_status": "SearchPage"},
                ]
            }
        },
        {"$project": {"asin": 1, "_id": 0}},
    ]

    def __init__(
        self,
        driver: SeleniumDriver,
        action_type: str,
        pipeline: list[dict] | None = None,
    ) -> None:
        super().__init__(driver, action_type)
        self._pipeline = pipeline if pipeline else self.DEFAULT_PIPELINE

    def query(self) -> None:
        """
        Queries the database collection and retrieves a list of ASINs.
        """
        asins = self.db.collection.aggregate(self._pipeline)
        self._queue = [asin["asin"] for asin in asins]

    def run(self) -> None:
        """
        Runs the scraping process for each ASIN in the queue.
        Retrieves product information, updates the database, and prints the total number of items updated.
        """

        self.query()

        for asin in self._queue:
            url = f"https://www.amazon.fr/dp/{asin}"
            scraper = ProductItemScraper(self.driver, url)
            scraper.run()
            item = scraper.dump()
            self._data.extend(item)
            # add metadata
            metadata = ItemMetadata(
                last_session_id=self.session_id,
                last_session_time=self._init_time,
                scrap_status="ProductPage",
            )
            item["asin"] = asin
            item["_metadata"] = dict(metadata)

            # update the database
            self.db.update_product(item)

        print(f"Updated {len(self._data)} items in total.")

    def log(self) -> dict:
        """
        Log the meta data.

        This method logs the meta data by adding the action time and update count to the meta dictionary.
        It then calls the `log` method of the `db` object to store the meta data in the database.

        Returns:
            dict: The updated meta dictionary.
        """
        self._meta["action_time"] = self.time
        self._meta["update_count"] = len(self._data)
        self.db.log(self._meta)
        return self._meta
