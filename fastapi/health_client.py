import requests

url = "http://127.0.0.1:8000/health-check"

payload = {
    "devices": [
        {
            "device_type": "cisco_ios",
            "ip": "192.168.177.131",
            "username": "ramesh",
            "password": "cisco123",
            "secret": "admin"
        },
        {
            "device_type": "cisco_ios",
            "ip": "192.168.177.132",
            "username": "phani1",
            "password": "phani123",
            "secret": "cisco123"
        },
        {
            "device_type": "cisco_ios",
            "ip": "192.168.177.133",
            "username": "phani",
            "password": "cisco123",
            "secret": "admin"
        }
    ]
}

response = requests.post(url, json=payload)
response.raise_for_status()

print(response.json())