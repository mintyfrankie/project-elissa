"""
A spider for scraping the product pages of the website.
"""

from types import SimpleNamespace

from selenium import webdriver

PATTERNS = SimpleNamespace(
    price_1="//div[@data-feature-name='corePriceDisplay_desktop']//span[contains(@class, 'aok-offscreen')]",
    price_2="//span[contains(@class, 'apexPriceToPay')]//span[@class='a-offscreen']",
    unities="//table[@id='productDetails_techSpec_section_1']//th[text()=' Unités ']/following-sibling::td",
    feature_bullets="//div[@id='feature-bullets']//span[@class='a-list-item']",
    review_url="//a[@data-hook='see-all-reviews-link-foot']",
    title_id="productTitle",
    brand_id="bylineInfo",
    rating_id="acrPopover",
    num_reviews_id="acrCustomerReviewText",
)
