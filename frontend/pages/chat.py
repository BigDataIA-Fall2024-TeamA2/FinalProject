import os
import streamlit as st
from dotenv import load_dotenv
from frontend.utils.chat import (
    get_openai_model_choices,
    get_categories,
    search_initial,
    search_product_listings,
)

# Load environment variables
load_dotenv()

# Ensure required environment variables are loaded
BACKEND_URI = os.getenv("BACKEND_URI")
if not BACKEND_URI:
    raise ValueError("BACKEND_URI is not set. Please add it to your environment variables.")

def create_cards(product_list):
    """
    Creates an HTML card layout for the given product list.
    """
    cards_per_row = 4
    all_rows_html = ""
    for i in range(0, len(product_list), cards_per_row):
        row_items = product_list[i : i + cards_per_row]
        row_html = '<div style="display: flex; gap: 10px; margin-bottom: 10px;">'
        for item in row_items:
            title = item.get("title", "N/A")
            price = item.get("price", "N/A")
            product_url = item.get("product_url", "#")
            merchant_name = item.get("merchant_name", "N/A")
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
                <a href="{product_url}" target="_blank" style="color: #0275d8; text-decoration: none; font-size: 0.9em;">
                    View Product
                </a>
            </div>"""
            row_html += card_html
        row_html += "</div>"
        all_rows_html += row_html
    return all_rows_html

def process_search_response(response, chat_container):
    """
    Processes the initial search response, extracts recommended products, and displays them.
    """
    if isinstance(response, dict):
        rag_output = response.get("response", {})
        products = rag_output.get("products", [])
        reasoning_summary = rag_output.get("reasoning_summary", "")

        if products:
            assistant_reply = "Based on the community discussions, here are some recommended products:\n\n"
            st.session_state.recommended_products = []

            for idx, product in enumerate(products, start=1):
                product_name = product.get("product_name", "Unknown Product")
                reason = product.get("reason_for_recommendation", "No reason provided.")
                st.session_state.recommended_products.append({
                    "name": product_name,
                    "listings": [],
                })
                assistant_reply += f"**{idx}. {product_name}**\n{reason}\n\n"

            if reasoning_summary:
                assistant_reply += f"**Reasoning Summary:** {reasoning_summary}"

            with chat_container.chat_message("assistant"):
                st.markdown(assistant_reply)
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

            # Fetch product listings for recommended products
            for product in st.session_state.recommended_products:
                process_product_search(product["name"], chat_container, is_recommendation=True)

            return True
    return False

def process_product_search(prompt, chat_container, is_recommendation=False):
    """
    Searches for products based on the given prompt and displays results.
    """
    with st.spinner("Searching products..."):
        try:
            response = search_product_listings(prompt)
            if isinstance(response, list) and response:
                with chat_container.chat_message("assistant"):
                    if not is_recommendation:
                        st.markdown(f"Here are some products I found for '{prompt}':")
                    card_markdown = create_cards(response[:5])
                    st.markdown(card_markdown, unsafe_allow_html=True)

                if is_recommendation:
                    # Update the corresponding product entry in recommended_products
                    for product in st.session_state.recommended_products:
                        if product["name"] == prompt:
                            product["listings"] = response[:5]
                            break

            return True
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return False

def process_all_initial_searches(model, category, chat_container):
    """
    Processes all user inputs in chat history for initial searches.
    """
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.spinner(f"Processing initial search for: {message['content']}..."):
                response = search_initial(model, message["content"], category)
                process_search_response(response, chat_container)

def qa_interface():
    """
    Main interface for the search application.
    """
    st.title("Search Interface")

    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]
    if "recommended_products" not in st.session_state:
        st.session_state.recommended_products = []

    # Sidebar settings
    with st.sidebar:
        st.title("🔧 Settings")
        model = st.selectbox("Model", get_openai_model_choices() or ["gpt-3.5-turbo"])
        category = st.selectbox("Category", get_categories() or ["general"])
        if st.button("Clear Chat"):
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Hello! How can I help you today?"}
            ]
            st.session_state.recommended_products = []
            st.experimental_rerun()

    # Create main chat container
    chat_container = st.container()

    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Perform initial searches for all past prompts
    if "initialized" not in st.session_state:
        process_all_initial_searches(model, category, chat_container)
        st.session_state["initialized"] = True

    # Handle user input
    prompt = st.chat_input("Enter your prompt:")

    # Process new input
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)
        process_product_search(prompt, chat_container)

    # Display recommended products and their listings
    if st.session_state.recommended_products:
        st.divider()
        st.subheader("Recommended Products and Listings")
        for product in st.session_state.recommended_products:
            if isinstance(product, dict) and "name" in product:
                st.markdown(f"### {product['name']}")
                if product["listings"]:
                    card_markdown = create_cards(product["listings"])
                    st.markdown(card_markdown, unsafe_allow_html=True)
                else:
                    st.write("No listings found for this product.")
            else:
                st.warning(f"Unexpected product format: {product}")
            st.write("---")

if __name__ == "__main__":
    qa_interface()
