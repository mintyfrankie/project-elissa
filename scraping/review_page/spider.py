"""
Define the ReviewItemScraper and ReviewPageSpiderWorker class.
"""

from mongodb.interfaces import SessionLogInfo
from scraping.base import BaseItemScraper, BaseSpiderWorker
from scraping.common import (
    SeleniumDriver,
    is_antirobot,
    is_captcha,
    random_sleep,
    solve_captcha,
)
from scraping.interfaces import ItemMetadata
from scraping.pipelines import DEFAULT_REVIEW_PAGE_PIPELINE

from .functions import (
    get_body,
    get_metadata,
    get_next_page,
    get_rating,
    get_review_cards,
    get_title,
)


class ReviewItemScraper(BaseItemScraper):
    """
    A scraper for scraping all review pages for an ASIN.
    """

    def __init__(
        self, driver: SeleniumDriver, starting_url: str, max_page: int = -1
    ) -> None:
        super().__init__(driver, starting_url)
        self._max_page = max_page
        self._is_anti_robot = False

    def parse(self, url: str) -> dict[str, list[str]]:
        """Parse a review page by its url, return data and next page url."""

        self.driver.get(url)

        if is_antirobot(self.driver):
            self._is_anti_robot = True
            return {"is_antirobot": True}

        if is_captcha(self.driver):
            solve_captcha(self.driver)

        review_cards = get_review_cards(self.driver)
        next_page = get_next_page(self.driver)
        items = []
        if review_cards:
            for review_card in review_cards:
                item = {}
                metadata = get_metadata(review_card)
                item["rating"] = get_rating(review_card)
                item["title"] = get_title(review_card)
                item["country"] = None
                item["date"] = None
                item["body"] = get_body(review_card)
                if metadata:
                    item["country"], item["date"] = metadata
                items.append(item)

        return {"next_page": next_page, "items": items}

    def run(self) -> None:
        """Run the scraper that scrapes all review pages for an ASIN."""

        url = self._starting_url
        page_count = 0
        while url and (self._max_page == -1 or page_count < self._max_page):
            output = self.parse(url)
            if output.get("is_antirobot"):
                self._is_anti_robot = True
                break
            items = output.get("items")
            if items:
                self._data.extend(items)
            url = output.get("next_page")
            page_count += 1
            print(f"Scraped Page {page_count}")
            # random_sleep(0.1, 0.9)

    def validate(self) -> bool:
        """Validate the operation, if anti-robot is not detected"""

        return not self._is_anti_robot

    def dump(self) -> list[dict]:
        """Dump the data."""

        return self._data


class ReviewPageSpiderWorker(BaseSpiderWorker):
    """
    A spider worker for scraping all review pages for a list of ASINs.
    """

    default_pipeline = DEFAULT_REVIEW_PAGE_PIPELINE

    def __init__(
        self,
        driver: SeleniumDriver,
        action_type: str = "Review Page Scraping",
        pipeline: list[dict] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(driver, action_type)
        self._pipeline = pipeline or self.default_pipeline
        self.__kwargs = kwargs
        self._queue = None

    def query(self) -> None:
        """Query the database for ASINs to update."""

        asins = list(self.db.collection.aggregate(self._pipeline))
        self._queue = asins

    def run(self) -> None:
        """Run the scraper that can iterate over a list of ASINs."""

        self.query()
        if self._pipeline == self.default_pipeline:
            print("Use default pipeline to query the database.")
        print(f"Found {len(self._queue)} items to update.")

        for elem in self._queue:
            asin = elem.get("asin")
            url = elem.get("review_url")
            scraper = ReviewItemScraper(self.driver, url, **self.__kwargs)
            print(f"Scraping reviews for Product: {asin}")
            scraper.run()
            if not scraper.validate():
                print("Anti-robot detected, aborting...")
                break
            items = scraper.dump()
            elem["reviews"] = items
            # add metadata
            metadata = ItemMetadata(
                last_session_id=self.session_id,
                last_session_time=self._init_time,
                scrap_status="ReviewPage",
            )
            elem["_metadata"] = dict(metadata)

            self._data.append(elem)
            self.db.update_product(elem)
            print(f"Updated {asin} -- Progress {len(self._data)}/{len(self._queue)}")

        print(f"Updated {len(self._data)} items in total.")

    def log(self) -> dict:
        """Log the session information."""

        self._meta["update_count"] = len(self._data)
        self._meta["updated_asins"] = list(self._queue)
        info = SessionLogInfo(**self._meta)
        self.db.log(info)
        return self._meta
