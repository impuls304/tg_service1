# Мастер на дом — Telegram Mini App

Мини-приложение Telegram для сервиса «Мастер на дом» с витриной услуг, портфолио и заявкой на расчет стоимости.

## Возможности
- FastAPI backend с базой SQLite/SQLAlchemy
- REST API для услуг, портфолио и заявок
- Интеграция с Telegram WebApp и webhook-и a iogram
- Адаптивный фронтенд (HTML/CSS/JS) с lightbox-галереей
- Typer CLI для наполнения демо-данными

## Стек
- Python 3.10+, FastAPI, SQLAlchemy, aiogram, Typer
- Frontend: HTML5 + CSS3 + Vanilla JS

## Подготовка окружения
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Переменные окружения
Создайте `.env` с параметрами:
```
DATABASE_URL=sqlite:///./data/master_service.db
TELEGRAM_BOT_TOKEN=<bot_token>
TELEGRAM_MASTER_CHAT_ID=<chat_id>
TELEGRAM_WEBHOOK_BASE_URL=https://example.com
```

## Запуск
```bash
uvicorn backend.app.main:app --reload
```
Frontend доступен на `/` (статический), API — `/api/*`.

## Telegram webhook
1. Настройте внешний HTTPS.
2. Отправьте POST на `/telegram/set-webhook`.

## CLI
```bash
python -m backend.app.admin.cli seed
```
Создает демо-услуги и примеры работ.

## API
- `GET /api/services/`
- `GET /api/portfolio/`
- `GET /api/requests/`
- `POST /api/requests/`

## Структура БД
- services
- portfolio
- users
- requests

## Дальнейшие шаги
- Подключить постоянное хранилище изображений
- Настроить уведомления мастеру через Telegram Bot API
- Развернуть на HTTPS хостинге (Railway/Render/Heroku/VPS)
