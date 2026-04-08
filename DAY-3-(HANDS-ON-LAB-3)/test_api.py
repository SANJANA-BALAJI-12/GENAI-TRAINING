import urllib.request
import json

req = urllib.request.Request(
    'http://127.0.0.1:8000/moderate/submit', 
    data=json.dumps({"text": "Hello world this is completely benign."}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    response = urllib.request.urlopen(req)
    print(response.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
