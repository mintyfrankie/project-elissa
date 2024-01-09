from mongodb.interfaces import SessionLogInfo
from scraping.base import BaseItemScraper, BaseSpiderWorker
from scraping.common import (
    SeleniumDriver,
    is_antirobot,
    is_captcha,
    random_sleep,
    solve_captcha,
)
from scraping.interfaces import ItemMetadata, ProductItem
from scraping.pipelines import DEFAULT_PRODUCT_PAGE_PIPELINE

from .functions import (
    get_avg_rating,
    get_brand,
    get_category,
    get_feature_bullets,
    get_num_reviews,
    get_price,
    get_review_url,
    get_unities,
    is_target,
)


class ProductItemScraper(BaseItemScraper):
    def __init__(
        self,
        driver: SeleniumDriver,
        starting_url: str,
    ) -> None:
        super().__init__(driver, starting_url)
        self._url = starting_url
        self._is_antirobot = False
        self._to_filter = False

    def parse(self, url: str) -> dict:
        self.driver.get(url)

        if is_antirobot(self.driver):
            self._is_antirobot = True

        if is_captcha(self.driver):
            solve_captcha(self.driver)

        if not is_target(self.driver):
            self._to_filter = True

        item = {
            "price": get_price(self.driver),
            "brand": get_brand(self.driver),
            "avg_rating": get_avg_rating(self.driver),
            "num_reviews": get_num_reviews(self.driver),
            "feature_bullets": get_feature_bullets(self.driver),
            "unities": get_unities(self.driver),
            "review_url": get_review_url(self.driver),
            "category": get_category(self.driver),
        }

        return item

    def run(self) -> None:
        url = self._starting_url
        item = self.parse(url)
        self._item = item

    def validate(self) -> bool:
        return False if self._is_antirobot else True

    def dump(self) -> dict:
        """
        Returns the data stored in the object as a list of dictionaries.

        Returns:
            dict: The data stored in the object.
        """
        return self._item


class ProductPageSpiderWorker(BaseSpiderWorker):
    default_pipeline = DEFAULT_PRODUCT_PAGE_PIPELINE

    def __init__(
        self,
        driver: SeleniumDriver,
        action_type: str = "Product Page Scraping",
        pipeline: list[dict] | None = None,
    ) -> None:
        super().__init__(driver, action_type)
        self._pipeline = pipeline or self.default_pipeline

    def query(self) -> None:
        asins = self.db.collection.aggregate(self._pipeline)
        self._queue = [asin["asin"] for asin in asins]

    def run(self) -> None:
        self.query()
        if self._pipeline == self.default_pipeline:
            print("Use default pipeline to query the database.")
        print(f"Found {len(self._queue)} items to update.")

        for asin in self._queue:
            # random_sleep(message=False)
            url = f"https://www.amazon.fr/dp/{asin}"
            scraper = ProductItemScraper(self.driver, url)
            scraper.run()
            if not scraper.validate():
                print("Anti-robot detected, aborting...")
                break
            item = scraper.dump()
            item = ProductItem(**item)
            # add metadata
            item.asin = asin
            metadata = ItemMetadata(
                last_session_id=self.session_id,
                last_session_time=self._init_time,
                scrap_status="ProductPage",
            )
            item.metadata = metadata

            # update the database
            self._data.append(item)
            self.db.update_product(item.model_dump(by_alias=True))

            print(f"Updated {asin} -- Progress {len(self._data)}/{len(self._queue)}")

        print(f"Updated {len(self._data)} items in total.")

    def log(self) -> dict:
        self._meta["update_count"] = len(self._data)
        self._meta["updated_asins"] = self._queue
        info = SessionLogInfo(**self._meta)
        self.db.log(info)
        self._logged = True
        return self._meta
