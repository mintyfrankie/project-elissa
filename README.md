![CleanShot 2024-01-01 at 09 49 31](https://github.com/mintyfrankie/project-elissa/assets/77310871/b0a7f22d-da23-4b3b-84e2-419fc4b2d1ec)

<h1 align='center'> Project Elissa - Albert School </h1>

## Introduction

This project is for the course Hands-on Data for Startup Cases. It intends to build a recommendation system for feminine hygienic products based on their reviews, price, quality as well as users' preference. 

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
- [ ] For reviews, it lacks the rating and title for reviews outside of France. Need to find a way to get them.
