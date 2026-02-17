# -------------------------
# Import packages
# -------------------------
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd


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
fruit_df = session.table("smoothies.public.fruit_options").select(col("fruit_name"),col('SEARCH_ON'))
fruit_rows = fruit_df.collect()
fruit_list = [row["SEARCH_ON"] for row in fruit_rows]

# Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC funtion
pd_df=fruit_df.to_pandas
st.dataframe(pd_df)
st.stop()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# -------------------------
# Insert order into Snowflake
# -------------------------
if ingredients_list and name_on_order:  # proceed only if user filled both
    ingredients_string = " ".join(ingredients_list)

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + " " + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    
    if st.button("Submit Order"):
        # Insert into Snowflake safely using parameter binding
        # ORDER_UID is numeric auto-generated
        # ORDER_TS uses column default CURRENT_TIMESTAMP
        session.sql(
            """
            INSERT INTO smoothies.public.orders (
                ORDER_FILLED,
                NAME_ON_ORDER,
                INGREDIENTS
            ) VALUES (?, ?, ?)
            """,
            params=[
                False,              # ORDER_FILLED
                name_on_order,      # NAME_ON_ORDER
                ingredients_string  # INGREDIENTS
            ]
        ).collect()

        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

elif ingredients_list and not name_on_order:
    st.warning("Please enter a name for your Smoothie before submitting!")







