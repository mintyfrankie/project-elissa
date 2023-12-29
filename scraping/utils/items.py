"""
Identify the fields for the items
"""

from typing import NotRequired, TypedDict


class SearchItem(TypedDict):
    """Search item"""

    asin: str
    title: str | None
    image_url: str | None
    metadata: NotRequired[dict]


class ProductItem(TypedDict):

    """
    A product on Amazon.
    """

    asin: str
    title: str
    brand: str
    price: float | None
    unities: float | None
    avg_rating: float | None
    num_reviews: int | None
    features_bullets: list[str] | None
    image_url: str
    review_url: str | None


class ReviewItem(TypedDict):
    """
    A review on Amazon.
    """

    asin: str
    rating: int | None
    title: str | None
    content: str | None
    metadata: str | None
