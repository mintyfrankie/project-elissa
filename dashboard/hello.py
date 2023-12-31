"""
A demo dashboard for testing purposes, with Streamlit.
"""

import pandas as pd
import streamlit as st

st.title("Project Elissa - Dashboard")

data_load_state = st.text("Loading data...")
data = pd.read_csv("./data/products.csv")
data_load_state.text("Loading data... done!")

st.subheader("Raw data")
st.write(data)
