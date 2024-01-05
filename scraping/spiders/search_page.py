"""
A spider for scraping the search pages of the website.
"""

from types import SimpleNamespace
from urllib.parse import urlencode, urljoin

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from scraping.base import BaseItemScraper, BaseSpiderWorker
from scraping.common import EXCLUDE_KEYWORDS, SeleniumDriver, is_antirobot, is_filtered
from scraping.interfaces import ItemMetadata

PATTERNS = SimpleNamespace(
    main_frame="//span[@data-component-type='s-search-results']",
    asins="//div[@data-asin]",
    asin_title=".//h2/a/span",
    image_url=".//img[@class='s-image']",
    pagination_next=".//a[contains(@class, 's-pagination-next')]",
)


def get_mainframe(driver: webdriver.Chrome) -> WebElement | None:
    """Get the main frame of the search page."""

    try:
        return driver.find_element(By.XPATH, PATTERNS.main_frame)
    except NoSuchElementException:
        return None


def get_asin_cards(main_frame: WebElement) -> list[WebElement]:
    """Get the ASIN cards from the main frame."""

    return main_frame.find_elements(By.XPATH, PATTERNS.asins)


def parse_asin_card(asin_card: WebElement) -> dict:
    """Parse the ASIN cards."""

    asin = asin_card.get_attribute("data-asin")
    if not asin:
        asin = ""
    try:
        title = asin_card.find_element(By.XPATH, PATTERNS.asin_title).get_attribute(
            "textContent"
        )
    except NoSuchElementException:
        title = ""

    try:
        image = asin_card.find_element(By.XPATH, PATTERNS.image_url).get_attribute(
            "src"
        )
    except NoSuchElementException:
        image = None

    output = {
        "asin": asin,
        "title": title,
        "thumbnail": image,
    }

    return output


def get_nextpage(driver: webdriver.Chrome) -> str | None:
    """
    Turn the page.
    """
    try:
        next_button = driver.find_element(By.XPATH, PATTERNS.pagination_next)
        url = urljoin("https://www.amazon.fr", next_button.get_attribute("href"))
        return url
    except NoSuchElementException:
        return None


class SearchItemScraper(BaseItemScraper):
    """A scraper for scraping a set of search pages for a specific keyword."""

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

    def parse(self, url: str) -> dict[str, list[dict]]:
        """
        Parses a search page and extracts relevant information.

        Returns:
            dict: A dictionary containing the next page URL and a list of items.
        """

        self.driver.get(url)
        print(f"##### Parsing URL: {url}")

        if is_antirobot(self.driver):
            print("Anti-robot check is triggered.")
            return {}

        items = []
        main_frame = get_mainframe(self.driver)
        if main_frame == [] or main_frame is None:
            return {}

        asin_cards = get_asin_cards(main_frame)
        for asin_card in asin_cards:
            item = parse_asin_card(asin_card)
            if item["asin"] != "" and item["asin"] not in self._asins:
                if item["title"] and is_filtered(item["title"], EXCLUDE_KEYWORDS):
                    print(f"Filtered {item['asin']}.")
                    continue
            print(f"Updated {item['asin']}.")
            self._asins.add(item["asin"])
            items.append(item)

        print(f"### Scraped {len(items)} items.")
        next_page = get_nextpage(self.driver)

        return {"next_page": next_page, "items": items}

    def run(self) -> None:
        """
        Executes the spider and collects data from the starting URL and subsequent pages.

        Returns:
            None
        """
        url = self._starting_url
        page_count = 0
        while url:
            if self._max_page != -1 and page_count >= self._max_page:
                break
            output = self.parse(url=url)
            items = output.get("items")
            self._data.extend(items) if items else None
            url = output.get("next_page")
            page_count += 1

    def validate(self) -> bool:
        """
        Validates the data.

        Returns:
            bool: True if the data is valid, False otherwise.
        """
        return True

    @property
    def asins(self) -> set[str]:
        """
        Returns a set of ASINs.

        Returns:
            set[str]: A set of ASINs.
        """
        return self._asins

    def dump(self) -> list[dict]:
        """
        Returns the data stored in the object as a list of dictionaries.

        Returns:
            list[dict]: The data stored in the object.
        """
        return self._data


class SearchPageSpiderWorker(BaseSpiderWorker):
    """
    Spider worker class for performing search and scraping on search pages given a queue of keywords.

    It will not modify any existing documents in the database. It will only add new documents.

    This class inherits from the BaseSpiderWorker class and provides methods to execute the search and scraping process
    for a given query. It retrieves existing ASINs from the database, updates the internal ASIN set, constructs the search
    URL for each keyword, runs a scraper to extract ASINs and data, filters out duplicate ASINs, filters the data to include
    only the ASINs not already in the internal ASIN set, updates the database with the scraped product information, and
    prints the total number of items updated.

    Attributes:
        driver (SeleniumDriver): The Selenium driver instance.
        action_type (str): The type of action being performed.
        queue (list[str] | None): The queue of ASINs to process.
        __kwargs: Additional keyword arguments.

    Methods:
        run(): Executes the search and scraping process for the given query.
        log(): Logs the meta data.

    """

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
        self.__kwargs = kwargs

    def query(self) -> None:
        """
        No query for this spider,
        as the queue is defined in the constructor.
        """
        pass

    def run(self) -> None:
        """
        Executes the search and scraping process for the given query.

        This method performs the following steps:
        1. Retrieves existing ASINs from the database.
        2. Updates the internal ASIN set with the existing ASINs.
        3. Iterates over each keyword in the query.
        4. Constructs the search URL for the keyword.
        5. Initializes a SearchItemScraper with the driver, URL, and existing ASINs.
        6. Runs the scraper to extract ASINs and data.
        7. Filters out duplicate ASINs from the scraper results.
        8. Filters the data to include only the ASINs not already in the internal ASIN set.
        9. Appends the filtered data to the internal data list.
        10. Updates the database with the scraped product information.
        11. Prints the total number of items updated.

        Returns:
            None
        """
        existing_asins = self.db.get_asins()
        self._asins.update(existing_asins)

        for keyword in self._query:
            url = "https://www.amazon.fr/s?" + urlencode({"k": keyword})
            scraper = SearchItemScraper(
                driver=self.driver,
                starting_url=url,
                asin_queue=existing_asins,
                **self.__kwargs,
            )
            scraper.run()
            scaper_asins = scraper.asins
            data = scraper.dump()
            # filter only asins that are not in the asin set
            scaper_asins = [asin for asin in scaper_asins if asin not in self._asins]
            self._asins.update(scaper_asins)
            # filter the data to only include the asins that are not in the asin set
            data = [item for item in data if item["asin"] in scaper_asins]
            self._data.extend(data)
            # update the database
            for item in data:
                # add metadata
                metadata = ItemMetadata(
                    last_session_id=self.session_id,
                    last_session_time=self._init_time,
                    scrap_status="SearchPage",
                )
                item["_metadata"] = metadata

                self.db.update_product(item)

        print(f"Updated {len(self._data)} items in total.")

    def log(self) -> dict:
        """
        Log the meta data.

        This method logs the meta data by adding the action time, update count, and query keywords to the meta dictionary.
        It then calls the `log` method of the `db` object to store the meta data in the database.

        Returns:
            dict: The updated meta dictionary.
        """
        self._meta["action_time"] = self.time
        self._meta["update_count"] = len(self._data)
        self._meta["query_keywords"] = list(self._query)
        self.db.log(self._meta)
        return self._meta
