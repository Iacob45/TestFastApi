import requests

headers = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

response = requests.get("http://127.0.0.1:5050/items?count=50", headers=headers)
print(response.json())