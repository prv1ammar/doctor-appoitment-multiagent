#!/usr/bin/env python3
"""Simplified main.py that works without complex agent graph."""

from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json

app = FastAPI()

class UserQuery(BaseModel):
    id_number: int
    messages: str

# Simple rule-based responses
def get_response(user_message: str, patient_id: int) -> str:
    """Simple rule-based response system."""
    user_message_lower = user_message.lower().strip()
    
    # Greetings
    if user_message_lower in ['hi', 'hello', 'hey', 'bonjour', 'salut']:
        return "Hello! I can help you with doctor appointments. You can ask about availability, book appointments, or get patient information."
    
    # Patient information
    elif any(word in user_message_lower for word in ['patient', 'my info', 'information', 'get my']):
        try:
            import pandas as pd
            df = pd.read_csv("data/patients.csv")
            patient = df[df["ID"] == patient_id]
            
            if len(patient) == 0:
                return f"No patient found with ID: {patient_id}"
            
            patient_info = patient.iloc[0]
            return (
                f"Patient ID: {patient_info['ID']}\n"
                f"Name: {patient_info['nom']}\n"
                f"Email: {patient_info['email']}\n"
                f"Phone: {patient_info['telephone']}\n"
                f"Birth Date: {patient_info['date_naissance']}\n"
                f"Gender: {patient_info['sexe']}\n"
                f"Address: {patient_info['addresse']}"
            )
        except Exception as e:
            return f"Error retrieving patient information: {str(e)}"
    
    # Availability check
    elif any(word in user_message_lower for word in ['available', 'availability', 'schedule']):
        if 'dr.' in user_message_lower or 'doctor' in user_message_lower:
            # Extract doctor name (simplified)
            if 'mohamed' in user_message_lower or 'tajmouati' in user_message_lower:
                doctor = "Dr.Mohamed Tajmouati"
            elif 'adil' in user_message_lower:
                doctor = "Dr.Adil Tajmouati"
            elif 'hanane' in user_message_lower or 'louizi' in user_message_lower:
                doctor = "Dr.Hanane Louizi"
            else:
                doctor = "a doctor"
            
            return f"I can check availability for {doctor}. For specific availability, please provide a date (format: DD-MM-YYYY)."
        else:
            return "I can check doctor availability. Please specify which doctor you're interested in."
    
    # Appointment booking
    elif any(word in user_message_lower for word in ['appointment', 'book', 'booking', 'schedule']):
        return "I can help you book an appointment. Please provide: 1) Doctor name, 2) Preferred date and time, 3) Your patient ID."
    
    # FAQ
    elif any(word in user_message_lower for word in ['service', 'faq', 'what', 'help']):
        return "We offer dental services including: Orthodontics, Prosthetics and Implants, Periodontology and Aesthetics. Our specialists have 10-15 years of experience."
    
    # Default
    else:
        return "I can help you with doctor appointments. You can ask about: 1) Patient information, 2) Doctor availability, 3) Booking appointments, 4) Our services."

@app.post("/execute")
def execute_agent(user_input: UserQuery):
    """Simplified endpoint that works without agent graph."""
    try:
        response_text = get_response(user_input.messages, user_input.id_number)
        
        return {
            "messages": [
                {"sender": "user", "content": user_input.messages},
                {"sender": "assistant", "content": response_text}
            ]
        }
    except Exception as e:
        return {
            "messages": [
                {"sender": "user", "content": user_input.messages},
                {"sender": "assistant", "content": f"Error: {str(e)}"}
            ]
        }

@app.get("/")
def read_root():
    return {"message": "Doctor Appointment API (Simplified Version)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8004)
