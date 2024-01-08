![CleanShot 2024-01-01 at 09 49 31](https://github.com/mintyfrankie/project-elissa/assets/77310871/b0a7f22d-da23-4b3b-84e2-419fc4b2d1ec)

<h1 align='center'> Project Elissa - Albert School </h1>

## Introduction

The repository is a monorepo for the Project Elissa. It intends to build a recommendation interface for feminine hygienic products based on their price, quality, customer reviews as well as users' preference.

**The project is for educational purposes only and is not to be used commercially. The creators accept no liability for any misuse or damages. Use at your own risk.**

## Repository Structure

```
.
├── README.md
├── mongodb/        # a client for connecting and querying to MongoDB databases
├── scraping/       # scrapers and spider workers for getting informations
├── tests/          # pytest module for testing
├── dashboard/      # a Streamlit dashboard for displaying an interface for user interaction and visualisations
├── api/            # a FastAPI module
```

## Modules

### 1. Scraping - `Selenium`

The scraping module uses `Selenium` for webdriver interactions. It contains mainly three parts:

1. `Search Page`: a spider for scraping products' ASIN from search pages given a list of keywords.
2. `Product Page`: a spider for scraping products' information from product pages given a list of ASINs.
3. `Review Page`: a spider for scraping reviews from review pages given a list of ASINs.

For each part, an `ItemScraper` is charged to scrape information around an item, and a `SpiderWorker` is charged to orchestrate the queue of `ItemScrapers`, communicate with the Database, and execute cronjob according to needs.

### 2. Data Storage - `MongoDB`

The project adopts MongoDB as the database for storing data. 

The `DatabaseClient` class in `mongodb` module is a client for connecting to MongoDB. It provides methods for inserting, updating, and querying data for the spiders.

### 3. Data Modelling

> Not Implemented

### 4. Data Visualization

> Not Implemented

### 5. APIs - `FastAPI`

> Not Implemented

### \*. Testing - `pytest`

The project uses `pytest` as the testing framework. The `tests` module contains test cases for the spiders and the database client.
