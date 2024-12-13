import streamlit as st
from dotenv import load_dotenv
import os
from backend.services.e_commerce import fetch_google_shopping_listings

# Load environment variables from .env file
load_dotenv()

# Streamlit app title
st.title("Google Shopping Product Search")

# Inputs for credentials and query
username = st.text_input("Enter your OxyLabs Username", type="password")
password = st.text_input("Enter your OxyLabs Password", type="password")
query = st.text_input("Search for products (e.g., 'headphones')", "headphones")

# If search is triggered
if st.button("Search"):
    with st.spinner("Fetching results..."):
        try:
            # Call the backend function
            products = fetch_google_shopping_listings(query, username, password)

            # Display results
            if products:
                st.write(f"### Results for '{query}':")

                # Limit to the first 10 results
                for product in products[:10]:
                    title = product.get("title", "N/A")
                    price = product.get("price", "N/A")
                    currency = product.get("currency", "N/A")
                    url = product.get("url", "#")
                    image_url = product.get("image_url", "")

                    # Display product details
                    st.write(f"**Title:** {title}")
                    st.write(f"**Price:** {price} {currency}" if price != "N/A" else "**Price:** N/A")
                    st.write(f"[View Product]({url})" if url else "URL not available")
                    if image_url:
                        st.image(image_url, width=150)
                    else:
                        st.write("📷 Image not available")
                    st.markdown("---")  # Separator
            else:
                st.error("No results found.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
