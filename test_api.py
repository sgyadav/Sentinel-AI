import requests
import sys

endpoints = [
    ('GET', '/health', None),
    ('POST', '/auth/login', {'username': 'admin', 'password': 'Admin1234'}),
    ('GET', '/employees', None),
    ('GET', '/devices', None),
    ('GET', '/assignments', None),
    ('GET', '/threats', None),
    ('GET', '/dashboard', None),
    ('GET', '/employee-monitoring', None),
    ('GET', '/settings', None),
    ('GET', '/usb-events', None),
    ('GET', '/processes/live', None),
    ('GET', '/notifications', None),
]

base = 'http://127.0.0.1:8000'

print("\n=== API ENDPOINT TEST ===\n")
for method, path, data in endpoints:
    try:
        if method == 'GET':
            r = requests.get(f'{base}{path}', timeout=3)
        else:
            r = requests.post(f'{base}{path}', json=data, timeout=3)
        
        status = 'PASS' if r.status_code == 200 else f'FAIL-{r.status_code}'
        print(f'[{status}] {method:4} {path}')
    except Exception as e:
        print(f'[ERR]  {method:4} {path} - {str(e)[:40]}')

print("\n=== TEST COMPLETE ===\n")
