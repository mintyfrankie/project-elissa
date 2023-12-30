"""
Identify the fields for the items
"""

from typing import NotRequired, TypedDict


class ItemMetadata(TypedDict):
    """Item metadata"""

    last_session_id: int
    last_session_time: str
    product_page_scraped: bool
    review_page_scraped: bool


class SearchItem(TypedDict):
    """Search item"""

    _metadata: ItemMetadata
    asin: str
    title: str | None
    thumbnail: str | None


class ProductItem(TypedDict):

    """
    A product on Amazon.
    """

    _metadata: ItemMetadata
    asin: str
    title: str
    brand: str
    thumbnail: str
    price: float | None
    unities: float | None
    avg_rating: float | None
    num_reviews: int | None
    features_bullets: list[str] | None
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


class SessionLogInfo(TypedDict):
    """A session log info."""

    action_type: str
    action_time: int
    update_count: int
    query_keywords: NotRequired[list[str]]


class SessionLog(TypedDict):
    """A session log."""

    id: int
    time: str
    info: SessionLogInfo | dict
