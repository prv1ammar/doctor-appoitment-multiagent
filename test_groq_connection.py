import os
import sys
from groq import Groq
import socket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test DNS resolution
print("Testing DNS resolution...")
try:
    ip = socket.gethostbyname('api.groq.com')
    print(f"  DNS resolved to: {ip}")
except Exception as e:
    print(f"  DNS error: {e}")

# Test with IPv4 only
print("\nTesting with IPv4 only...")
try:
    # Force IPv4
    socket.getaddrinfo = lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("  No API key found")
        sys.exit(1)
    
    print(f"  API Key: {api_key[:10]}...")
    client = Groq(api_key=api_key)
    
    # Try with short timeout
    import httpx
    client._client.timeout = httpx.Timeout(10.0)
    
    response = client.chat.completions.create(
        messages=[{'role': 'user', 'content': 'Hello'}],
        model='llama-3.1-8b-instant',
        max_tokens=10
    )
    print(f"  Success! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {e}")

# Test with custom base URL (if available)
print("\nTesting alternative approach...")
try:
    api_key = os.getenv('GROQ_API_KEY')
    client = Groq(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",  # Try explicit base URL
        timeout=10.0
    )
    
    response = client.chat.completions.create(
        messages=[{'role': 'user', 'content': 'Hello'}],
        model='llama-3.1-8b-instant',
        max_tokens=10
    )
    print(f"  Success with explicit base URL! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {e}")
    
# Test raw HTTP request
print("\nTesting raw HTTP request...")
try:
    import requests
    api_key = os.getenv('GROQ_API_KEY')
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'llama-3.1-8b-instant',
        'messages': [{'role': 'user', 'content': 'Hello'}],
        'max_tokens': 10
    }
    
    response = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers=headers,
        json=data,
        timeout=10
    )
    print(f"  HTTP Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  Success! Response: {response.json()['choices'][0]['message']['content']}")
    else:
        print(f"  Error: {response.text}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {e}")
