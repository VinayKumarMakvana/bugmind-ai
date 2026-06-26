import urllib.request
import json

url = "http://localhost:8000/api/v1/auth/register"
data = {"email": "test456@test.com", "password": "password123", "name": "Test User"}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print("Status Code:", response.getcode())
        print("Response:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Error Response:", e.read().decode('utf-8'))
except Exception as e:
    print("Other Error:", str(e))
