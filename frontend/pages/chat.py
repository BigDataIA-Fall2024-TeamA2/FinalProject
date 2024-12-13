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

def create_cards(product_list):
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

def qa_interface():
    st.title("Search Interface")

    # Initialize session state
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

    # Sidebar
    with st.sidebar:
        st.title("🔧 Settings")
        model = st.selectbox("Model", get_openai_model_choices() or ["gpt-3.5-turbo"])
        category = st.selectbox("Category", get_categories() or ["general"])
        selected_chat_session = st.selectbox("Chat Session", options=["New Chat"] + fetch_chat_sessions())


        if st.button("Clear Chat"):
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Hello! How can I help you today?"}
            ]
            st.session_state.recommended_products = []
            st.rerun()

    # Create main chat container
    chat_container = st.container()

    # Handle user input
    prompt = st.chat_input("Enter your prompt:")

    # Display chat history and process new input
    with chat_container:
        # Display existing chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Process new input
        if prompt:
            # Display user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            user_messages = [m for m in st.session_state.chat_history if m["role"] == "user"]

            if len(user_messages) == 1:
                # Initial search
                with st.spinner("Processing initial search..."):
                    response = search_initial(model, prompt, category, selected_chat_session)
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
                                st.session_state.recommended_products.append(product_name)
                                assistant_reply += f"**{idx}. {product_name}**\n{reason}\n\n"

                            if reasoning_summary:
                                assistant_reply += f"**Reasoning Summary:** {reasoning_summary}"

                            with st.chat_message("assistant"):
                                st.markdown(assistant_reply)
                            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

                            # Process product listings for recommended products
                            if st.session_state.recommended_products:
                                st.divider()
                                st.subheader("Buy These Recommended Products:")
                                for product_name in st.session_state.recommended_products:
                                    st.markdown(f"### {product_name}")
                                    with st.spinner(f"Fetching product links for: {product_name}..."):
                                        try:
                                            pl_response = search_product_listings(product_name)
                                            if isinstance(pl_response, list) and pl_response:
                                                card_markdown = create_cards(pl_response[:5])
                                                st.markdown(card_markdown, unsafe_allow_html=True)
                                            st.write("---")
                                        except Exception as e:
                                            st.error(f"Error fetching products: {str(e)}")
            else:
                # Product search
                with st.spinner("Searching products..."):
                    response = search_product_listings(prompt)
                    if isinstance(response, list) and response:
                        with st.chat_message("assistant"):
                            st.markdown("Here are some products I found:")
                            card_markdown = create_cards(response[:5])
                            st.markdown(card_markdown, unsafe_allow_html=True)
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": "Here are some products I found:"}
                        )

if __name__ == "__main__":
    qa_interface()
