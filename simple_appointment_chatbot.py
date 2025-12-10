"""
Simple appointment chatbot focused on appointment management
"""

from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
import os

app = FastAPI()

# -------------------------------
# DATA MODELS
# -------------------------------
class AppointmentRequest(BaseModel):
    patient_id: int
    action: str  # "create", "get", "update", "cancel"
    doctor_name: str = None
    date: str = None
    time: str = None
    appointment_id: int = None
    new_date: str = None
    new_time: str = None

class ChatMessage(BaseModel):
    patient_id: int
    message: str

# -------------------------------
# DATA MANAGEMENT
# -------------------------------
APPOINTMENTS_FILE = "data/rendez_vous.csv"
DOCTORS_FILE = "data/doctors.csv"

def load_appointments():
    """Load appointments from CSV"""
    if os.path.exists(APPOINTMENTS_FILE):
        return pd.read_csv(APPOINTMENTS_FILE)
    else:
        # Create empty dataframe
        return pd.DataFrame(columns=['appointment_id', 'patient_id', 'doctor_name', 'date', 'time', 'status'])

def save_appointments(df):
    """Save appointments to CSV"""
    df.to_csv(APPOINTMENTS_FILE, index=False)

def load_doctors():
    """Load doctors from CSV"""
    if os.path.exists(DOCTORS_FILE):
        return pd.read_csv(DOCTORS_FILE)
    else:
        # Default doctors
        return pd.DataFrame([
            {"doctor_id": 1, "name": "Dr.Mohamed Tajmouati", "specialization": "Orthodontics"},
            {"doctor_id": 2, "name": "Dr.Adil Tajmouati", "specialization": "Prosthetics"},
            {"doctor_id": 3, "name": "Dr.Hanane Louizi", "specialization": "Periodontology"}
        ])

# -------------------------------
# APPOINTMENT OPERATIONS
# -------------------------------
def create_appointment(patient_id, doctor_name, date, time):
    """Create a new appointment"""
    df = load_appointments()
    
    # Generate new appointment ID
    if len(df) > 0:
        new_id = df['appointment_id'].max() + 1
    else:
        new_id = 1
    
    # Add new appointment
    new_appointment = {
        'appointment_id': new_id,
        'patient_id': patient_id,
        'doctor_name': doctor_name,
        'date': date,
        'time': time,
        'status': 'scheduled'
    }
    
    df = pd.concat([df, pd.DataFrame([new_appointment])], ignore_index=True)
    save_appointments(df)
    
    return f"Appointment created successfully! ID: {new_id}, Doctor: {doctor_name}, Date: {date}, Time: {time}"

def get_appointments(patient_id):
    """Get all appointments for a patient"""
    df = load_appointments()
    patient_appointments = df[df['patient_id'] == patient_id]
    
    if len(patient_appointments) == 0:
        return "You have no appointments scheduled."
    
    appointments_list = []
    for _, row in patient_appointments.iterrows():
        appointments_list.append(
            f"ID: {row['appointment_id']} - Doctor: {row['doctor_name']} - Date: {row['date']} - Time: {row['time']} - Status: {row['status']}"
        )
    
    return "Your appointments:\n" + "\n".join(appointments_list)

def update_appointment(appointment_id, new_date=None, new_time=None):
    """Update an existing appointment"""
    df = load_appointments()
    
    if appointment_id not in df['appointment_id'].values:
        return f"Appointment ID {appointment_id} not found."
    
    # Update appointment
    idx = df[df['appointment_id'] == appointment_id].index[0]
    
    if new_date:
        df.at[idx, 'date'] = new_date
    if new_time:
        df.at[idx, 'time'] = new_time
    
    save_appointments(df)
    
    updated = df.iloc[idx]
    return f"Appointment updated successfully! ID: {appointment_id}, Doctor: {updated['doctor_name']}, New Date: {updated['date']}, New Time: {updated['time']}"

def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    df = load_appointments()
    
    if appointment_id not in df['appointment_id'].values:
        return f"Appointment ID {appointment_id} not found."
    
    # Update status to cancelled
    idx = df[df['appointment_id'] == appointment_id].index[0]
    df.at[idx, 'status'] = 'cancelled'
    
    save_appointments(df)
    
    return f"Appointment {appointment_id} cancelled successfully."

