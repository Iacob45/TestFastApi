from enum import Enum
import uvicorn
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
import redis
import httpx
import json

app = FastAPI(
    title="Api1",
    description="Test API using dictionary of tools",
    version="0.1"
)

class Category(Enum):
    """Category of an item"""
    TOOLS = "tools"
    CONSUMABLES = "consumables"

class Item(BaseModel):
    """Structure of items"""
    name: str = Field(description="Name of the item")
    price: float = Field(description="Price of the item")
    count: int = Field(description="Number of items")
    id: int = Field(description="Unique identifier of the item")
    category: Category = Field(description="Category of the item")

items = {
    0: Item(name="Hammer", price=9.99, count=20, id=0, category=Category.TOOLS),
    1: Item(name="APliers", price=3.5, count=5, id=1, category=Category.TOOLS),
    2: Item(name="Nails", price=5.99, count=4, id=2, category=Category.CONSUMABLES)
}

Selection = dict[str,str|int|float|Category|None]

#GET------------------------------------------------------------------------
@app.get("/items")
def index() -> dict[str,dict[int, Item]]:
    return {"items":items}

@app.get("/items/{item_id}")
def query_item_by_id(item_id: int = Path(ge=0)) -> Item:
    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"Item with {item_id=} does not exist.")
    return items[item_id]

@app.get("/sth")
def show_test_string() -> str:
    return "something"

@app.get("/testing")
def query_all_items() -> dict[int, Item]:
    return items

@app.get("/chooseitem")
def query_item_by_parameters(
        name: str | None = None,
        price: float | None = Query(default=None,ge=0),
        count: int | None = Query(default=None,ge=0),
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


#POST------------------------------------------------------------------------
@app.post("/items")
def add_item(item: Item) -> dict[str, Item]:

    if item.id in items:
        raise HTTPException(status_code=400, detail=f"Item with {item.id=} already exists.")

    items[item.id] = item
    return {"added":item}


#PUT------------------------------------------------------------------------
@app.put("/items/{item_id}")
def updateoradd(
        item_id: int = Path(ge=0),
        name: str | None = None,
        price: float | None = Query(default=None,ge=0),
        count: int | None = Query(default=None,ge=0),
        category: Category | None = None) -> dict[str, Item]:
    #if item_id not in items:
    #    raise HTTPException(status_code=400, detail=f"Item with {item_id=} does not exist.")
    if all(info is None for info in (name, price, count, category)):
        raise HTTPException(status_code=400, detail=f"No parameters provided.")
    if item_id in items:
        item = items[item_id]
        if name is not None:
            item.name = name
        if price is not None:
            item.price = price
        if count is not None:
            item.name = count
        if category is not None:
            item.category = category
        return {"updated": item}
    elif all(info is not None for info in (name, price, count, category)):
        items[item_id] = Item(name=name, price=price, count=count, id=item_id, category=category)
        return {"added": items[item_id]}
    else:
        raise HTTPException(status_code=400, detail=f"Item with {item_id=} does not exist and not all parameters were added for creating a new Item")


#PATCH------------------------------------------------------------------------
@app.patch("/items/{item_id}",
           responses={
               404: {"description": "Item not found"},
               400: {"description": "No arguments specified"},
           }
)
def update(
        item_id: int = Path(ge=0),
        name: str | None = None,
        price: float | None = Query(default=None,ge=0),
        count: int | None = Query(default=None,ge=0),
        category: Category | None = None) -> dict[str, Item]:
    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"Item with {item_id=} does not exist.")
    if all(info is None for info in (name, price, count, category)):
        raise HTTPException(status_code=400, detail=f"No parameters provided for update.")

    item = items[item_id]
    if name is not None:
        item.name = name
    if price is not None:
        item.price = price
    if count is not None:
        item.name = count
    if category is not None:
        item.category = category

    return {"updated": item}


#DELETE------------------------------------------------------------------------
@app.delete("/items/{item_id}")
def delete_item(item_id: int = Path(ge=0)) -> dict[str, Item]:

    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"Item with {item_id=} does not exist.")

    item = items.pop(item_id)
    return {"deleted": item}


print("Working")





#STEP 2
@app.on_event("startup")
async def startup_event():
    pool = redis.ConnectionPool(host="127.0.0.1", port=int(6379), db=int(0), password="parola divina23^&")
    app.state.redis = redis.Redis(pool)
    app.state.http_client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown():
    app.state.redis.close()

@app.get("/entries")
async def read_item():
    response = await app.state.http_client.get("https://catfact.ninja/fact")
    return response.json()










if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5050)