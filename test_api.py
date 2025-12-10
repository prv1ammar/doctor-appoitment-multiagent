import requests
import json
import time
import subprocess
import sys
import os

def start_server():
    """Start the FastAPI server in background."""
    proc = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8003'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(5)  # wait for server to start
    return proc

def stop_server(proc):
    """Stop the server."""
    proc.terminate()
    proc.wait()

def test_faq():
    """Test FAQ query."""
    url = 'http://127.0.0.1:8003/execute'
    payload = {'id_number': 123, 'messages': 'What are your services?'}
    try:
        response = requests.post(url, json=payload, timeout=30)
        print('FAQ Test:')
        print('  Status Code:', response.status_code)
        print('  Response:', response.json())
        return response.status_code == 200
    except Exception as e:
        print('  Error:', e)
        return False

def test_appointment():
    """Test appointment booking with realistic data."""
    url = 'http://127.0.0.1:8003/execute'
    payload = {
        'id_number': 1234567,
        'messages': 'I want to book an appointment with Dr.Mohamed Tajmouati on 04-12-2025 at 10:00.'
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        print('Appointment Test:')
        print('  Status Code:', response.status_code)
        print('  Response:', response.json())
        return response.status_code == 200
    except Exception as e:
        print('  Error:', e)
        return False

def main():
    print('Starting server...')
    proc = start_server()
    try:
        print('Server started. Running tests...')
        success_faq = test_faq()
        success_app = test_appointment()
        if success_faq and success_app:
            print('\nAll tests passed!')
        else:
            print('\nSome tests failed.')
    finally:
        print('Stopping server...')
        stop_server(proc)

if __name__ == '__main__':
    main()
