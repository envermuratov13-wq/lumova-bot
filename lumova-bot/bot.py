
import asyncio
import os
import sqlite3
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

TOKEN = os.getenv("LUMOVA_BOT_TOKEN")

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "lumova.db"

dp = Dispatcher()


def init_db():
    """Создаёт базу и таблицу пользователей, если их ещё нет."""
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                full_name TEXT,
                age INTEGER,
                step TEXT NOT NULL DEFAULT 'name',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def get_user(telegram_id: int):
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        row = db.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,),
        ).fetchone()
        return dict(row) if row else None


def create_user(telegram_id: int):
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """
            INSERT OR IGNORE INTO users (telegram_id, step)
            VALUES (?, 'name')
            """,
            (telegram_id,),
        )


def update_user(telegram_id: int, **fields):
    allowed = {"full_name", "age", "step"}
    if not fields or not set(fields).issubset(allowed):
        raise ValueError("Недопустимые поля пользователя")

    columns = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [telegram_id]

    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            f"UPDATE users SET {columns} WHERE telegram_id = ?",
            values,
        )


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏢 Подобрать РКО",
                    callback_data="rko",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 Подобрать карту",
                    callback_data="cards",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚖️ Сравнить банки",
                    callback_data="compare",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌐 Открыть сайт LUMOVA",
                    url="https://example.com",
                )
            ],
        ]
    )


def profile_message(user):
    return (
        "✦ LUMOVA\n\n"
        "Помогаем разобраться в банковских продуктах "
        "для бизнеса и повседневных расходов.\n\n"
        f"Имя: {user['full_name']}\n"
        f"Возраст: {user['age']}\n\n"
        "Выбери, что тебя интересует:"
    )


@dp.message(CommandStart())
async def start(message: Message):
    telegram_id = message.from_user.id
    user = get_user(telegram_id)

    if user is None:
        create_user(telegram_id)
        await message.answer(
            "✦ Добро пожаловать в LUMOVA!\n\n"
            "Перед началом заполним короткую анкету.\n"
            "ФИО нужно для обработки заявки. "
            "Не отправляй паспортные данные, банковские "
            "пароли или номера карт.\n\n"
            "Напиши свои фамилию, имя и отчество."
        )
        return

    if user["step"] == "name":
        await message.answer("Напиши свои фамилию, имя и отчество.")
        return

    if user["step"] == "age":
        await message.answer("Сколько тебе полных лет? Введи число.")
        return

    if user["step"] == "age_check":
        await message.answer(
            "Анкета сохранена, но продолжение оформления "
            "нужно сверить с возрастными условиями "
            "конкретной партнёрской программы."
        )
        return

    await message.answer(
        profile_message(user),
        reply_markup=main_menu(),
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Используй /start, чтобы открыть главное меню LUMOVA.\n"
        "Если анкета ещё не заполнена, бот предложит закончить её."
    )


