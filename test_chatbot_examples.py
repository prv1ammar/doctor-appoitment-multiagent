#!/usr/bin/env python3
"""Example conversations to test the chatbot functionality."""

import requests
import time
import sys

API_URL = "http://127.0.0.1:8003/execute"

def test_conversation(patient_id, messages, description):
    """Test a single conversation turn."""
    print(f"\n{'='*60}")
    print(f"Test: {description}")
    print(f"Patient ID: {patient_id}")
    print(f"User: {messages}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            API_URL,
            json={"id_number": patient_id, "messages": messages},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("Response:")
            for msg in result.get("messages", []):
                if isinstance(msg, dict):
                    sender = msg.get("sender", "unknown")
                    content = msg.get("content", "")
                    print(f"  {sender}: {content}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

def main():
    """Run example conversations."""
    print("Doctor Appointment Chatbot - Example Conversations")
    print("=" * 60)
    
    # Wait a moment for user to read
    time.sleep(1)
    
    # Example 1: Simple greeting
    test_conversation(
        patient_id=1,
        messages="Hello",
        description="Simple greeting (should go to FAQ agent)"
    )
    
    # Example 2: Check availability
    test_conversation(
        patient_id=2,
        messages="Is Dr. Mohamed Tajmouati available tomorrow?",
        description="Check doctor availability"
    )
    
    # Example 3: Patient information
    test_conversation(
        patient_id=3,
        messages="Get my patient information",
        description="Retrieve patient info using patient management agent"
    )
    
    # Example 4: Check patient ID
    test_conversation(
        patient_id=999,
        messages="Check if patient ID 5 exists",
        description="Check patient ID existence"
    )
    
    # Example 5: FAQ question
    test_conversation(
        patient_id=4,
        messages="What are your services?",
        description="FAQ question about services"
    )
    
    # Example 6: Specific time availability
    test_conversation(
        patient_id=5,
        messages="Is Dr. Adil Tajmouati available on 05-12-2025 at 09:00?",
        description="Check specific time slot availability"
    )
    
    # Example 7: Create new patient (this would fail without proper data)
    test_conversation(
        patient_id=6,
        messages="I want to create a new patient record",
        description="Patient creation request"
    )
    
    # Example 8: Check specialization availability
    test_conversation(
        patient_id=7,
        messages="Which orthodontists are available next week?",
        description="Check availability by specialization"
    )
    
    print("\n" + "=" * 60)
    print("Note: To run these tests, make sure the server is running:")
    print("1. Start the backend: python -m uvicorn main:app --host 127.0.0.1 --port 8003")
    print("2. Run this test: python test_chatbot_examples.py")
    print("=" * 60)

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:8003/docs", timeout=2)
        if response.status_code == 200:
            print("Server is running. Starting tests...")
            main()
        else:
            print("Server returned status code:", response.status_code)
            print("Please start the server first.")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Server is not running. Please start it first:")
        print("python -m uvicorn main:app --host 127.0.0.1 --port 8003")
        sys.exit(1)
