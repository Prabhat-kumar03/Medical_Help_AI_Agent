import streamlit as st
import requests

FASTAPI_URL = "http://localhost:8000/answer"  
st.set_page_config(page_title="DataSmith Assignment", page_icon="💬", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []  

st.title("💬 Datasmith AI Assignment")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        response = requests.post(FASTAPI_URL, data={"user_input": user_input, "session_id": "111"})
        response.raise_for_status()
        data = response.json()
        assistant_reply = data.get("result", "⚠️ No response received.")
        assistant_reply = assistant_reply[0].get("value")
    except Exception as e: 
        assistant_reply = f"❌ Error contacting backend: {e}"

    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

# st.markdown(
#     """
#     ---
#     **Tips:**
#     - Type a message and press Enter to send.
#     - The conversation persists in memory until you refresh the page.
#     - Connect to your FastAPI `/answer` endpoint that returns a JSON: `{"response": "..."}`
#     """
# )