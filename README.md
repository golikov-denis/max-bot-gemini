# MAX Bot — Gemini Access

Чат-бот для мессенджера МАКС: принимает команду `/start`, отправляет приветствие с инлайн-кнопками и по нажатию на кнопки выдаёт информацию об обучении и условиях записи. Прицельная задача — сопроводить пользователя к мини-приложению Gemini внутри МАКС и к группе с бесплатными вебинарами.

## Стек

- Python 3.12
- FastAPI
- requests
- MAX Platform API (`platform-api.max.ru`)

## Документация

Полная документация собрана на сайте: **https://golikov-denis.github.io/max-bot-gemini/**

Там описана архитектура, формат вебхуков и исходящих запросов, инструкции по деплою на Railway и VPS, а также руководство пользователя.

## Быстрый запуск локально

```bash
git clone https://github.com/golikov-denis/max-bot-gemini.git
cd max-bot-gemini

python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # подставить свой MAX_TOKEN
export MAX_TOKEN=...          # либо через переменные окружения

uvicorn main:app --host 0.0.0.0 --port 8000
```

Подробности — в разделе [Быстрый старт](https://golikov-denis.github.io/max-bot-gemini/#быстрый-старт) на сайте.

## Лицензия

MIT
