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
fruit_df = session.table("smoothies.public.fruit_options").select(col("fruit_name"),col('SEARCH_ON'))
fruit_rows = fruit_df.collect()
fruit_list = [row["SEARCH_ON"] for row in fruit_rows]

# Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC funtion
#pd_df=fruit_df.to_pandas()
pd_df=fruit_df.to_pandas()
st.dataframe(pd_df)


# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# -------------------------
# Insert order into Snowflake
# -------------------------

if ingredients_list and name_on_order:

    ingredients_string = " ".join(ingredients_list)

    for fruit_name in ingredients_list:

        st.subheader(f"{fruit_name} Nutrition Information")

        # Match on SEARCH_ON since that's what your multiselect uses
        filtered = pd_df.loc[
            pd_df['SEARCH_ON'] == fruit_name,
            'SEARCH_ON'
        ]

        if not filtered.empty:
            search_on = filtered.iloc[0]
            st.write('The search value for', fruit_name, 'is', search_on)

            smoothiefroot_response = requests.get(
                "https://my.smoothiefroot.com/api/fruit/" + search_on
            )

            st.dataframe(
                data=smoothiefroot_response.json(),
                use_container_width=True
            )

        else:
            st.write('No matching fruit found for', fruit_name)

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




