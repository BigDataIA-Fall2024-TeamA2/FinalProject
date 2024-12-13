import os
import streamlit as st
from dotenv import load_dotenv

from frontend.utils.chat import (
    get_openai_model_choices,
    get_categories,
    search_initial,
    search_product_listings
)

load_dotenv()

def qa_interface():
    st.title("Search Interface")

    # Initialize chat history if not present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]

    # Fetch models and categories (expected to return lists)
    models = get_openai_model_choices() or []
    categories = get_categories() or []

    # Sidebar settings
    with st.sidebar:
        st.title("🔧 Settings")
        model = st.selectbox("Model", models if models else ["gpt-3.5-turbo"])
        category = st.selectbox("Category", categories if categories else ["general"])
        if st.button("Clear Chat"):
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Hello! How can I help you today?"}
            ]

    # Display existing chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input for the prompt
    prompt = st.chat_input("Enter your prompt:")

    if prompt:
        # Add the user's message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Determine which endpoint to call
        user_messages = [m for m in st.session_state.chat_history if m["role"] == "user"]

        if len(user_messages) == 1:
            # If this is the first user query after greeting -> call /search/initial
            with st.spinner("Performing initial search..."):
                response = search_initial(model, prompt, category)

                # Debug print to see what search_initial returns
                st.write("Debug: Raw response from search_initial:", response)

                if isinstance(response, dict):
                    st.write("Debug: search_initial response is a dict")
                    # According to the example you gave, the response looks like:
                    # {
                    #   "response": "...",
                    #   "tools_used": "vector_search"
                    # }
                    assistant_reply = response.get("response", "No 'response' field found.")
                elif isinstance(response, str):
                    st.write("Debug: search_initial response is a string")
                    assistant_reply = response
                else:
                    st.write("Debug: Unexpected response type for initial search:", type(response))
                    assistant_reply = "Error: Unexpected response format from initial search."

        else:
            # Subsequent queries -> call /search/product-listings
            with st.spinner("Searching products..."):
                response = search_product_listings(prompt)

                # Debug print to see what search_product_listings returns
                st.write("Debug: Raw response from search_product_listings:", response)

                if isinstance(response, list):
                    st.write("Debug: response is a list of products")
                    products = response
                    if products:
                        assistant_reply = "Here are some products I found:\n\n"
                        for p in products:
                            title = p.get("title", "N/A")
                            price = p.get("price", "N/A")
                            product_url = p.get("product_url", "#")
                            merchant_name = p.get("merchant_name", "N/A")
                            assistant_reply += (
                                f"- **{title}**\n"
                                f"  Price: {price}\n"
                                f"  Merchant: {merchant_name}\n"
                                f"  URL: {product_url}\n\n"
                            )
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

        # Display the assistant's reply
        with st.chat_message("assistant"):
            st.markdown(assistant_reply)

        # Add the assistant's message to the chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": assistant_reply
        })

if __name__ == "__main__":
    qa_interface()
