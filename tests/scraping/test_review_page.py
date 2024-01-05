"""
Test the ReviewPageSpider.
"""


from scraping.spiders.review_page import (
    ReviewItemScraper,
    ReviewPageSpiderWorker,
    get_body,
    get_metadata,
    get_next_page,
    get_rating,
    get_review_cards,
    get_title,
)


class TestReviewPageFunctions:
    """Test the ReviewPageSpider."""

    def test_get_review_cards(self, review_page):
        """Test if the review cards are found."""
        review_cards = get_review_cards(review_page)
        assert review_cards, "Review cards are not found"

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
        assert (
            next_page != review_page.current_url
        ), "Next page is the same as current page"
        assert isinstance(next_page, str), "Next page is not a string"


def test_ReviewItemScraper(driver):
    """Test the ReviewItemScraper."""
    scraper = ReviewItemScraper(
        driver=driver,
        starting_url="https://www.amazon.fr/Nana-Goodnight-Serviettes-Hygi%C3%A9niques-Ailettes/product-reviews/B09WBF4NYJ/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews",
        max_page=1,
    )
    scraper.run()
    data = scraper.dump()
    assert len(data) > 0, "No data is scraped"
    assert scraper.validate(), "Data is not validated"


def test_ReviewPageSpiderWorker(driver):
    """Test the ReviewPageSpiderWorker."""
    try:
        pipeline = [
            {"$match": {"asin": "B082VVRKTP"}},
            {"$project": {"asin": 1, "_id": 0, "review_url": 1}},
        ]
        with ReviewPageSpiderWorker(
            driver=driver,
            action_type="Testing - pytest test_ReviewPageSpiderWorker",
            pipeline=pipeline,
            max_page=1,
        ) as worker:
            worker.run()
    except Exception as e:
        assert False, f"Exception raised: {e}"
