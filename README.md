Проект для подбора участников в IT-проекты с использованием AI. Состоит из backend микросервисов, веб-фронтенда и десктопного приложения.

## Архитектура

- **Backend**: Микросервисы на FastAPI (core, ai, tg) с PostgreSQL, Redis и Docker.
- **Frontend**: Веб-приложение на React + Vite.
- **Desktop**: Десктопное приложение на Python + CustomTkinter.

## Сервисы

### Backend

Микросервисы для API, AI-интеграции и Telegram бота. Подробно в `backend/README.md`.

### Frontend

Веб-интерфейс для пользователей. Подробно в `frontend/README.md`.

### Desktop

Десктопная версия приложения. Подробно в `desktop/README.md`.

## Запуск всего проекта

1. Запустите backend: `cd backend && docker compose up --build`
2. Запустите frontend: `cd frontend && npm install && npm run dev`
3. Запустите desktop: `cd desktop && uv sync && uv run python main.py`
