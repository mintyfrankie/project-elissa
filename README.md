# Project Elissa

## Introduction

## Repository Structure

```
.
├── README.md
├── mongodb/        # a Client for connecting to mongodb
├── scraping/       # three Spiders for scraping data from websites
├── tests/          # pytest module for testing
```

## Modules

### 1. Scraping

The project contains three dedicated spiders based on Selenium and headless Chrome for scraping data from websites. These spiders include:

1. `SearchPageSpider`: a spider for scraping products' ASIN from search pages given a list of keywords.
2. `ProductPageSpider`: a spider for scraping products' information from product pages given a list of ASINs.
3. `ReviewPageSpider`: a spider for scraping reviews from review pages given a list of ASINs.

### 2. Data Storage

The project adopts MongoDB as the database for storing data. The `DatabaseClient` class in `mongodb` module is a client for connecting to MongoDB. It provides methods for inserting, updating, and querying data for the spiders.

### 3. Data Modelling

> NotImplemented

### 4. Data Visualization

> NotImplemented

### 5. Dashboarding and APIs

> NotImplemented

### \*. Testing

The project uses `pytest` as the testing framework. The `tests` module contains test cases for the spiders and the database client.

## TODO

- [ ] Setup devcontainer with selenium and chrome
- [ ] Find ways to exclude irrelevant products in the database
