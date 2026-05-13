# Журнал изменений

Все заметные изменения проекта фиксируются здесь. Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/), номера версий следуют [SemVer](https://semver.org/lang/ru/).

## [Unreleased]

### Планируется

- Перенос текстов сообщений в отдельный JSON-файл, чтобы редактировать без релиза.
- Переход с `requests` на `httpx.AsyncClient`.
- Обработка сообщений с текстом, отличным от `/start`: подсказка пользователю, какие команды доступны.
- Базовые метрики (количество `/start`, количество нажатий по кнопкам) в формате Prometheus.

## [1.0.0] — 2026-04-10

### Добавлено

- Эндпоинт `POST /webhook` для приёма обновлений от MAX Platform API.
- Обработка `update_type = message_created` для команд `/start` и `/старт`.
- Обработка `update_type = message_callback` для значений `payload` `about` и `signup`.
- Приветственное сообщение `START_TEXT` с инлайн-клавиатурой на две кнопки.
- Тексты `ABOUT_TEXT` и `SIGNUP_TEXT` для соответствующих кнопок.
- Эндпоинты `GET /` и `GET /health` для проверки живости.
- Логирование входящих обновлений и исходящих запросов.

### Технические детали

- Стек: Python 3.12, FastAPI, requests.
- Конфигурация через переменную окружения `MAX_TOKEN`.
- Базовый URL платформы: `https://platform-api.max.ru`.

---

[Unreleased]: https://github.com/golikov-denis/max-bot-gemini/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/golikov-denis/max-bot-gemini/releases/tag/v1.0.0
