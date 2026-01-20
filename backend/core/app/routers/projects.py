from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import httpx

from ..deps import get_db, get_current_user
from ..models import Project, User, ProjectMember
from ..schemas import ProjectCreate, ProjectPublic, ProjectUpdate, ProjectMemberPublic
from ..main import settings

router = APIRouter()


@router.post("/", response_model=ProjectPublic)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
):
    p = Project(
        name=payload.name,
        description=payload.description,
        roles=[r.model_dump() for r in payload.roles] if payload.roles else None,
        owner_id=current.id,
    )
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@router.get("/", response_model=list[ProjectPublic])
async def list_projects(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Project).order_by(Project.id.desc()))
    return list(res.scalars().all())


@router.get("/{project_id}", response_model=ProjectPublic)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Project).where(Project.id == project_id))
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    return p


@router.patch("/{project_id}", response_model=ProjectPublic)
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
):
    res = await db.execute(select(Project).where(Project.id == project_id))
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    if p.owner_id != current.id:
        raise HTTPException(status_code=403, detail="Only owner can edit")

    if payload.name is not None:
        p.name = payload.name
    if payload.description is not None:
        p.description = payload.description
    if payload.roles is not None:
        p.roles = [r.model_dump() for r in payload.roles]

    await db.commit()
    await db.refresh(p)
    return p


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
):
    res = await db.execute(select(Project).where(Project.id == project_id))
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    if p.owner_id != current.id:
        raise HTTPException(status_code=403, detail="Only owner can delete")

    await db.execute(delete(Project).where(Project.id == project_id))
    await db.commit()
    return {"ok": True}


@router.get("/{project_id}/members", response_model=list[ProjectMemberPublic])
async def list_members(project_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.members).selectinload(ProjectMember.user))
    )
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")

    # Возвращаем участников с их ролями
    result = []
    for m in p.members:
        user_data = {
            "id": m.user.id,
            "telegram_id": m.user.telegram_id,
            "username": m.user.username,
            "name": m.user.name,
            "skills": m.user.skills,
            "bio": m.user.bio,
            "role_name": m.role_name,
        }
        result.append(user_data)
    return result


# ИЗМЕНЕНО: добавление участника с указанием роли
@router.post("/{project_id}/members/{user_id}")
async def add_member(
    project_id: int,
    user_id: int,
    role_name: str = None,  # query parameter
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
):
    res = await db.execute(select(Project).where(Project.id == project_id))
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    if p.owner_id != current.id:
        raise HTTPException(status_code=403, detail="Only owner can add members")

    res = await db.execute(select(User).where(User.id == user_id))
    u = res.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем существование
    res = await db.execute(
        select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
    )
    existing = res.scalar_one_or_none()
    if existing:
        # Обновляем роль если передана
        if role_name:
            existing.role_name = role_name
            await db.commit()
        return {"ok": True, "already": True}

    db.add(ProjectMember(project_id=project_id, user_id=user_id, role_name=role_name))
    await db.commit()

    # notify
    role_text = f" на роль '{role_name}'" if role_name else ""
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(
            f"{settings.TG_SERVICE_URL}/notify",
            json={"telegram_id": u.telegram_id, "text": f"Вас добавили в проект: {p.name}{role_text}"},
        )

    return {"ok": True}


@router.delete("/{project_id}/members/{user_id}")
async def remove_member(
    project_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
):
    res = await db.execute(select(Project).where(Project.id == project_id))
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    if p.owner_id != current.id:
        raise HTTPException(status_code=403, detail="Only owner can remove members")

    res = await db.execute(select(User).where(User.id == user_id))
    u = res.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    await db.execute(
        delete(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
    )
    await db.commit()

    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(
            f"{settings.TG_SERVICE_URL}/notify",
            json={"telegram_id": u.telegram_id, "text": f"Вас удалили из проекта: {p.name}"},
        )

    return {"ok": True}