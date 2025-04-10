from enum import Enum
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Category(Enum):
    TOOLS = "tools"
    CONSUMABLES = "consumables"

class Item(BaseModel):
    name: str
    price: float
    count: int
    id: int
    category: Category

items = {
    0: Item(name="Hammer", price=9.99, count=20, id=0, category=Category.TOOLS),
    1: Item(name="APliers", price=3.5, count=5, id=1, category=Category.TOOLS),
    2: Item(name="Nails", price=5.99, count=4, id=2, category=Category.CONSUMABLES)
}

Selection = dict[str,str|int|float|Category|list|dict|None]



@app.get("/")
def index() -> dict[str,dict[int, Item]]:
    return {"items":items}

@app.get("/items/{item_id}")
def query_item_by_id(item_id: int) -> Item:
    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"Item with {item_id} does not exist")
    return items[item_id]


@app.get("/sth")
def show_test_string() -> str:
    return "something"

@app.get("/testing")
def query_all_items() -> dict[int, Item]:
    return items

@app.get("/items")
def query_item_by_parameters(
        name: str | None = None,
        price: float | None = None,
        count: int | None = None,
        category: Category | None = None) -> dict[str, list | Selection]:
    def check_item(item: Item) -> bool:
        return all(
            (
                name is None or item.name == name,
                price is None or item.price == price,
                count is None or item.count == count,
                category is None or item.category is category
            )
        )
    selection = [item for item in items.values() if check_item(item)]
    return {
        "query": {"name": name, "price": price, "count": count, "category": category},
        "selection": selection
    }

print("Working")



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5050)