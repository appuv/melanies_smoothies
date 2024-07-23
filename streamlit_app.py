# Import Python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Customize Your Smoothie :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)

# User input for name on order
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be: ", name_on_order)

try:
    # Establish connection to Snowflake (assuming st.connection is correctly defined)
    cnx = st.connection("snowflake")
    session = cnx.session()

    # Retrieve fruit options from Snowflake
    my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

    # Multi-select for choosing ingredients
    ingredients_list = st.multiselect('Choose up to 5 ingredients:', my_dataframe, max_selections=5)

    # Process ingredients selection
    if ingredients_list:
        ingredients_string = ' '.join(ingredients_list)  # Join selected ingredients into a single string
        for fruit_chosen in ingredients_list:
            try:
                # Make API request to get details about each fruit
                fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
                fruityvice_response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
                
                if fruityvice_response.status_code == 200:
                    fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
                else:
                    st.warning(f"Failed to fetch details for {fruit_chosen}")
            
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to fetch details for {fruit_chosen}: {str(e)}")

        # SQL statement to insert order into database (assuming proper handling of SQL injection risk)
        my_insert_stmt = """INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                            VALUES ('{}', '{}')""".format(ingredients_string, name_on_order)

        # Button to submit order
        time_to_insert = st.button('Submit Order')
        if time_to_insert:
            try:
                # Execute SQL insert statement
                session.sql(my_insert_stmt).collect()
                st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")
            except Exception as e:
                st.error(f"Failed to submit order: {str(e)}")

except Exception as ex:
    st.error(f"An error occurred: {str(ex)}")

# Display a link
st.write("https://github.com/appuv")
