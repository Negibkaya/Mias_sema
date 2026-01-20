import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import httpx

from ..deps import get_db, get_current_user
from ..models import Project, User, LLMRequest, ProjectMember
from ..schemas import MatchRequestIn, RoleMatchResult
from ..main import settings

router = APIRouter()


@router.post("/match", response_model=list[RoleMatchResult])
async def match_candidates(
    payload: MatchRequestIn,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
):
    # Загружаем проект с участниками
    res = await db.execute(
        select(Project)
        .where(Project.id == payload.project_id)
        .options(selectinload(Project.members))
    )
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    if p.owner_id != current.id:
        raise HTTPException(status_code=403, detail="Only owner can run matching")

    if not p.roles:
        raise HTTPException(status_code=400, detail="Project has no roles defined")

    # Получаем ID уже добавленных участников
    existing_member_ids = {m.user_id for m in p.members}

    # Считаем заполненность ролей
    role_fill_count = {}
    for m in p.members:
        if m.role_name:
            role_fill_count[m.role_name] = role_fill_count.get(m.role_name, 0) + 1

    # Фильтруем роли для обработки
    roles_to_process = p.roles
    if payload.role_name:
        roles_to_process = [r for r in p.roles if r["name"] == payload.role_name]
        if not roles_to_process:
            raise HTTPException(status_code=404, detail=f"Role '{payload.role_name}' not found")

    # Получаем всех кандидатов (кроме владельца)
    res = await db.execute(select(User).where(User.id != current.id))
    all_candidates = list(res.scalars().all())

    if not all_candidates:
        return [
            RoleMatchResult(
                role_name=r["name"],
                needed=r["count"],
                filled=role_fill_count.get(r["name"], 0),
                candidates=[]
            )
            for r in roles_to_process
        ]

    # Формируем запрос к AI
    ai_input = {
        "project": {
            "id": p.id,
            "name": p.name,
            "description": p.description,
        },
        "roles": roles_to_process,
        "candidates": [
            {
                "id": u.id,
                "name": u.name,
                "username": u.username,
                "bio": u.bio,
                "skills": u.skills or [],
            }
            for u in all_candidates
        ],
        "top_n": payload.top_n,
    }

    # Вызываем AI service
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{settings.AI_SERVICE_URL}/match", json=ai_input)

    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"AI service error: {r.text}")

    data = r.json()
    results = data.get("results", [])
    raw = data.get("raw", "")

    # Сохраняем запрос
    q = f"Match candidates for project_id={p.id}, roles={[r['name'] for r in roles_to_process]}"
    db.add(LLMRequest(project_id=p.id, user_id=current.id, question=q, answer=raw or json.dumps(results)))
    await db.commit()

    # Формируем ответ
    output = []
    for role_result in results:
        output.append(RoleMatchResult(
            role_name=role_result.get("role_name", "Unknown"),
            needed=role_result.get("needed", 1),
            filled=role_fill_count.get(role_result.get("role_name"), 0),
            candidates=role_result.get("candidates", [])
        ))

    return output