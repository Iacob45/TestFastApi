from enum import Enum
import uvicorn
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
import redis.asyncio as redis
import httpx
import json

app = FastAPI(
    title="FastAPI Redis",
    description="Test API using Redis as database and cache",
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

'''
items = {
    0: Item(name="Hammer", price=9.99, count=20, id=0, category=Category.TOOLS),
    1: Item(name="Pliers", price=3.5, count=5, id=1, category=Category.TOOLS),
    2: Item(name="Nails", price=5.99, count=4, id=2, category=Category.CONSUMABLES)
}
'''

Selection = dict[str,str|int|float|Category|None]


async def insert_item(item: Item):
    key = f"item:{item.id}"
    value = item.model_dump_json()
    return await app.state.redis.set(key,value)

async def update_item(item_id,name,price,count,category):
    key = f"item:{item_id}"
    item_data = await app.state.redis.get(key)
    item_data = json.loads(item_data)
    if name is not None:
        item_data["name"] = name
    if price is not None:
        item_data["price"]= price
    if count is not None:
        item_data["name"] = count
    if category is not None:
        item_data["category"] = category
    item = Item(**item_data)
    value = item.model_dump_json()
    if await app.state.redis.set(key, value) is True:
        return item
    else:
        return False


async def delete_item_by_id(id: int):
    #return await app.state.redis.delete(f"item:{id}")
    item = await app.state.redis.execute_command("GETDEL", f"item:{id}")
    return json.loads(item)
async def exists_item(item: Item):
    return await app.state.redis.exists(f"item:{item.id}")

async def exists_id(id: int):
    return await app.state.redis.exists(f"item:{id}")

async def return_hashes():
    items = []
    async for key in app.state.redis.scan_iter(type=str, match="item:*"):
        value = await app.state.redis.get(key)
        items.append(json.loads(value))
    return items

async def return_hashes_by_params(name,price,count,category):
    items = []
    item = 0
    async for key in app.state.redis.scan_iter(type=str, match="item:*"):
        item = await app.state.redis.get(key)
        item = json.loads(item)
        if all(
            (
                name is None or item["name"] == name,
                price is None or item["price"] == price,
                count is None or item["count"] == count,
                category is None or item["category"] is category
            )
        ) == 1:
            items.append(item)
    return items



async def return_item(id: int):
    item = await app.state.redis.get(f"item:{id}")
    return json.loads(item)


#GET------------------------------------------------------------------------
@app.get("/items")
async def index() -> dict[str,list[dict]]:
    items = await return_hashes()
    return {"items":items}

@app.get("/items/{item_id}")
async def query_item_by_id(item_id: int = Path(ge=0)) -> dict[str,dict]:
    if await exists_id(item_id) == 0:
        raise HTTPException(status_code=404, detail=f"Item with {item_id=} does not exist.")
    item = await return_item(item_id)
    return {f"item with {item_id=}": item}


@app.get("/sth")
def show_test_string() -> str:
    return "something"

@app.get("/testing")
async def query_all_items() -> list[dict]:
    items = await return_hashes()
    return items


@app.get("/chooseitem")
async def query_item_by_parameters(
        name: str | None = None,
        price: float | None = Query(default=None,ge=0),
        count: int | None = Query(default=None,ge=0),
        category: Category | None = None) -> dict[str, dict|list]:

    selection = await return_hashes_by_params(name=name,price=price,count=count,category=category)
    return {
        "query": {"name": name, "price": price, "count": count, "category": category},
        "selection": selection
    }


#POST------------------------------------------------------------------------
@app.post("/items")
async def add_item(item: Item) -> dict[str, Item]:

    if await exists_item(item):
        raise HTTPException(status_code=400, detail=f"Item with {item.id=} already exists.")

    if await insert_item(item):
        return {"added":item}
    else:
        raise HTTPException(status_code=400, detail=f"Something happened, item not added.")


#PUT------------------------------------------------------------------------
@app.put("/items/{item_id}")
async def updateoradd(
        item_id: int = Path(ge=0),
        name: str | None = None,
        price: float | None = Query(default=None,ge=0),
        count: int | None = Query(default=None,ge=0),
        category: Category | None = None) -> dict[str, Item]:
    #if item_id not in items:
    #    raise HTTPException(status_code=400, detail=f"Item with {item_id=} does not exist.")
    if all(info is None for info in (name, price, count, category)):
        raise HTTPException(status_code=400, detail=f"No parameters provided.")
    if await exists_id(item_id):
        item = await update_item(item_id=item_id, name=name, price=price, count=count, category=category)
        if item is not None:
            return {"updated": item}
        else:
            raise HTTPException(status_code=400, detail=f"Something happened, item not updated.")
    elif all(info is not None for info in (name, price, count, category)):
        item = Item(name=name, price=price, count=count, id=item_id, category=category)
        if await insert_item(item):
            return {"added": item}
        else:
            raise HTTPException(status_code=400, detail=f"Something happened, item not added.")
    else:
        raise HTTPException(status_code=400, detail=f"Item with {item_id=} does not exist and not all parameters were added for creating a new Item")


#PATCH------------------------------------------------------------------------
@app.patch("/items/{item_id}")
async def update(
        item_id: int = Path(ge=0),
        name: str | None = None,
        price: float | None = Query(default=None,ge=0),
        count: int | None = Query(default=None,ge=0),
        category: Category | None = None):
    if await exists_id(item_id) == 0:
        raise HTTPException(status_code=404, detail=f"Item with {item_id=} does not exist.")
    if all(info is None for info in (name, price, count, category)):
        raise HTTPException(status_code=400, detail=f"No parameters provided for update.")

    item = await update_item(item_id=item_id, name=name, price=price, count=count, category=category)

    if item is not None:
        return {"updated":item}
    else:
        raise HTTPException(status_code=400, detail=f"Something happened, item not updated.")



#DELETE------------------------------------------------------------------------
@app.delete("/items/{item_id}")
async def delete_item(item_id: int = Path(ge=0)) -> dict[str, Item]:

    if await exists_id(item_id) == 0:
        raise HTTPException(status_code=400, detail=f"The item with {item_id=} doesn't exist.")

    item = await delete_item_by_id(item_id)
    if item is not None:
        return {"deleted": item}
    else:
        raise HTTPException(status_code=400, detail=f"Something happened, item was not deleted.")


print("Working")





#STEP 2 - CACHING
@app.on_event("startup")
async def startup_event():
    pool = redis.ConnectionPool(host="127.0.0.1", port=int(6379), db=int(1), password="parola divina23^&")
    app.state.redis = redis.Redis(connection_pool=pool)
    app.state.http_client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown():
    app.state.redis.close()

#CATFACT
@app.get("/catfact")
async def read_item():
    value = app.state.redis.get("catfact")

    if value is None:
        response = await app.state.http_client.get("https://catfact.ninja/fact")
        value = response.json()
        data_str = json.dumps(value)
        app.state.redis.set("catfact", data_str, ex=1800)
        return value

    return json.loads(value)

@app.get("/fish/{species}")
async def read_fish(species: str):
    value = app.state.redis.get(f"fish_{species}")

    if value is None:
        response = await app.state.http_client.get(f"https://www.fishwatch.gov/api/species/{species}")
        if response.text == "":
            raise HTTPException(status_code=404, detail=f"Species not found")
        value = response.json()
        data_str = json.dumps(value)
        app.state.redis.set(f"fish_{species}", data_str, ex=1800)
        return value

    return json.loads(value)








if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5050)