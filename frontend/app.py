import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8006/execute"

st.title("Doctor Appointment Assistant")
st.markdown("---")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "patient_id" not in st.session_state:
    st.session_state.patient_id = 2  # Default ID

# Sidebar for patient ID and info
with st.sidebar:
    st.header("Patient Information")
    
    # Patient ID input
    patient_id = st.number_input(
        "Patient ID",
        min_value=1,
        max_value=99999999,
        value=st.session_state.patient_id,
        help="Enter your patient ID (7-8 digits)"
    )
    st.session_state.patient_id = patient_id
    
    # Check patient info button
    if st.button("Check My Info"):
        with st.spinner("Checking patient information..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"messages": f"Get my patient information", "id_number": patient_id},
                    timeout=10
                )
                if response.status_code == 200:
                    result = response.json()
                    if "messages" in result:
                        st.info(f"Patient ID: {patient_id}")
                        # Try to extract patient info from response
                        for msg in result["messages"]:
                            if isinstance(msg, dict) and msg.get("sender") == "assistant":
                                st.write(msg.get("content", "No information available"))
                else:
                    st.error("Failed to retrieve patient information")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    st.header("Available Actions")
    st.markdown("""
    - **Book Appointment**: "I want to book an appointment with Dr. Mohamed Tajmouati"
    - **Check Availability**: "Is Dr. Adil Tajmouati available on 15-12-2024?"
    - **Cancel Appointment**: "Cancel my appointment with Dr. Hanane Louizi"
    - **Patient Management**: "Create a new patient", "Update my information", "Get my patient info"
    - **FAQ**: "What are your services?", "What are your working hours?"
    """)
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# Main chat interface
st.header("Chat with Assistant")

# Display chat history
chat_container = st.container()
with chat_container:
    for sender, message in st.session_state.chat_history:
        if sender == "You":
            with st.chat_message("user"):
                st.write(message)
        else:
            with st.chat_message("assistant"):
                # Handle both string and dict messages
                if isinstance(message, dict):
                    if "content" in message:
                        st.write(message["content"])
                    else:
                        st.write(json.dumps(message, indent=2))
                else:
                    st.write(message)

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to chat
    with chat_container:
        with st.chat_message("user"):
            st.write(user_input)
    
    # Add to history
    st.session_state.chat_history.append(("You", user_input))
    
    # Get bot response
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                API_URL,
                json={"messages": user_input, "id_number": st.session_state.patient_id},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                bot_messages = result.get("messages", [])
                
                # Extract assistant messages
                for msg in bot_messages:
                    if isinstance(msg, dict) and msg.get("sender") in ["assistant", "check_suggest_availability_sup_agent", "appointment_management_sup_agent", "faq_sup_agent", "patient_management_sup_agent"]:
                        bot_content = msg.get("content", "No response")
                        
                        # Add to history
                        st.session_state.chat_history.append(("Bot", msg))
                        
                        # Display in chat
                        with chat_container:
                            with st.chat_message("assistant"):
                                st.write(bot_content)
                        break
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                st.session_state.chat_history.append(("Bot", error_msg))
                with chat_container:
                    with st.chat_message("assistant"):
                        st.error(error_msg)
                        
        except requests.exceptions.Timeout:
            error_msg = "Request timed out. Please try again."
            st.session_state.chat_history.append(("Bot", error_msg))
            with chat_container:
                with st.chat_message("assistant"):
                    st.error(error_msg)
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.session_state.chat_history.append(("Bot", error_msg))
            with chat_container:
                with st.chat_message("assistant"):
                    st.error(error_msg)

# Footer
st.markdown("---")
st.caption("Doctor Appointment Multi-Agent System v1.0")
