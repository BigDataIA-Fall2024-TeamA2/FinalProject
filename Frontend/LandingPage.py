import os
import openai
import streamlit as st

def chat_page():
    # Set your OpenAI API key
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Page config
    st.set_page_config(page_title="ChatGPT-like UI", page_icon="🤖", layout="wide")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]

    # Sidebar for settings
    with st.sidebar:
        st.title("🔧 Settings")
        model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4"])
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
        st.markdown("---")
        if st.button("Clear Chat"):
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! How can I help you today?"}
            ]

    # Style and layout
    st.markdown(
        """
        <style>
        body {
            font-family: 'Helvetica', sans-serif;
            background-color: #F9F9F9;
        }
        .user-bubble {
            background: #E0E0E0;
            padding: 10px 15px;
            border-radius: 15px;
            margin-bottom: 10px;
            color: #333333;
            max-width: 80%;
            width: fit-content;
        }
        .assistant-bubble {
            background: #DCF8C6;
            padding: 10px 15px;
            border-radius: 15px;
            margin-bottom: 10px;
            color: #333333;
            max-width: 80%;
            width: fit-content;
        }
        .assistant-bubble pre {
            background: #f3f3f3;
            border-radius: 5px;
            padding: 10px;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
        }
        .message-row {
            display: flex;
            margin-bottom: 20px;
        }
        .message-row.user .user-bubble {
            margin-left: auto;
            margin-right: 0;
        }
        .message-row.assistant .assistant-bubble {
            margin-left: 0;
            margin-right: auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("🤖 Chat with AI")

    # Display conversation
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "assistant":
            st.markdown(
                f"""
                <div class="message-row assistant">
                    <div class="assistant-bubble">{msg['content']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="message-row user">
                    <div class="user-bubble">{msg['content']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # User input
    user_input = st.text_input("Type your message:", value="", key="user_input", placeholder="Ask me anything...")

    # Send button
    if st.button("Send", type="primary"):
        if user_input.strip():
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Get response
            with st.spinner("Thinking..."):
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=st.session_state.messages,
                    temperature=temperature,
                )
                assistant_reply = response["choices"][0]["message"]["content"]
                # Add assistant's response
                st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

            # Clear input field
            st.session_state.user_input = ""

    # Regenerate button
    if len(st.session_state.messages) > 1 and st.button("Regenerate Response"):
        # Remove last assistant message if it exists
        if st.session_state.messages[-1]["role"] == "assistant":
            st.session_state.messages.pop()
        with st.spinner("Re-generating..."):
            response = openai.ChatCompletion.create(
                model=model,
                messages=st.session_state.messages,
                temperature=temperature,
            )
            assistant_reply = response["choices"][0]["message"]["content"]
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

# Call the page function if this file is run directly
if __name__ == "__main__":
    chat_page()
