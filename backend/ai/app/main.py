import json
from fastapi import FastAPI, HTTPException
import httpx

from .settings import Settings

settings = Settings()
app = FastAPI(title="ai-service")


@app.post("/match")
async def match(payload: dict):
    """
    payload:
    {
      "project": {"id", "name", "description"},
      "roles": [{"name": "Backend", "count": 2, "skills": [...]}],
      "candidates": [{id, skills, bio, ...}, ...],
      "top_n": 3
    }
    """
    project = payload.get("project") or {}
    roles = payload.get("roles") or []
    candidates = payload.get("candidates") or []
    top_n = payload.get("top_n", 3)

    if not project or not roles or not candidates:
        raise HTTPException(status_code=400, detail="project, roles and candidates required")

    # Формируем промпт для LLM
    prompt = f"""You are an HR AI Assistant for team matching.

PROJECT: {project.get("name")}
DESCRIPTION: {project.get("description") or "Not specified"}

ROLES NEEDED:
{json.dumps(roles, ensure_ascii=False, indent=2)}

CANDIDATES:
{json.dumps(candidates, ensure_ascii=False, indent=2)}

TASK:
For each role, analyze all candidates and select TOP {top_n} best matches.
Consider:
1. Skill match (name AND level - candidate level should be >= required level)
2. Bio/experience relevance
3. Overall fit for the role

IMPORTANT: Return ONLY valid JSON, no other text!

RESPONSE FORMAT:
{{
  "results": [
    {{
      "role_name": "<role name>",
      "needed": <count needed>,
      "candidates": [
        {{"id": <candidate_id>, "score": <0-100>, "reason": "<short explanation in Russian>"}},
        ...
      ]
    }},
    ...
  ]
}}

Each role should have maximum {top_n} candidates, sorted by score descending.
If no good match found for a role, return empty candidates array.
Score meaning: 80-100 = excellent match, 60-79 = good, 40-59 = acceptable, below 40 = poor.
""".strip()

    req = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }

    headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            # ДОБАВЬ ЭТИ ДВЕ СТРОКИ:
            "HTTP-Referer": "https://mias-sema.onrender.com",
            "X-Title": "Student Project AI Service",
    }

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=req)

    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=r.text)

    data = r.json()
    msg = data["choices"][0]["message"].get("content", "")
    raw = msg

    # Парсим JSON из ответа
    results = []
    try:
        parsed = json.loads(msg)
        results = parsed.get("results", [])
    except Exception:
        # Пробуем найти JSON в тексте
        start = msg.find("{")
        end = msg.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                parsed = json.loads(msg[start:end + 1])
                results = parsed.get("results", [])
            except Exception:
                pass

    return {"results": results, "raw": raw}