import os

from fastapi import FastAPI, HTTPException, Request
from aiogram import Bot
from aiogram.types import Update

from bot import dp

app = FastAPI()


@app.get("/")
async def health():
    return {"status": "Lumova webhook is ready"}


@app.post("/")
async def telegram_webhook(request: Request):
    token = os.getenv("LUMOVA_BOT_TOKEN")
    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")

    if not token or not secret:
        raise HTTPException(
            status_code=500,
            detail="Server configuration missing",
        )

    received_secret = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token"
    )

    if received_secret != secret:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        data = await request.json()
        update = Update.model_validate(data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid update")

    telegram_bot = Bot(token=token)

    try:
        await dp.feed_update(telegram_bot, update)
    finally:
        await telegram_bot.session.close()

    return {"ok": True}
