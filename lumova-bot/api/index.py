
import os

from fastapi import FastAPI, HTTPException, Request
from aiogram import Bot
from aiogram.types import Update

from bot import dp, init_db

TOKEN = os.getenv("LUMOVA_BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET")

app = FastAPI()


@app.get("/")
async def health():
    return {"status": "LUMOVA webhook ready"}


@app.post("/")
async def telegram_webhook(request: Request):
    if not TOKEN or not WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Server configuration missing")

    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        data = await request.json()
        update = Update.model_validate(data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Telegram update")

    init_db()
    bot = Bot(token=TOKEN)
    try:
        await dp.feed_update(bot, update)
    finally:
        await bot.session.close()

    return {"ok": True}
