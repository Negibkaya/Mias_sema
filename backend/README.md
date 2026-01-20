# Backend Микросервисы

Проект состоит из трёх микросервисов: **core-service**, **ai-service** и **tg-service**, развернутых с помощью Docker Compose. Также добавлен pgAdmin для управления базой данных PostgreSQL.

## Общая архитектура

- **PostgreSQL**: Основная база данных для хранения пользователей, проектов, участников проектов и истории запросов к AI (таблицы: users, projects, project_members, llm_requests).
- **Redis**: Кэш для временных данных авторизации (коды логина на 5 минут).
- **pgAdmin**: Интерфейс для управления БД (доступен на http://localhost:5050, логин: admin@example.com, пароль: admin).

Сервисы взаимодействуют через HTTP (httpx) и запускаются на портах:

- core-service: 8000
- ai-service: 8001
- tg-service: 8002

## core-service (FastAPI + SQLAlchemy async + Postgres)

Основной сервис для управления данными и бизнес-логикой.

### API Endpoints

#### Аутентификация

- `POST /auth/telegram/complete`: Принимает код из Telegram бота, верифицирует через tg-service, создаёт/обновляет пользователя в БД, выдаёт JWT токен.

#### Пользователи

- `GET /users/me`: Получить профиль текущего пользователя (требует авторизации).
- `PUT /users/me`: Обновить профиль (имя, навыки, био) текущего пользователя (требует авторизации).
- `GET /users/`: Список всех пользователей.
- `GET /users/{user_id}`: Получить профиль пользователя по ID.

#### Проекты

- `POST /projects/`: Создать новый проект (только авторизованный пользователь становится владельцем).
- `GET /projects/`: Список всех проектов.
- `GET /projects/{project_id}`: Получить проект по ID.
- `PATCH /projects/{project_id}`: Обновить проект (только владелец).
- `DELETE /projects/{project_id}`: Удалить проект (только владелец).

#### Участники проектов

- `GET /projects/{project_id}/members`: Список участников проекта.
- `POST /projects/{project_id}/members/{user_id}`: Добавить участника (только владелец), отправляет уведомление через tg-service.
- `DELETE /projects/{project_id}/members/{user_id}`: Удалить участника (только владелец), отправляет уведомление.

#### AI Matching

- `POST /ai/match`: Запустить подбор кандидатов для проекта. Принимает project_id и опционально список candidate_ids. Вызывает ai-service, сохраняет запрос в БД (таблица llm_requests), возвращает список с score и reason для каждого кандидата.

### Модели данных

- **User**: telegram_id (int), username (str), name (str), skills (JSON list), bio (str).
- **Project**: name (str), description (str), skills_need (JSON list), owner_id (int).
- **ProjectMember**: project_id (int), user_id (int) (уникальная пара).
- **LLMRequest**: project_id (int), user_id (int), question (str), answer (str), created_at (datetime).

## ai-service (FastAPI + OpenRouter)

Сервис для интеграции с AI (LLM) через OpenRouter.

### API Endpoints

- `POST /match`: Принимает JSON с проектом и кандидатами. Формирует промпт для HR AI Assistant, отправляет в OpenRouter (модель openai/gpt-oss-120b:free). Возвращает результаты скоринга и сырой ответ.

### Формат ответа AI

AI отвечает в формате JSON:

```json
{
  "results": [
    {
      "id": 1,
      "score": 85,
      "reason": "Отличные навыки в Python и опыте в веб-разработке"
    },
    ...
  ],
  "raw": "Полный сырой ответ от LLM"
}
```

Где:

- `id`: ID кандидата (int)
- `score`: Оценка соответствия 0-100 (int)
- `reason`: Короткое объяснение (str)

## tg-service (FastAPI + aiogram + Redis)

Сервис для Telegram бота и REST API для уведомлений.

### Telegram бот

- `/start`: Приветственное сообщение.
- `/login`: Генерирует уникальный 6-символьный код, сохраняет в Redis на 5 минут с данными пользователя (telegram_id, username, name).

### REST API

- `POST /verify-code`: Принимает код, возвращает данные пользователя из Redis (и удаляет код).
- `POST /notify`: Принимает telegram_id и текст, отправляет сообщение пользователю в Telegram.

Бот работает в фоне с long polling.

## Запуск

1. Скопируйте `.env.example` в `.env` и заполните ключи (TELEGRAM_BOT_TOKEN, OPENROUTER_API_KEY, JWT_SECRET, CORE_DATABASE_URL, REDIS_URL).
2. `cd backend && docker compose up --build`
3. Доступ:
   - core-service: http://localhost:8000/docs
   - ai-service: http://localhost:8001/docs
   - tg-service: http://localhost:8002/docs
   - pgAdmin: http://localhost:5050

## Сценарий тестирования

1. В Telegram боте: `/start`, затем `/login` → получить CODE.
2. В Swagger core-service: `POST /auth/telegram/complete` с `{"code": "CODE"}` → получить token.
3. Авторизоваться (Bearer token).
4. `POST /projects/` создать проект.
5. `POST /projects/{id}/members/{user_id}` добавить участника → уведомление в Telegram.
6. `POST /ai/match` с project_id → получить скоринг кандидатов в формате списка {"id", "score", "reason"}.
