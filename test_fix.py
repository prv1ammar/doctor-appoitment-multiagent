import subprocess
import time
import requests
import json
import os

# Kill any python processes first
os.system('taskkill /F /IM python.exe 2>nul')
time.sleep(2)

# Start server
print('Starting server...')
proc = subprocess.Popen(['python', '-m', 'uvicorn', 'main:app', '--reload', '--port', '8003'], 
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(5)

url = 'http://127.0.0.1:8003/execute'

# Test 1: Simple greeting
print('\nTest 1: Simple greeting "hi"')
payload1 = {'id_number': 2, 'messages': 'hi'}
try:
    response1 = requests.post(url, json=payload1, timeout=20)
    print(f'Status: {response1.status_code}')
    if response1.status_code == 200:
        print('Response:', json.dumps(response1.json(), indent=2))
    else:
        print('Error:', response1.text[:200])
except Exception as e:
    print(f'Request error: {e}')

# Test 2: Specific query  
print('\nTest 2: Specific query about services')
payload2 = {'id_number': 2, 'messages': 'What are your services?'}
try:
    response2 = requests.post(url, json=payload2, timeout=20)
    print(f'Status: {response2.status_code}')
    if response2.status_code == 200:
        print('Response:', json.dumps(response2.json(), indent=2))
    else:
        print('Error:', response2.text[:200])
except Exception as e:
    print(f'Request error: {e}')

print('\nStopping server...')
proc.terminate()
proc.wait()
