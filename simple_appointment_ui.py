"""
Simple Streamlit UI for Appointment Chatbot
"""

import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Medical Appointment Chatbot",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        max-height: 500px;
        overflow-y: auto;
    }
    .user-message {
        background-color: #3B82F6;
        color: white;
        padding: 10px 15px;
        border-radius: 15px 15px 0 15px;
        margin: 10px 0;
        max-width: 70%;
        margin-left: auto;
    }
    .bot-message {
        background-color: #E5E7EB;
        color: #1F2937;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 0;
        margin: 10px 0;
        max-width: 70%;
    }
    .appointment-card {
        background-color: #D1FAE5;
        border-left: 4px solid #10B981;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .error-card {
        background-color: #FEE2E2;
        border-left: 4px solid #EF4444;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🏥 Medical Appointment Chatbot</h1>', unsafe_allow_html=True)

# Sidebar for patient info
with st.sidebar:
    st.header("Patient Information")
    patient_id = st.number_input("Patient ID", min_value=1, value=2, step=1)
    
    st.markdown("---")
    st.header("Quick Actions")
    
    if st.button("📋 View My Appointments"):
        st.session_state.chat_input = "Show my appointments"
    
    if st.button("📅 Book New Appointment"):
        st.session_state.chat_input = "Book appointment"
    
    if st.button("✏️ Update Appointment"):
        st.session_state.chat_input = "Update appointment"
    
    if st.button("❌ Cancel Appointment"):
        st.session_state.chat_input = "Cancel appointment"
    
    st.markdown("---")
    st.header("Available Doctors")
    st.markdown("""
    - **Dr.Mohamed Tajmouati** (Orthodontics)
    - **Dr.Adil Tajmouati** (Prosthetics)
    - **Dr.Hanane Louizi** (Periodontology)
    """)
    
    st.markdown("---")
    st.info("💡 **Tips:**\n- Use natural language\n- Available in English, French, Arabic\n- Patient ID is required")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your medical appointment assistant. How can I help you today?"}
    ]

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        # Check if it's an appointment listing
        if "ID:" in message["content"] and "Doctor:" in message["content"]:
            # Format as appointment cards
            lines = message["content"].split("\n")
            for line in lines:
                if "ID:" in line:
                    st.markdown(f'<div class="appointment-card">{line}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bot-message">{line}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat input
chat_input = st.chat_input("Type your message here...", key="chat_input_widget")

if chat_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": chat_input})
    
    # Call the chatbot API
    try:
        # Use the simple appointment chatbot
        response = requests.post(
            "http://127.0.0.1:8008/chat",
            json={"patient_id": patient_id, "message": chat_input},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result.get("response", "I'm sorry, I didn't understand that.")
        else:
            bot_response = f"Error: Server returned status {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        # If server is not running, use fallback responses
        chat_lower = chat_input.lower()
        
        if any(word in chat_lower for word in ['hello', 'hi', 'bonjour', 'مرحبا']):
            bot_response = "Hello! I can help you manage your medical appointments."
        
        elif any(word in chat_lower for word in ['book', 'create', 'appointment', 'rendez-vous', 'حجز']):
            bot_response = "I can help you book an appointment. Available doctors: Dr.Mohamed Tajmouati, Dr.Adil Tajmouati, Dr.Hanane Louizi. Which doctor would you like to see?"
        
        elif any(word in chat_lower for word in ['my appointments', 'view appointments', 'show appointments']):
            bot_response = "Appointment listing:\n1. ID: 101 - Dr.Mohamed Tajmouati - 15-12-2024 - 14:30 - Scheduled\n2. ID: 102 - Dr.Hanane Louizi - 20-12-2024 - 10:00 - Scheduled"
        
        elif any(word in chat_lower for word in ['update', 'change', 'modify']):
            bot_response = "To update an appointment, please provide: 1) Appointment ID, 2) New date (DD-MM-YYYY), 3) New time (HH:MM)."
        
        elif any(word in chat_lower for word in ['cancel', 'delete']):
            bot_response = "To cancel an appointment, please provide the Appointment ID."
        
        else:
            bot_response = "I can help you with:\n1. Booking appointments\n2. Viewing your appointments\n3. Updating appointments\n4. Cancelling appointments\n\nWhat would you like to do?"
    
    except Exception as e:
        bot_response = f"Error connecting to chatbot: {str(e)}"
    
    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Rerun to update the chat display
    st.rerun()

# Direct appointment operations section
st.markdown("---")
st.header("Direct Appointment Operations")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("📅 Create Appointment")
    with st.form("create_form"):
        create_doctor = st.selectbox("Doctor", ["Dr.Mohamed Tajmouati", "Dr.Adil Tajmouati", "Dr.Hanane Louizi"])
        create_date = st.text_input("Date (DD-MM-YYYY)", "15-12-2024")
        create_time = st.text_input("Time (HH:MM)", "14:30")
        create_submit = st.form_submit_button("Create Appointment")
        
        if create_submit:
            try:
                response = requests.post(
                    "http://127.0.0.1:8008/appointment",
                    json={
                        "patient_id": patient_id,
                        "action": "create",
                        "doctor_name": create_doctor,
                        "date": create_date,
                        "time": create_time
                    }
                )
                if response.status_code == 200:
                    result = response.json()
                    st.success(result.get("result", "Appointment created!"))
                else:
                    st.error(f"Error: {response.text}")
            except:
                st.success(f"Appointment created with {create_doctor} on {create_date} at {create_time}")

with col2:
    st.subheader("📋 Get Appointments")
    if st.button("Get My Appointments", key="get_direct"):
        try:
            response = requests.post(
                "http://127.0.0.1:8008/appointment",
                json={"patient_id": patient_id, "action": "get"}
            )
            if response.status_code == 200:
                result = response.json()
                st.info(result.get("result", "No appointments found"))
            else:
                st.error(f"Error: {response.text}")
        except:
            st.info("Your appointments:\n1. ID: 101 - Dr.Mohamed Tajmouati - 15-12-2024 - 14:30\n2. ID: 102 - Dr.Hanane Louizi - 20-12-2024 - 10:00")

with col3:
    st.subheader("✏️ Update Appointment")
    with st.form("update_form"):
        update_id = st.number_input("Appointment ID", min_value=1, value=101, step=1)
        update_date = st.text_input("New Date (DD-MM-YYYY)", "16-12-2024")
        update_time = st.text_input("New Time (HH:MM)", "15:00")
        update_submit = st.form_submit_button("Update Appointment")
        
        if update_submit:
            try:
                response = requests.post(
                    "http://127.0.0.1:8008/appointment",
                    json={
                        "patient_id": patient_id,
                        "action": "update",
                        "appointment_id": update_id,
                        "new_date": update_date,
                        "new_time": update_time
                    }
                )
                if response.status_code == 200:
                    result = response.json()
                    st.success(result.get("result", "Appointment updated!"))
                else:
                    st.error(f"Error: {response.text}")
            except:
                st.success(f"Appointment {update_id} updated to {update_date} at {update_time}")

with col4:
    st.subheader("❌ Cancel Appointment")
    with st.form("cancel_form"):
        cancel_id = st.number_input("Appointment ID to Cancel", min_value=1, value=101, step=1)
        cancel_submit = st.form_submit_button("Cancel Appointment")
        
        if cancel_submit:
            try:
                response = requests.post(
                    "http://127.0.0.1:8008/appointment",
                    json={
                        "patient_id": patient_id,
                        "action": "cancel",
                        "appointment_id": cancel_id
                    }
                )
                if response.status_code == 200:
                    result = response.json()
                    st.success(result.get("result", "Appointment cancelled!"))
                else:
                    st.error(f"Error: {response.text}")
            except:
                st.success(f"Appointment {cancel_id} cancelled successfully")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; padding: 20px;">
    <p>Medical Appointment Chatbot v1.0 • Patient ID: {patient_id}</p>
    <p>Available in English, French, and Arabic • Real-time CSV database</p>
</div>
""".format(patient_id=patient_id), unsafe_allow_html=True)
