import json
import random
import google.generativeai as genai
from fastapi import FastAPI
from .settings import Settings

settings = Settings()
app = FastAPI(title="ai-service")

# Настраиваем Google API один раз при запуске
genai.configure(api_key=settings.GEMINI_API_KEY)

@app.post("/match")
async def match(payload: dict):
    project = payload.get("project") or {}
    roles = payload.get("roles") or []
    candidates = payload.get("candidates") or []
    top_n = payload.get("top_n", 3)

    if not candidates:
        return {"results": [], "raw": "No candidates provided"}

    # Промпт
    prompt = f"""You are an HR AI Assistant.
    
    PROJECT: {project.get("name")}
    DESCRIPTION: {project.get("description")}
    
    ROLES NEEDED:
    {json.dumps(roles)}
    
    CANDIDATES:
    {json.dumps(candidates)}
    
    TASK:
    Select top {top_n} candidates for EACH role.
    
    OUTPUT SCHEMA:
    Return a JSON object with a key "results" containing a list of objects.
    Each object must have: "role_name", "needed" (int), and "candidates" (list of objects with "id", "score", "reason").
    """

    raw_response = ""
    results = []

    try:
        # Используем модель с конфигурацией JSON
        model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            generation_config={"response_mime_type": "application/json"}
        )

        # Выполняем синхронный запрос (внутри FastAPI он отработает нормально в треде)
        # Google SDK сам обрабатывает повторные попытки
        response = model.generate_content(prompt)
        
        raw_response = response.text
        
        # Парсим JSON (Google гарантирует JSON, но на всякий случай проверяем)
        parsed = json.loads(raw_response)
        results = parsed.get("results", [])

    except Exception as e:
        print(f"⚠️ GEMINI ERROR: {e}")
        # === FALLBACK (ЗАПАСНОЙ ВАРИАНТ) ===
        # Если вдруг Google упадет (маловероятно), генерируем фейк
        raw_response = f"Error: {str(e)}. Using fallback."
        
        fallback_results = []
        for role in roles:
            fake_candidates = []
            available = candidates[:top_n] if len(candidates) >= top_n else candidates
            for cand in available:
                score = random.randint(70, 99)
                fake_candidates.append({
                    "id": cand["id"],
                    "score": score,
                    "reason": f"Подходит на роль {role['name']} (Gemini API Error Fallback)"
                })
            fake_candidates.sort(key=lambda x: x["score"], reverse=True)
            fallback_results.append({
                "role_name": role["name"],
                "needed": role["count"],
                "candidates": fake_candidates
            })
        results = fallback_results

    return {"results": results, "raw": raw_response}