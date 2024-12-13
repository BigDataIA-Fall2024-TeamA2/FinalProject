# app.py

import streamlit as st
from backend.services.test import fetch_google_shopping_results, extract_product_details

# Streamlit app title
st.title("Google Shopping Product Search")

# Search input box
query = st.text_input("Search for products (e.g., 'headphones')", "headphones")

# If search is triggered
if st.button("Search"):
    with st.spinner("Fetching results..."):
        try:
            # Fetch data from the backend
            api_response = fetch_google_shopping_results(query)
            products = extract_product_details(api_response)

            # Display results
            if products:
                st.write(f"### Results for '{query}':")

                # Limit to the first 10 results
                for product in products[:10]:
                    title = product.get("title", "N/A")
                    price = product.get("price", "N/A")
                    product_url = product.get("product_url", "#")
                    merchant_name = product.get("merchant_name", "N/A")

                    # Display product details
                    st.write(f"**Title:** {title}")
                    st.write(f"**Price:** {price}")
                    st.write(f"**Merchant:** {merchant_name}")
                    st.write(f"[View Product]({product_url})")
                    st.markdown("---")  # Separator
            else:
                st.error("No results found.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
