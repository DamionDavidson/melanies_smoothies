# -------------------------
# Import packages
# -------------------------
import streamlit as st
from snowflake.snowpark.functions import col

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
fruit_df = session.table("smoothies.public.fruit_options").select(col("fruit_name"))
fruit_rows = fruit_df.collect()
fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

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


