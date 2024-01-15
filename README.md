![CleanShot 2024-01-01 at 09 49 31](https://github.com/mintyfrankie/project-elissa/assets/77310871/b0a7f22d-da23-4b3b-84e2-419fc4b2d1ec)

<h1 align='center'> Project Elissa - Albert School </h1>

## Introduction

The repository is a monorepo for the Project Elissa. It intends to build a recommendation interface for feminine hygienic products based on their price, quality, customer reviews as well as users' preference. Based on the information and reviews scraped on an e-Commerce website, we proceed to analyse the documents with Natural Language Processing in order to gather users' opinion around a feminin hygenic product. 

**The project is for educational purposes only and is not to be used commercially. The creators accept no liability for any misuse or damages. Use at your own risk.**

1. **Project Objectives**
Our mission is to empower individuals by providing them with informed choices regarding menstrual products. Recognizing the existing lack of comprehensive information, we leverage cutting-edge technology, including scraping, machine learning, APIs, and data visualization, to create a personalized platform. We aim to enhance user well-being by offering a seamless experience, allowing users to select menstrual products aligned with their preferences, health needs, and budget. Through innovation and user-centric design, our goal is to revolutionize the menstrual product landscape, fostering a community of individuals who make confident and conscious choices for their menstrual health.

2. **Key Stats and Context**
The composition of menstrual pads includes dioxins, perfume additives, oils, alcohols, aluminum, pesticide residue, halogenated derivatives residue, and endocrine disruptors. Examining French women's product usage, we find that sanitary towels are the most commonly used (41%), followed by single-use tampons (24%), menstrual panties (11%), menstrual cups (10%), washable sanitary towels (7%), and other options like toilet paper, free-flow instances, etc. Key statistics indicate that Period Poverty affected 4 million people in 2022 (up from 2 million in 2021), and that menstrual protection constitutes 13% of household waste. France has announced free menstrual products for women under 25, following the footsteps of Scotland (2020) and Britain (2021). Challenges in menstrual product accessibility in France include the limitation of free products until the age of 25, the exclusion of pain medication, and the implementation of EU - Ecolabel criteria for reusable products with a focus on reducing single-use plastics and toxins.

3. **Methodology (Elissa)**
Our project commenced with a comprehensive market analysis, identifying the lack of information on the environmental impact and health implications of menstrual products. To address this, we initiated the project by scraping data, training a machine learning algorithm, answering business needs, and creating an API. We focused on menstrual pads, tampons, menstrual cups, and menstrual underwear. The primary issues addressed were the lack of clarity on suitable products, the environmental impact of menstrual waste, and the hidden health consequences associated with using unsuitable products.

## Repository Structure

```
.
├── README.md
├── mongodb/        # a client for connecting and querying to MongoDB databases
├── scraping/       # scrapers and spider workers for getting informations
├── tests/          # pytest module for testing
├── visualisation/  # a Jupyter notebook for analysing and visualising our output
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

### 3. Data Mining - Natrual Language Processing on Reviews

Based on the available data, we proceed with the folloing steps for leveraging the Natural Langauge Processing techniques.

1. **Aspect Definition**: We conduct a Theme Modeling with Latent Dirichlet Allocation (LDA) for find out the most important themes and their related keywords in the reviews corpus.

2. **Keywords Extraction**: With each of the aspect pre-defined from the aspects extracted from the previous theme modeling, we apply the TF-IDF Vectorizer algorithm to find out the most relevant and recurrent keywords around each aspect.

3. **Linguistic analysis** : for a span to have a positive label there are two conditions, it needs to contain a predefined keyword and be associated by a neutral or positive sentiment. We included the neutral sentiment because some comments not being "positive enough" for the algortihm like "confortable et agréable" were identified as neutral when they were positive. On the other hand, for a span to be categorized under a negative label the conditions are that it needs to be associated with an obvious negative sentiment AND must contain a negative keyword.

4. **Score per product** : then we grouped the dataset by asin (product) keeping the sum of positive and negative reviews for each label, as well as the total number of reviews per product.


### 4. Data Visualization

In our comprehensive analysis of menstrual products sourced from the e-commerce website, we aimed to unravel valuable insights by examining various aspects such as product categories, customer reviews, countries of sale, and other pertinent variables. Through a systematic exploration, we sought to achieve three primary objectives:

**1.⁠ ⁠Identifying the Most Relevant Product Categories**

Our initial exploration focused on discerning the product categories with the greatest diversity. Tampons as the singular product with the highest variety. Pads and other singular-use products emerge as the second most varied category, while reusable products like cups and menstrual underwear exhibit the least variety. This analysis provides a foundation for understanding the landscape of available menstrual products.

**2. Analyzing Consumer Interest Through Reviews**

To delve into consumer interest and preferences, we conducted an in-depth analysis of keywords prevalent in product reviews. 

**3.⁠ ⁠Evaluating Product Performance and Consumer Sentiment**

We delved into the top 10 products in each category, considering the average review score. Additionally, we explore the differences in ratings between reusable and non-reusable products, providing valuable insights into consumer satisfaction.

These analyses collectively aim to unravel the intricate dynamics surrounding menstrual products, offering nuanced perspectives on consumer preferences, product performance, and potential biases in the data. By combining data scraping, machine learning, and visualizations, our objective is to empower individuals with informed choices regarding menstrual products, fostering a community of conscious and confident decision-makers for their menstrual health.

### 5. APIs - `FastAPI`

The module of API built with `FastAPI` prodives some entry points for querying and updating products and submitting process request on new products based on their ASINs. Basic API-Key authentication as well as query parameters validation have been implemented.

### \*. Testing - `pytest`

The project uses `pytest` as the testing framework. The `tests` module contains test cases for the spiders and the database client.
