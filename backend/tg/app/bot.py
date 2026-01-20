import asyncio
import json
import secrets
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message

from .settings import Settings
from .redis_client import redis_client

settings = Settings()

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

LOGIN_TTL_SECONDS = 300


async def generate_unique_code() -> str:
    for _ in range(10):
        code = secrets.token_hex(3)  # что-то вроде "a1b2c3"
        key = f"login_code:{code}"
        exists = await redis_client.exists(key)
        if not exists:
            return code
    # fallback
    return secrets.token_hex(4)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Для входа на сайт используй команду /login.\n"
        "Я пришлю код, который нужно вставить на сайте."
    )


@router.message(Command("login"))
async def cmd_login(message: Message):
    code = await generate_unique_code()

    tg_user = message.from_user
    data = {
        "telegram_id": tg_user.id,
        "username": tg_user.username,
        "name": tg_user.full_name,
    }

    await redis_client.setex(f"login_code:{code}", LOGIN_TTL_SECONDS, json.dumps(data))
    await message.answer(f"Код для входа: {code}\nДействует {LOGIN_TTL_SECONDS//60} минут(ы).")


async def start_polling():
    await dp.start_polling(bot)