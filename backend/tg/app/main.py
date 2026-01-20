import asyncio
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .bot import start_polling, bot
from .redis_client import redis_client

app = FastAPI(title="tg-service")


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(start_polling())


class VerifyIn(BaseModel):
    code: str


@app.post("/verify-code")
async def verify_code(payload: VerifyIn):
    key = f"login_code:{payload.code}"
    raw = await redis_client.get(key)
    if not raw:
        raise HTTPException(status_code=401, detail="Invalid/expired code")
    await redis_client.delete(key)
    return json.loads(raw)


class NotifyIn(BaseModel):
    telegram_id: int
    text: str


@app.post("/notify")
async def notify(payload: NotifyIn):
    try:
        await bot.send_message(chat_id=payload.telegram_id, text=payload.text)
    except Exception:
        return {"ok": False}
    return {"ok": True}