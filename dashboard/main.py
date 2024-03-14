import pandas as pd
import streamlit as st
from st_pages import Page, add_page_title, show_pages

st.set_page_config(
    page_title="Elissa",
    page_icon="🩸",
    layout="wide",
)
show_pages(
    [
        Page("dashboard/main.py", "Home", "🏠"),
        Page("dashboard/pages/engine.py", "Searching Engine", "🔧"),
        Page("dashboard/pages/visualization.py", "Visualization", "📊"),
    ]
)

add_page_title()

st.image(
    "https://github.com/mintyfrankie/project-elissa/assets/77310871/b0a7f22d-da23-4b3b-84e2-419fc4b2d1ec"
)

st.markdown(
    """

# Project Elissa - Albert School

## Introduction

The repository is a monorepo for the Project Elissa. It intends to build a recommendation interface for feminine hygienic products based on their price, quality, customer reviews as well as users' preference. Based on the information and reviews scraped on an e-Commerce website, we proceed to analyse the documents with Natural Language Processing in order to gather users' opinion around a feminin hygenic product. 

**The project is for educational purposes only and is not to be used commercially. The creators accept no liability for any misuse or damages. Use at your own risk.**

1. **Project Objectives**
Our mission is to empower individuals by providing them with informed choices regarding menstrual products. Recognizing the existing lack of comprehensive information, we leverage cutting-edge technology, including scraping, machine learning, APIs, and data visualization, to create a personalized platform. We aim to enhance user well-being by offering a seamless experience, allowing users to select menstrual products aligned with their preferences, health needs, and budget. Through innovation and user-centric design, our goal is to revolutionize the menstrual product landscape, fostering a community of individuals who make confident and conscious choices for their menstrual health.

2. **Key Stats and Context**
The composition of menstrual pads includes dioxins, perfume additives, oils, alcohols, aluminum, pesticide residue, halogenated derivatives residue, and endocrine disruptors. Examining French women's product usage, we find that sanitary towels are the most commonly used (41%), followed by single-use tampons (24%), menstrual panties (11%), menstrual cups (10%), washable sanitary towels (7%), and other options like toilet paper, free-flow instances, etc. Key statistics indicate that Period Poverty affected 4 million people in 2022 (up from 2 million in 2021), and that menstrual protection constitutes 13% of household waste. France has announced free menstrual products for women under 25, following the footsteps of Scotland (2020) and Britain (2021). Challenges in menstrual product accessibility in France include the limitation of free products until the age of 25, the exclusion of pain medication, and the implementation of EU - Ecolabel criteria for reusable products with a focus on reducing single-use plastics and toxins.

3. **Methodology**
Our project commenced with a comprehensive market analysis, identifying the lack of information on the environmental impact and health implications of menstrual products. To address this, we initiated the project by scraping data, training a machine learning algorithm, answering business needs, and creating an API. We focused on menstrual pads, tampons, menstrual cups, and menstrual underwear. The primary issues addressed were the lack of clarity on suitable products, the environmental impact of menstrual waste, and the hidden health consequences associated with using unsuitable products.

"""
)
