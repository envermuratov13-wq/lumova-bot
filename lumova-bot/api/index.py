@app.get("/")
async def health():
    return {
        "status": "GET works",
        "routes": [
            {
                "path": route.path,
                "methods": list(route.methods or [])
            }
            for route in app.routes
        ]
    }
