from fastapi import FastAPI
import uvicorn

app = FastAPI()

# GET, POST, PUT, DELETE
@app.get('/')
def index():
    return {"message": "Hello World"}

@app.get('/calculation')
async def calculation():
    await requests

    return ""




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5049)