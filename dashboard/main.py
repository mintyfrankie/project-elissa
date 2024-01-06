"""
A demo dashboard for testing purposes, with Streamlit.

TODO:
- [ ] Implement database connection for querying real products
"""

import streamlit as st

CATEGORIES = ("Tampon", "Serviette", "Cup", "Culotte", "Protège-slip", "Autre")
FEATURES = ("Confort", "Écologie", "Absorption", "Prix", "Praticité", "Autre")

with st.sidebar:
    st.subheader("Category")
    category_option = st.radio("Select a category", CATEGORIES, horizontal=True)

    st.subheader("Features")
    features_option = st.multiselect("Select features", FEATURES)

    with st.container():
        st.subheader("Price range")
        price_range = st.slider("Select a price range", 0, 100, (25, 75))


def product_card():
    with st.container(border=True) as card:
        st.image("https://m.media-amazon.com/images/I/81mAiEAY81L._AC_UL320_.jpg")
        st.write(
            "Nana Dailies Style Protège-Lingerie Multistyle - Protège-Slip Fin et Ultra-Absorbant pour Tous Types de Lingerie - 30 en Pochette Individuelle"
        )
        st.write("Évaluation : 4.4 / 5 -- 806 avis")
        st.write("Prix : 1,73€")
        st.write("Tags : Confort, Praticité, Prix")
        return card


st.subheader("Presentation Example")
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        product_card()
    with col2:
        product_card()
    with col3:
        product_card()
    with col4:
        product_card()
