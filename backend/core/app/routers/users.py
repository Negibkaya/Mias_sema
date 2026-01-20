from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db, get_current_user
from ..models import User
from ..schemas import UserPublic, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def me(current: User = Depends(get_current_user)):
    return current


@router.put("/me", response_model=UserPublic)
async def update_me(
    patch: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if patch.name is not None:
        current.name = patch.name
    if patch.bio is not None:
        current.bio = patch.bio
    if patch.skills is not None:
        current.skills = [s.model_dump() for s in patch.skills]

    await db.commit()
    await db.refresh(current)
    return current


@router.get("/", response_model=list[UserPublic])
async def list_users(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).order_by(User.id.desc()))
    return list(res.scalars().all())


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return user