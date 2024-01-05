![CleanShot 2024-01-01 at 09 49 31](https://github.com/mintyfrankie/project-elissa/assets/77310871/b0a7f22d-da23-4b3b-84e2-419fc4b2d1ec)

<h1 align='center'> Project Elissa - Albert School </h1>

## Introduction

The repository is a monorepo for the Project Elissa. It intends to build a recommendation interface for feminine hygienic products based on their price, quality, customer reviews as well as users' preference.

**The project is for educational purposes only and is not to be used commercially. The creators accept no liability for any misuse or damages. Use at your own risk.**

## Repository Structure

```
.
├── README.md
├── mongodb/        # a Client for connecting to mongodb
├── scraping/       # three Spiders for scraping data from websites
├── tests/          # pytest module for testing
├── scripts/        # some handy scripts for DevOps
├── deepnote/       # related jupyter notebooks hosted on Deepnote
├── dashboard/
├── api/
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

> Not Implemented

### 4. Data Visualization

> Not Implemented

### 5. Dashboarding and APIs

> Not Implemented

### \*. Testing

The project uses `pytest` as the testing framework. The `tests` module contains test cases for the spiders and the database client.

## TODO

- [ ] Setup devcontainer with selenium and chrome
- [ ] Find ways to exclude irrelevant products in the database
- [ ] For reviews, it lacks the rating and title for reviews outside of France. Need to find a way to get them.
- [ ] Enforce Pydantic models across modules
