import requests

print("Adding an item:")
print(requests.post("http://127.0.0.1:5050/items", json={"name": "Screwdriver", "price": 3.99, "count": 10, "id": 3, "category": "tools"}).json())
print(requests.get("http://127.0.0.1:5050/items").json())
print()

print("Updating an item:")
print(requests.put("http://127.0.0.1:5050/items/3?category=consumables").json())
print(requests.get("http://127.0.0.1:5050/items").json())
print()

print("Deleting an item:")
print(requests.delete("http://127.0.0.1:5050/items/3").json())
print(requests.get("http://127.0.0.1:5050/items").json())
print()

