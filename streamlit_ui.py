import streamlit as st
import requests

API_URL = "http://127.0.0.1:8003/execute"

st.title("💬 Doctor Appointment Assistant")

# Session state to keep conversation
if "history" not in st.session_state:
    st.session_state.history = []

user_id = st.text_input("Enter your ID number:", "")

query = st.text_area(
    "Enter your query:",
    placeholder="Example: Can you check if a dentist is available tomorrow at 10 AM?"
)

if st.button("Send"):
    if user_id.strip() == "" or query.strip() == "":
        st.warning("Please enter both ID and query.")
    else:
        try:
            with st.spinner("Processing your request..."):
                payload = {
                    "messages": query,
                    "id_number": int(user_id),
                }

                response = requests.post(API_URL, json=payload, verify=False)

                if response.status_code == 200:
                    data = response.json()

                    # Add to chat history
                    st.session_state.history.append(("🧑 User", query))

                    # Extract agent response
                    agent_messages = data.get("messages", [])

                    # Convert list of dict messages to readable text
                    result_text = ""
                    for msg in agent_messages:
                        # If message is a dict with content
                        if isinstance(msg, dict):
                            result_text += msg.get("content", "") + "\n"
                        else:
                            result_text += str(msg) + "\n"

                    st.session_state.history.append(("🤖 Agent", result_text))
                else:
                    st.error(f"Error {response.status_code}: Could not process the request.")

        except Exception as e:
            st.error(f"⚠️ Exception occurred: {e}")

# Show full chat history
st.subheader("Conversation History:")

for sender, text in st.session_state.history:
    st.markdown(f"**{sender}:** {text}")
