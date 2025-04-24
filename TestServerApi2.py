import requests

print("Index:")
print(requests.get("http://127.0.0.1:5049/").json())
print()