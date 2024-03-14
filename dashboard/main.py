import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Elissa",
    page_icon="🩸",
    layout="wide",
)

products = pd.read_csv("data/dashboard.csv")
products = products[products["category"].apply(lambda x: x == x)]
min_price = products["price"].min()
max_price = products["price"].max()
num_products = len(products)

CATEGORY_OPTIONS = list(products["category"].unique())
CATEGORY_DISPLAY = {
    "Tampons": "Tampons",
    "Serviettes": "Pads",
    "Coupes": "Cups",
    "Protèges-Slips": "Liners",
    "Culottes Menstruelles": "Period Underwear",
}
TAG_OPTIONS = list(
    [
        tag.replace("_score", "").capitalize()
        for tag in products.columns
        if tag.endswith("_score")
    ]
)
TAG_DISPLAY = {
    "Price": "Price",
    "Leak": "Leak-proof",
    "Absorb": "Absorbency",
    "Comfort": "Comfort",
    "Material": "Organic Material",
    "Package": "Great Packaging",
    "Size": "Size Options",
}

products_column_config = {
    "thumbnail": st.column_config.ImageColumn("Thumbnail", width="medium"),
    "asin": st.column_config.LinkColumn("Link", display_text="Link"),
    "title": "Title",
    "brand": "Brand",
    "avg_rating": "Avg. Rating",
    "num_reviews": "Num. Reviews",
    "category": "Category",
    "price": "Price",
    "unities": "Unities",
}


st.header("Project Elissa")

with st.sidebar:
    st.title("Filters")
    st.write("Use these filters to explore the products")
    category_option = st.multiselect(
        "Category",
        CATEGORY_OPTIONS,
        default=CATEGORY_OPTIONS,
        # format_func=CATEGORY_DISPLAY.get,
    )
    tags_option = st.multiselect(
        "Tags", TAG_OPTIONS, default=None, format_func=TAG_DISPLAY.get
    )
    price_range = st.slider(
        "Price Range (euros)", min_price, max_price, (min_price, max_price)
    )


df_display = products.query("category == @category_option").query(
    "price >= @price_range[0] and price <= @price_range[1]"
)
for tag in tags_option:
    df_display = df_display.query(f"{tag.lower()}_rank < (@num_products / 10)")
df_display["total_score"] = df_display[
    [f"{tag.lower()}_score" for tag in tags_option]
].mean(axis=1)
df_display["total_rank"] = df_display["total_score"].rank(ascending=False)
df_display = df_display.sort_values(
    ["num_reviews", "total_rank"], ascending=[True, False]
)

num_eligible_products = len(df_display)


col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Products", num_products)
with col2:
    st.metric("Eligible Products", num_eligible_products)
with col3:
    st.metric("Average Rating", df_display["avg_rating"].mean().__round__(2))

tab1, tab2 = st.tabs(["Card View", "Table View"])


def display_grid(df: pd.DataFrame):
    def crop_title(title, max_length=40):
        if len(title) > max_length:
            return title[:max_length] + "..."
        return title

    n = len(df)
    rows = (n + 2) // 3

    for i in range(rows):
        cols = st.columns(3)
        for j in range(3):
            df_index = i * 3 + j
            if df_index < n:
                with cols[j]:
                    with st.container(border=True, height=500):
                        st.image(df.iloc[df_index]["thumbnail"], width=200)
                        st.write(f"**{crop_title(df.iloc[df_index]['title'])}**")
                        st.link_button("Link", df.iloc[df_index]["asin"])
                        st.write(
                            f"*{df.iloc[df_index]['brand']}* - {df.iloc[df_index]['category']}"
                        )
                        st.write(f"Price: {df.iloc[df_index]['price']}€")
                        composite_score = df.iloc[df_index]["total_score"].__round__(2)
                        if composite_score is not None:
                            st.write(f"Composite Score: {composite_score}")


with tab1:
    display_grid(df_display)


with tab2:
    st.dataframe(df_display, column_config=products_column_config, hide_index=True)
