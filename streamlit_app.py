# -------------------------
# Import packages
# -------------------------
import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import requests


# -------------------------
# Streamlit UI
# -------------------------
st.title("Customize Your Smoothie! :cup_with_straw:")
st.write("**Choose the fruits you want in your custom Smoothie!**")

# User input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# -------------------------
# Snowflake session
# -------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit list from Snowflake table
fruit_df = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))

pd_df = fruit_df.to_pandas()

# Create mapping dictionary (FRUIT_NAME -> SEARCH_ON)
fruit_map = dict(zip(pd_df["FRUIT_NAME"], pd_df["SEARCH_ON"]))

# Multiselect shows ONLY FRUIT_NAME
fruit_display_list = pd_df["FRUIT_NAME"].tolist()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_display_list,
    max_selections=5
)

# -------------------------
# Insert order into Snowflake
# -------------------------

if ingredients_list and name_on_order:

    ingredients_string = " ".join(ingredients_list)

    for fruit in ingredients_list:

        # Get SEARCH_ON value behind the scenes
        search_on = fruit_map.get(fruit)

        st.subheader(f"{fruit} Nutrition Information")

        try:
            response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )

            if response.status_code == 200:
                st.dataframe(
                    data=response.json(),
                    use_container_width=True
                )
            else:
                st.error(f"API returned status {response.status_code}")

        except Exception as e:
            st.error(f"Error calling API: {e}")

    if st.button("Submit Order"):
        session.sql(
            """
            INSERT INTO smoothies.public.orders (
                ORDER_FILLED,
                NAME_ON_ORDER,
                INGREDIENTS
            ) VALUES (?, ?, ?)
            """,
            params=[
                False,
                name_on_order,
                ingredients_string
            ]
        ).collect()

        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

elif ingredients_list and not name_on_order:
    st.warning("Please enter a name for your Smoothie before submitting!")




