import os
import streamlit as st
from dotenv import load_dotenv

from frontend.utils.chat import (
    get_openai_model_choices,
    get_categories,
    search_initial,
    search_product_listings, fetch_chat_sessions
)

load_dotenv()

def qa_interface():
    st.title("Search Interface")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]
    if "recommended_products" not in st.session_state:
        st.session_state.recommended_products = []
    if "chat_session_id" not in st.session_state:
        st.session_state.chat_session_id = None

    # Fetch models/categories
    models = get_openai_model_choices() or []
    categories = get_categories() or []
    chat_sessions = ["New Chat"] + fetch_chat_sessions()

    # Sidebar
    with st.sidebar:
        st.title("🔧 Settings")
        model = st.selectbox("Model", models if models else ["gpt-3.5-turbo"])
        category = st.selectbox("Category", categories if categories else ["general"])
        selected_chat_session = st.selectbox("Chat Session", options=chat_sessions)

        if st.button("Clear Chat"):
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Hello! How can I help you today?"}
            ]
            st.session_state.recommended_products = []

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Prompt input
    prompt = st.chat_input("Enter your prompt:")

    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        user_messages = [m for m in st.session_state.chat_history if m["role"] == "user"]
        assistant_reply = ""

        if len(user_messages) == 1:
            # First user query -> call /search/initial
            with st.spinner("Performing initial search..."):
                response = search_initial(model, prompt, category, selected_chat_session, st.session_state.chat_history)
                st.write("Debug: Raw response from search_initial:", response)

                if isinstance(response, dict):
                    rag_output = response.get("response", {})
                    products = rag_output.get("products", [])
                    reasoning_summary = rag_output.get("reasoning_summary", "")

                    if products:
                        assistant_reply += "Based on the community discussions, here are some recommended products:\n\n"
                        st.session_state.recommended_products = []  # reset

                        for idx, product in enumerate(products, start=1):
                            product_name = product.get("product_name", "Unknown Product")
                            reason = product.get("reason_for_recommendation", "No reason provided.")
                            st.session_state.recommended_products.append(product_name)

                            assistant_reply += f"**{idx}. {product_name}**\n"
                            assistant_reply += f"{reason}\n\n"

                        if reasoning_summary:
                            assistant_reply += f"**Reasoning Summary:** {reasoning_summary}\n"
                    else:
                        assistant_reply = "No products found in the RAG response."
                elif isinstance(response, str):
                    assistant_reply = response
                else:
                    st.write("Debug: Unexpected response type for initial search:", type(response))
                    assistant_reply = "Error: Unexpected response format from initial search."

        else:
            # Subsequent queries -> call /search/product-listings
            with st.spinner("Searching products..."):
                response = search_product_listings(prompt)
                st.write("Debug: Raw response from search_product_listings:", response)

                if isinstance(response, list):
                    if response:
                        assistant_reply = "Here are some products I found:\n\n"
                        # Instead of just listing them in text, let's create the card layout:
                        assistant_reply += create_cards(response)
                    else:
                        assistant_reply = "No products found."
                elif isinstance(response, dict):
                    st.write("Debug: product_listings response is a dict")
                    assistant_reply = f"Error: {response}"
                elif isinstance(response, str):
                    st.write("Debug: product_listings response is a string")
                    assistant_reply = response
                else:
                    st.write("Debug: Unexpected response type for product listings:", type(response))
                    assistant_reply = "Error: Unexpected response format from product listings."

        with st.chat_message("assistant"):
            st.markdown(assistant_reply)
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

    # Show "links to buy" for each recommended product, limited to 5 listings displayed as cards
    if st.session_state.recommended_products:
        st.divider()
        st.subheader("Buy These Recommended Products:")

        for product_name in st.session_state.recommended_products:
            st.markdown(f"### {product_name}")
            with st.spinner(f"Fetching product links for: {product_name}..."):
                pl_response = search_product_listings(product_name)

            if isinstance(pl_response, list) and pl_response:
                limited_listings = pl_response[:5]
                # Render these 5 listings as cards
                card_markdown = create_cards(limited_listings)
                st.markdown(card_markdown, unsafe_allow_html=True)
            else:
                st.write("No links found or unexpected response.")
            st.write("---")

def create_cards(product_list):
    """
    Takes a list of product dicts and returns HTML for card-like layout
    with lighter backgrounds for better readability.
    """
    cards_per_row = 4
    all_rows_html = ""

    for i in range(0, len(product_list), cards_per_row):
        row_items = product_list[i : i + cards_per_row]
        # Use a flex container for a row of cards
        row_html = '<div style="display: flex; gap: 10px; margin-bottom: 10px;">'

        for item in row_items:
            title = item.get("title", "N/A")
            price = item.get("price", "N/A")
            product_url = item.get("product_url", "#")
            merchant_name = item.get("merchant_name", "N/A")

            # Card styling with a lighter background (e.g. #f0f0f0),
            # darker text (#333), and clearer color highlights
            card_html = f"""
            <div style="
                flex: 1; 
                background-color: #f0f0f0; 
                border-radius: 8px; 
                padding: 15px; 
                min-width: 150px;
            ">
                <p style="font-weight: bold; margin-bottom: 5px; color: #333;">{merchant_name}</p>
                <p style="color: #d9534f; font-size: 1.1em; margin: 0;">{price}</p>
                <p style="font-size: 0.9em; color: #333;">{title}</p>
                <a href="{product_url}" target="_blank" 
                   style="color: #0275d8; text-decoration: none; font-size: 0.9em;">
                    View Product
                </a>
            </div>"""
            row_html += card_html

        row_html += "</div>"
        all_rows_html += row_html

    return all_rows_html

if __name__ == "__main__":
    qa_interface()