# -------------------------------
# CHATBOT LOGIC
# -------------------------------
def process_chat_message(patient_id, message):
    """Process natural language message and perform appropriate action"""
    message_lower = message.lower()
    
    # Load doctors for reference
    doctors_df = load_doctors()
    doctors_list = ", ".join(doctors_df['name'].tolist())
    
    # Check for appointment creation
    if any(word in message_lower for word in ['book', 'create', 'make', 'schedule', 'appointment', 'rendez-vous', 'rdv', 'حجز', 'موعد']):
        # Check if doctor name is provided
        doctor_name = None
        for doctor in doctors_df['name']:
            if doctor.lower() in message_lower:
                doctor_name = doctor
                break
        
        if doctor_name:
            # Ask for date
            return f"I can help you book an appointment with {doctor_name}. What date would you like? (format: DD-MM-YYYY)"
        else:
            return f"I can help you book an appointment. Available doctors: {doctors_list}. Which doctor would you like to see?"
    
    # Check for getting appointments
    elif any(word in message_lower for word in ['my appointments', 'get appointments', 'view appointments', 'show appointments', 'list appointments', 'مواعيدي', 'rendez-vous']):
        return get_appointments(patient_id)
    
    # Check for updating appointments
    elif any(word in message_lower for word in ['update', 'change', 'modify', 'reschedule', 'تحديث', 'تغيير']):
        appointments = get_appointments(patient_id)
        if "no appointments" in appointments.lower():
            return "You have no appointments to update."
        return f"To update an appointment, please provide: 1) Appointment ID, 2) New date (DD-MM-YYYY), 3) New time (HH:MM).\n\nYour appointments:\n{appointments}"
    
    # Check for cancelling appointments
    elif any(word in message_lower for word in ['cancel', 'delete', 'remove', 'annuler', 'إلغاء']):
        appointments = get_appointments(patient_id)
        if "no appointments" in appointments.lower():
            return "You have no appointments to cancel."
        return f"To cancel an appointment, please provide the Appointment ID.\n\nYour appointments:\n{appointments}"
    
    # Check for doctor availability
    elif any(word in message_lower for word in ['available', 'availability', 'disponible', 'متاح']):
        return f"Available doctors: {doctors_list}. To check specific availability, please specify which doctor and date."
    
    # Default response
    else:
        return f"I can help you with appointment management. You can:\n1. Book an appointment\n2. View your appointments\n3. Update an appointment\n4. Cancel an appointment\n\nAvailable doctors: {doctors_list}\n\nWhat would you like to do?"

# -------------------------------
# API ENDPOINTS
# -------------------------------
@app.post("/chat")
async def chat_endpoint(chat: ChatMessage):
    """Chat endpoint for natural language interaction"""
    response = process_chat_message(chat.patient_id, chat.message)
    return {"patient_id": chat.patient_id, "response": response}

@app.post("/appointment")
async def appointment_endpoint(req: AppointmentRequest):
    """Direct appointment operations endpoint"""
    if req.action == "create":
        if not all([req.doctor_name, req.date, req.time]):
            return {"error": "Missing required fields for creating appointment"}
        result = create_appointment(req.patient_id, req.doctor_name, req.date, req.time)
    
    elif req.action == "get":
        result = get_appointments(req.patient_id)
    
    elif req.action == "update":
        if not req.appointment_id:
            return {"error": "Appointment ID required for update"}
        result = update_appointment(req.appointment_id, req.new_date, req.new_time)
    
    elif req.action == "cancel":
        if not req.appointment_id:
            return {"error": "Appointment ID required for cancellation"}
        result = cancel_appointment(req.appointment_id)
    
    else:
        return {"error": "Invalid action. Use 'create', 'get', 'update', or 'cancel'"}
    
    return {"success": True, "result": result}

@app.get("/")
async def root():
    return {"message": "Appointment Chatbot API", "endpoints": ["POST /chat", "POST /appointment"]}

# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    print("Starting Simple Appointment Chatbot...")
    print("Available at: http://127.0.0.1:8008")
    print("Endpoints:")
    print("  POST /chat - Natural language chat")
    print("  POST /appointment - Direct appointment operations")
    uvicorn.run(app, host="127.0.0.1", port=8008)
