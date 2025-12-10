import subprocess
import time
import requests

# Start server
print('Starting server...')
proc = subprocess.Popen(['python', '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8003'], 
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(5)

print('Testing API with message "hi"...')
try:
    r = requests.post('http://127.0.0.1:8003/execute', json={'id_number': 2, 'messages': 'hi'}, timeout=20)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        print('Success! Response:', r.json())
    else:
        print('Error:', r.text[:500])
except Exception as e:
    print(f'Request error: {e}')

print('Stopping server...')
proc.terminate()
proc.wait()
