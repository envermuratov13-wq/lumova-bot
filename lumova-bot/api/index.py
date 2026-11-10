import os

from fastapi import FastAPI, HTTPException, Request
from aiogram import Bot
from aiogram.types import Update

from bot import dp

TOKEN = os.getenv("8921151945:AAF6SrInfhTl1ETqHOb5tmxehGgkaiIOKOM")
WEBHOOK_SECRET = os.getenv("RKODENGIZHEKADIMAENVERAIDER77bazaDANIH")

app = FastAPI()


@app.get("/")
async def health():
    return {"status": "Lumova webhook is ready"}


@app.post("/")
async def telegram_webhook(request: Request):
    if not TOKEN or not WEBHOOK_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Server configuration missing",
        )

    secret = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token"
    )

    if secret != WEBHOOK_SECRET:
        raise HTTPException(
            status_code=403,
            detail="Forbidden",
        )

    try:
        data = await request.json()
        update = Update.model_validate(data)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid Telegram update",
        )

    telegram_bot = Bot(token=TOKEN)

    try:
        await dp.feed_update(telegram_bot, update)
    finally:
        await telegram_bot.session.close()

    return {"ok": True}
