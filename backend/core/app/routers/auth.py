from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from ..deps import get_db
from ..models import User
from ..schemas import LoginCompleteIn, TokenOut
from ..security import create_access_token
from ..main import settings

router = APIRouter()


@router.post("/telegram/complete", response_model=TokenOut)
async def telegram_complete(payload: LoginCompleteIn, db: AsyncSession = Depends(get_db)):
    # 1) проверяем код в tg-service
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{settings.TG_SERVICE_URL}/verify-code", json={"code": payload.code})
    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid/expired code")
    data = r.json()
    telegram_id = int(data["telegram_id"])
    username = data.get("username")
    name = data.get("name")

    # 2) upsert user
    res = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = res.scalar_one_or_none()
    if not user:
        user = User(telegram_id=telegram_id, username=username, name=name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # обновим username/name, если пришло
        if username and user.username != username:
            user.username = username
        if name and user.name != name:
            user.name = name
        await db.commit()

    token = create_access_token(
        {"user_id": user.id, "telegram_id": telegram_id},
        secret=settings.JWT_SECRET,
        expires_minutes=settings.JWT_EXPIRE_MINUTES,
    )
    return TokenOut(access_token=token)