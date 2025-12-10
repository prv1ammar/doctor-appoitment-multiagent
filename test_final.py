import subprocess
import time
import sys
import requests

# Start server with output
proc = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8003'], 
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# Wait for server to start
time.sleep(5)

print('Server started. Testing with "hi"...')
try:
    r = requests.post('http://127.0.0.1:8003/execute', json={'id_number': 2, 'messages': 'hi'}, timeout=20)
    print(f'Status: {r.status_code}')
    print(f'Response: {r.json()}')
except Exception as e:
    print(f'Error: {e}')

print('\nTesting with "What are your services?"...')
try:
    r2 = requests.post('http://127.0.0.1:8003/execute', json={'id_number': 2, 'messages': 'What are your services?'}, timeout=20)
    print(f'Status: {r2.status_code}')
    print(f'Response: {r2.json()}')
except Exception as e:
    print(f'Error: {e}')

proc.terminate()
proc.wait()
