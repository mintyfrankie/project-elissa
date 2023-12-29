"""
A spider for scraping the product pages of the website.
"""

from types import SimpleNamespace
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By

PATTERNS = SimpleNamespace(
    price_1="//span[contains(@class, 'apexPriceToPay')]//span[@class='a-offscreen']",
    price_2="//div[@data-feature-name='corePriceDisplay_desktop']//span[contains(@class, 'aok-offscreen')]",
    unities="//table[@id='productDetails_techSpec_section_1']//th[text()=' Unités ']/following-sibling::td",
    feature_bullets="//div[@id='feature-bullets']//span[@class='a-list-item']",
    review_url="//a[@data-hook='see-all-reviews-link-foot']",
    title_id="productTitle",
    brand_id="bylineInfo",
    rating_id="acrPopover",
    num_reviews_id="acrCustomerReviewText",
)


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

    return None


def get_title(driver: webdriver.Chrome) -> str | None:
    """
    Return the title of the product.
    """

    title = driver.find_elements(By.ID, PATTERNS.title_id)
    if title:
        return title[0].get_attribute("textContent")

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
        feature_bullets = [bullet for bullet in feature_bullets if bullet]
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
