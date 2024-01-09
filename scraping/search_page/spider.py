from urllib.parse import urlencode

from mongodb.interfaces import SessionLogInfo
from scraping.base import BaseItemScraper, BaseSpiderWorker
from scraping.common import (
    EXCLUDE_KEYWORDS,
    SeleniumDriver,
    is_antirobot,
    is_captcha,
    is_filtered,
    solve_captcha,
)
from scraping.interfaces import BaseItem, ItemMetadata

from .functions import get_asin_cards, get_mainframe, get_nextpage, parse_asin_card


class SearchItemScraper(BaseItemScraper):
    def __init__(
        self,
        driver: SeleniumDriver,
        starting_url: str,
        max_page: int = -1,
        asin_queue: list[str] | None = None,
    ) -> None:
        super().__init__(driver, starting_url)
        self._asins = set(asin_queue) if asin_queue else set()
        self._max_page = max_page
        self._is_antirobot = False

    def parse(self, url: str) -> dict[str, list[dict]]:
        self.driver.get(url)

        if is_antirobot(self.driver):
            print("Anti-robot check is triggered.")
            return {"is_antirobot": True}

        if is_captcha(self.driver):
            solve_captcha(self.driver)

        items = []
        main_frame = get_mainframe(self.driver)
        if main_frame == [] or main_frame is None:
            return {}

        asin_cards = get_asin_cards(main_frame)
        for asin_card in asin_cards:
            item = parse_asin_card(asin_card)
            if item["asin"] != "" and item["asin"] not in self._asins:
                if item["title"] and is_filtered(item["title"], EXCLUDE_KEYWORDS):
                    continue
                item = BaseItem(**item)
                self._asins.add(item.asin)
                items.append(item)

        next_page = get_nextpage(self.driver)

        return {"next_page": next_page, "items": items}

    def run(self) -> None:
        url = self._starting_url
        page_count = 0
        while url:
            if self._max_page != -1 and page_count >= self._max_page:
                break
            output = self.parse(url=url)
            if output.get("is_antirobot"):
                break
            items = output.get("items")
            if items:
                self._data.extend(items)
            url = output.get("next_page")
            # random_sleep(message=False)
            page_count += 1
            print(f"Scraped Page {page_count}")

    def validate(self) -> bool:
        return not self._is_antirobot

    @property
    def asins(self) -> set[str]:
        """
        Returns a set of ASINs.

        Returns:
            set[str]: A set of ASINs.
        """
        return self._asins

    def dump(self) -> list[BaseItem]:
        """
        Returns the data stored in the object as a list of dictionaries.

        Returns:
            list[dict]: The data stored in the object.
        """
        return self._data


class SearchPageSpiderWorker(BaseSpiderWorker):
    def __init__(
        self,
        driver: SeleniumDriver,
        action_type: str = "Search Page Scraping",
        queue: list[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(driver, action_type)
        self._query = queue
        self._asins = set()
        self._updated_asins = set()
        self.__kwargs = kwargs

    def query(self) -> None:
        pass

    def run(self) -> None:
        existing_asins = self.db.get_asins()
        self._asins.update(existing_asins)

        for keyword in self._query:
            url = "https://www.amazon.fr/s?" + urlencode({"k": keyword})
            print(f"Scraping Pages for Keyword: {keyword}")
            scraper = SearchItemScraper(
                driver=self.driver,
                starting_url=url,
                asin_queue=existing_asins,
                **self.__kwargs,
            )
            scraper.run()
            if not scraper.validate():
                print("Anti-robot detected, aborting...")
                break
            scaper_asins = scraper.asins
            data = scraper.dump()
            # filter only asins that are not in the asin set
            scaper_asins = [asin for asin in scaper_asins if asin not in self._asins]
            self._updated_asins.update(scaper_asins)
            self._asins.update(scaper_asins)
            # filter the data to only include the asins that are not in the asin set
            data = [item for item in data if item.asin in scaper_asins]
            self._data.extend(data)
            # update the database
            for item in data:
                # add metadata
                metadata = ItemMetadata(
                    last_session_id=self.session_id,
                    last_session_time=self._init_time,
                    scrap_status="SearchPage",
                )
                item.metadata = metadata

                self.db.update_product(item.model_dump(by_alias=True))

            print(f"Updated {len(data)} items.")

        print(f"Total Updated: {len(self._data)}")

    def log(self) -> dict:
        self._meta["update_count"] = len(self._data)
        self._meta["query_keywords"] = list(self._query)
        self._meta["updated_asins"] = list(self._updated_asins)
        info = SessionLogInfo(**self._meta)
        self.db.log(info)
        self._logged = True
        return self._meta
