"""
A demo dashboard for testing purposes, with Streamlit.
"""

import pandas as pd
import streamlit as st


@st.cache_data
def load_products():
    return pd.read_csv("./data/products.csv")


@st.cache_data
def load_reviews():
    return pd.read_csv("./data/reviews.csv")


with st.sidebar:
    st.title("Project Elissa")
    st.subheader("Navigation")
    st.markdown(
        """
        - [Dashboard](/dashboard)
        - [Recommender](/recommender)
        - [About](/about)
        """
    )

st.title("Dashboard")

products = load_products()
reviews = load_reviews()

with st.container(border=True):
    st.header("Metrics")
    col1, col2 = st.columns(2)
    col1.metric(label="Scraped Products", value=products.shape[0])
    col2.metric(label="Scraped reviews", value=reviews.shape[0])

with st.container(border=False):
    st.header("Products")
    st.dataframe(products)

with st.container(border=False):
    st.header("Reviews")
    st.dataframe(reviews)
