import os
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

TOKEN = os.getenv("8921151945:AAF6SrInfhTl1ETqHOb5tmxehGgkaiIOKOM")
LOG_CHANNEL_ID = os.getenv("-1003623768533")

SITE_URL = "https://lumova-site.vercel.app/"

if not TOKEN:
    raise RuntimeError("Не задана переменная LUMOVA_BOT_TOKEN")

if not LOG_CHANNEL_ID:
    raise RuntimeError("Не задана переменная LUMOVA_LOG_CHANNEL_ID")

LOG_CHANNEL_ID = int(LOG_CHANNEL_ID)

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def log_event(bot: Bot, event: str, user) -> None:
    """Отправляет событие в закрытый Telegram-канал."""
    username = f"@{user.username}" if user.username else "нет"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    text = (
        "📊 Lumova — событие\n\n"
        f"Событие: {event}\n"
        f"Telegram ID: {user.id}\n"
        f"Username: {username}\n"
        f"Время: {timestamp}"
    )

    try:
        await bot.send_message(LOG_CHANNEL_ID, text)
    except Exception as error:
        print(f"Ошибка записи в канал: {error}")


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏢 Расчётный счёт",
                    callback_data="rko",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 Банковские карты",
                    callback_data="cards",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚖️ Сравнить предложения",
                    callback_data="compare",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌐 Сайт Lumova",
                    url=SITE_URL,
                )
            ],
        ]
    )


def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Главное меню",
                    callback_data="menu",
                )
            ]
        ]
    )


@dp.message(CommandStart())
async def start(message: Message, bot: Bot):
    await log_event(bot, "Запуск бота /start", message.from_user)

    await message.answer(
        "👋 Добро пожаловать в Lumova!\n\n"
        "Lumova помогает находить банковские продукты "
        "и переходить к оформлению через предложения партнёров.\n\n"
        "Выберите нужный раздел:",
        reply_markup=main_menu(),
    )


@dp.message(Command("help"))
async def help_command(message: Message, bot: Bot):
    await log_event(bot, "Открыта помощь", message.from_user)

    await message.answer(
        "ℹ️ Lumova — сервис для поиска банковских предложений.\n\n"
        "Выберите интересующий раздел в главном меню."
    )


@dp.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery, bot: Bot):
    await log_event(bot, "Возврат в главное меню", callback.from_user)

    await callback.message.edit_text(
        "Выберите нужный раздел Lumova:",
        reply_markup=main_menu(),
    )
    await callback.answer()


@dp.callback_query(F.data == "rko")
async def rko_callback(callback: CallbackQuery, bot: Bot):
    await log_event(bot, "Открыт раздел РКО", callback.from_user)

    await callback.message.edit_text(
        "🏢 Расчётный счёт для бизнеса\n\n"
        "Здесь будут представлены предложения банков "
        "для ИП и ООО.\n\n"
        "Каталог предложений сейчас готовится.",
        reply_markup=back_menu(),
    )
    await callback.answer()


@dp.callback_query(F.data == "cards")
async def cards_callback(callback: CallbackQuery, bot: Bot):
    await log_event(bot, "Открыт раздел банковских карт", callback.from_user)

    await callback.message.edit_text(
        "💳 Банковские карты\n\n"
        "Здесь будут собраны доступные банковские карты "
        "с описанием условий и ссылками для оформления.\n\n"
        "Каталог предложений сейчас готовится.",
        reply_markup=back_menu(),
    )
    await callback.answer()


@dp.callback_query(F.data == "compare")
async def compare_callback(callback: CallbackQuery, bot: Bot):
    await log_event(bot, "Открыт раздел сравнения", callback.from_user)

    await callback.message.edit_text(
        "⚖️ Сравнение предложений\n\n"
        "В этом разделе можно будет сравнивать банковские "
        "продукты по условиям и преимуществам.\n\n"
        "Раздел сейчас готовится.",
        reply_markup=back_menu(),
    )
    await callback.answer()


@dp.message()
async def other_messages(message: Message):
    await message.answer(
        "Выберите раздел в меню Lumova:",
        reply_markup=main_menu(),
    )
