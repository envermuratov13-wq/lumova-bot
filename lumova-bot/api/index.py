import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def health():
    return {
        "status": "Lumova diagnostic",
        "token_exists": bool(os.getenv("LUMOVA_BOT_TOKEN")),
        "channel_exists": bool(os.getenv("LUMOVA_LOG_CHANNEL_ID")),
        "secret_exists": bool(os.getenv("TELEGRAM_WEBHOOK_SECRET")),
    }
