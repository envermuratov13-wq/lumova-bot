from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
async def health():
    return {"status": "GET works"}

@app.post("/")
async def test_post(request: Request):
    data = await request.json()
    return {
        "status": "POST works",
        "received": data
    }
