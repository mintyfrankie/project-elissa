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

## Architecture

<div align='center'>
  <img width="3312" alt="Project Elissa - Architecture" src="https://github.com/mintyfrankie/project-elissa/assets/77310871/98c941a1-bd06-44bf-85c4-d7c29b299e1c">
  <em align='center'>Project's Schema</em>
</div>

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

1. **Labels definition** : use of LDA to point out the most common words and subjects

2. **Tokenization** : Dependency parsing using spacy, so we can get more than one sentiment per review.

3. **Linguistic analysis** : for a span to have a positive label there are two conditions, it needs to contain a predefined keyword and be associated by a neutral or positive sentiment. We included the neutral sentiment because some comments not being "positive enough" for the algortihm like "confortable et agréable" were identified as neutral when they were positive. On the other hand, for a span to be categorized under a negative label the conditions are that it needs to be associated with an obvious negative sentiment AND must contain a negative keyword.

4. **Score per product** : then we grouped the dataset by asin (product) keeping the sum of positive and negative reviews for each label, as well as the total number of reviews per product.



### 4. Data Visualization

> Not Implemented

### 5. APIs - `FastAPI`

> Not Implemented

### \*. Testing - `pytest`

The project uses `pytest` as the testing framework. The `tests` module contains test cases for the spiders and the database client.
