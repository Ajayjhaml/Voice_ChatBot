import streamlit as st
import requests

st.set_page_config(page_title="Customer Service Chatbot", layout="centered")
st.title("🛍️ Customer Support Chatbot")
st.markdown("Ask any question related to our services!")

# Session state to hold chat history
if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("You:", placeholder="Type your question here...")

if st.button("Send"):
    if user_input.strip() != "":
        with st.spinner("Generating reply..."):
            try:
                response = requests.post("http://localhost:8000/generate", json={"instruction": user_input})
                if response.status_code == 200:
                    output = response.json().get("output", "❌ No response from model.")
                else:
                    output = f"❌ API Error: {response.status_code}"
            except Exception as e:
                output = f"❌ Connection error: {e}"

        st.session_state.history.append(("You", user_input))
        st.session_state.history.append(("Bot", output))

# Display chat history
for sender, message in reversed(st.session_state.history):
    if sender == "You":
        st.markdown(f"**🧑‍💼 You:** {message}")
    else:
        st.markdown(f"**🤖 Bot:** {message}")
