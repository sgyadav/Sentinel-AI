import requests
import traceback

try:
    print("Testing /devices endpoint...")
    r = requests.get('http://127.0.0.1:8000/devices')
    print(f'Status: {r.status_code}')
    print(f'Headers: {r.headers}')
    print(f'Content: {r.text}')
except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
