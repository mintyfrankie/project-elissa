"""
A demo dashboard for testing purposes, with Streamlit.

TODO:
- [ ] Implement database connection for querying real products
"""

import streamlit as st


def product_card():
    with st.container(border=True) as card:
        st.image("https://m.media-amazon.com/images/I/81mAiEAY81L._AC_UL320_.jpg")
        st.subheader("Nana Dailies Style Protège-Lingerie Multistyle...")
        st.write("*Évaluation : 4.4 / 5 -- 806 avis*")
        st.write("*Prix : 1,73€*")
        st.write("*Tags : Confort, Praticité, Prix*")
        return card


CATEGORIES = ("Tampon", "Serviette", "Cup", "Culotte", "Protège-slip", "Autre")
FEATURES = ("Confort", "Écologie", "Absorption", "Prix", "Praticité", "Autre")

st.header("Project Elissa")

st.empty()


st.subheader("Query", divider=True)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        category_option = st.radio("Category", CATEGORIES, horizontal=True)

        features_option = st.multiselect("Features", FEATURES)

    with col2:
        price_range = st.slider("Price range", 0, 100, (25, 75))


st.subheader("Result", divider=False)

tab1, tab2 = st.tabs(["Cards", "Table"])

with tab1:
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            product_card()
        with col2:
            product_card()
        with col3:
            product_card()

with tab2:
    pass