@dp.message(F.text)
async def profile_steps(message: Message):
    telegram_id = message.from_user.id
    user = get_user(telegram_id)

    # Если пользователь ещё не начал анкету, сначала запускаем её.
    if user is None:
        create_user(telegram_id)
        await message.answer(
            "Добро пожаловать в LUMOVA!\n\n"
            "Напиши свои фамилию, имя и отчество."
        )
        return

    if user["step"] == "name":
        full_name = " ".join(message.text.split())

        if len(full_name) < 5 or len(full_name) > 150:
            await message.answer(
                "Проверь ФИО и введи его ещё раз."
            )
            return

        update_user(
            telegram_id,
            full_name=full_name,
            step="age",
        )

        await message.answer(
            "Спасибо! Теперь укажи свой возраст "
            "в полных годах — только число."
        )
        return

    if user["step"] == "age":
        raw_age = message.text.strip()

        if not raw_age.isdigit():
            await message.answer(
                "Введи возраст числом, например: 25."
            )
            return

        age = int(raw_age)

        if age < 1 or age > 120:
            await message.answer(
                "Проверь возраст и введи число от 1 до 120."
            )
            return

        # Для этапов оформления ИП и банковских продуктов
        # нельзя автоматически допускать несовершеннолетних.
        if age < 18:
            update_user(
                telegram_id,
                age=age,
                step="age_check",
            )
            await message.answer(
                "Спасибо за ответы!\n\n"
                "Оформление ИП и участие в партнёрских "
                "программах могут иметь возрастные ограничения. "
                "Поэтому дальнейшие шаги оформления пока "
                "недоступны. Проверь официальные условия "
                "соответствующей программы."
            )
            return

        update_user(
            telegram_id,
            age=age,
            step="done",
        )

        user = get_user(telegram_id)
        await message.answer(
            "Анкета заполнена.\n\n" + profile_message(user),
            reply_markup=main_menu(),
        )
        return

    if user["step"] == "age_check":
        await message.answer(
            "Продолжение оформления зависит от официальных "
            "возрастных требований программы."
        )
        return

    await message.answer(
        "Выбери нужный раздел в меню:",
        reply_markup=main_menu(),
    )


@dp.callback_query(F.data == "rko")
async def rko_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Самозанятый",
                    callback_data="rko_self",
                )
            ],
            [
                InlineKeyboardButton(
                    text="ИП",
                    callback_data="rko_ip",
                )
            ],
            [
                InlineKeyboardButton(
                    text="ООО",
                    callback_data="rko_ooo",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ В меню",
                    callback_data="menu",
                )
            ],
        ]
    )

    await callback.message.answer(
        "🏢 Для кого подбираем расчётный счёт?",
        reply_markup=keyboard,
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("rko_"))
async def rko_type(callback: CallbackQuery):
    business_type = {
        "rko_self": "самозанятого",
        "rko_ip": "ИП",
        "rko_ooo": "ООО",
    }.get(callback.data, "бизнеса")

    await callback.message.answer(
        f"Подберём варианты РКО для: {business_type}.\n\n"
        "Перед выбором нужно проверить тарифы, стоимость "
        "обслуживания, комиссии и условия банка на его "
        "официальном сайте.\n\n"
        "Персональные предложения и ссылки появятся "
        "после настройки партнёрских условий."
    )
    await callback.answer()


@dp.callback_query(F.data == "cards")
async def cards_menu(callback: CallbackQuery):
    await callback.message.answer(
        "💳 Раздел банковских карт\n\n"
        "Здесь будут сравнение условий, стоимость "
        "обслуживания и возможности карт.\n\n"
        "Актуальные условия проверяй на официальном сайте "
        "банка. Одобрение продукта не гарантируется."
    )
    await callback.answer()


@dp.callback_query(F.data == "compare")
async def compare_menu(callback: CallbackQuery):
    await callback.message.answer(
        "⚖️ Сравнение банков\n\n"
        "Здесь будут собраны проверенные условия банков, "
        "комиссии, тарифы и ссылки на официальные источники.\n\n"
        "Сравнение будет добавлено после проверки актуальных "
        "предложений."
    )
    await callback.answer()


@dp.callback_query(F.data == "menu")
async def back_to_menu(callback: CallbackQuery):
    user = get_user(callback.from_user.id)

    if not user or user["step"] != "done":
        await callback.message.answer(
            "Сначала заверши анкету через /start."
        )
    else:
        await callback.message.answer(
            "Главное меню LUMOVA:",
            reply_markup=main_menu(),
        )

    await callback.answer()


async def main():
    if not TOKEN:
        raise RuntimeError(
            "Не задан LUMOVA_BOT_TOKEN. "
            "Установи токен в PowerShell перед запуском."
        )

    init_db()
    bot = Bot(token=TOKEN)

    print("LUMOVA запущен. Для остановки нажми Ctrl+C.")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
