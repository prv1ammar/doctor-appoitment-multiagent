#!/usr/bin/env python3
"""Test the simplified API."""

import requests
import time

def test_simple_api():
    """Test the simplified API."""
    print("Testing simplified API...")
    
    # Start the server (in background)
    import subprocess
    import sys
    import os
    
    # Kill any existing server on port 8004
    try:
        requests.get("http://127.0.0.1:8004/", timeout=1)
        print("Server already running on port 8004")
    except:
        # Start server
        print("Starting server on port 8004...")
        server_process = subprocess.Popen(
            [sys.executable, "main_simple.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)  # Wait for server to start
    
    # Test cases
    test_cases = [
        (1, "hello", "greeting"),
        (2, "get my patient information", "patient info"),
        (3, "is dr. mohamed available?", "availability"),
        (4, "book an appointment", "appointment"),
        (5, "what are your services?", "services"),
    ]
    
    for patient_id, message, description in test_cases:
        print(f"\nTest: {description}")
        print(f"Patient ID: {patient_id}, Message: {message}")
        
        try:
            response = requests.post(
                "http://127.0.0.1:8004/execute",
                json={"id_number": patient_id, "messages": message},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result['messages'][1]['content'][:50]}...")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Try to kill server
    try:
        server_process.terminate()
        server_process.wait()
    except:
        pass
    
    print("\n✅ Simplified API test complete!")

if __name__ == "__main__":
    test_simple_api()
