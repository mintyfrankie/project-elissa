"""
A spider for scraping the product pages of the website.
"""

from types import SimpleNamespace
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By

from scraping.base import BaseItemScraper, BaseSpiderWorker
from scraping.common import SeleniumDriver, is_antirobot
from scraping.utils.items import ItemMetadata
from scraping.utils.spiders import BaseSpider

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
        self._data.extend(item)

    def validate(self) -> bool:
        return True

    def dump(self) -> list[dict]:
        return super().dump()


# TODO : finish this
class ProductPageSpiderWorker(BaseSpiderWorker):
    # TODO: reflect on how to implement the pipeline and metadata update function
    pass


# ! : to be removed in future iterations
class ProductPageSpider(BaseSpider):
    """
    A spider for scraping the product pages of the website.
    """

    default_pipeline = [
        {"$match": {"product_page_scraped": False}},
        {"$project": {"asin": 1, "_id": 0}},
    ]

    def __init__(self, driver: webdriver.Chrome) -> None:
        super().__init__(driver)
        self.queue = []
        self.logs = []

    def parse(self, url: str) -> dict:
        """
        Parse the product page.
        """

        self.driver.get(url)

        if is_antirobot(self.driver):
            print("Anti-robot detected.")
            self.logs.append({"url": self.driver.current_url, "status": "Anti-robot"})
            return {}

        product = {
            "price": get_price(self.driver),
            # "title": get_title(self.driver),
            "brand": get_brand(self.driver),
            "avg_rating": get_avg_rating(self.driver),
            "num_reviews": get_num_reviews(self.driver),
            "feature_bullets": get_feature_bullets(self.driver),
            "unities": get_unities(self.driver),
            "review_url": get_review_url(self.driver),
        }

        return product

    def query(self, pipeline: list[dict] = default_pipeline) -> list[str]:
        """
        Get the products to scrape.
        """

        items = list(self.mongodb.collection.aggregate(pipeline))
        items = [doc["asin"] for doc in items]
        self.queue = items
        print(f"Found {len(items)} products to scrape.")
        return items

    def run(self) -> None:
        """
        Execute the spider.
        """

        if not self.queue:
            raise ValueError("No products to scrape, run query() first.")

        def process_item(asin: str) -> int:
            url = f"https://www.amazon.fr/dp/{asin}"
            product = self.parse(url)
            output: ItemMetadata = {
                "last_session_id": self.session_id,
                "last_session_time": self.strtime,
                "product_page_scraped": True,
                "review_page_scraped": False,
            }
            product["_metadata"] = output
            self.mongodb.collection.update_one(
                {"asin": asin},
                {"$set": product},
            )
            return 1

        counter = 0
        for asin in self.queue:
            counter += process_item(asin)
            print(f"Updated {asin} --- Progress {counter}/{len(self.queue)}")

        # Log the session.
        ACTION_TYPE = "Product Page Scraping"

        self.meta["action_type"] = ACTION_TYPE
        self.meta["action_time"] = self.time
        self.meta["update_count"] = counter
        self.meta["anomalies"] = self.logs

        print(f"Scraped {counter} products.")
        self.log()
        self.driver.quit()
