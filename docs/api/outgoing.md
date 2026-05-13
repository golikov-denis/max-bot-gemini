# Исходящие запросы

Бот вызывает два метода MAX Platform API: отправку сообщения в чат и ответ на нажатие инлайн-кнопки. Оба идут через общий хелпер `post_max`, который добавляет заголовки и логирование.

## Общие правила

| Параметр     | Значение                                           |
|--------------|----------------------------------------------------|
| Метод        | `POST`                                             |
| Базовый URL  | `https://platform-api.max.ru`                      |
| Заголовки    | `Authorization: <MAX_TOKEN>`, `Content-Type: application/json` |
| Таймаут      | 20 секунд                                          |
| Поведение при ошибке | `requests.raise_for_status()` + проброс наверх |

## Отправка сообщения

### Эндпоинт

```http
POST /messages?chat_id={chat_id}
```

### Тело запроса (без кнопок)

```json
{
  "text": "Привет!",
  "notify": true
}
```

### Тело запроса (с инлайн-клавиатурой)

```json
{
  "text": "Привет!",
  "notify": true,
  "attachments": [
    {
      "type": "inline_keyboard",
      "payload": {
        "buttons": [
          [
            { "type": "callback", "text": "Про обучение", "payload": "about" }
          ],
          [
            { "type": "callback", "text": "Записаться", "payload": "signup" }
          ]
        ]
      }
    }
  ]
}
```

### Поля

| Поле                     | Тип     | Описание                                                |
|--------------------------|---------|----------------------------------------------------------|
| `text`                   | string  | Текст сообщения                                          |
| `notify`                 | bool    | Отправлять ли пуш-уведомление                            |
| `attachments`            | array   | Дополнительные вложения, включая клавиатуру              |
| `attachments[].type`     | string  | Для кнопок — `"inline_keyboard"`                         |
| `attachments[].payload.buttons` | array | Матрица кнопок: внешний массив — строки, внутренний — кнопки в строке |
| `buttons[][].type`       | string  | Тип кнопки, в боте используется `"callback"`             |
| `buttons[][].text`       | string  | Подпись кнопки                                           |
| `buttons[][].payload`    | string  | Значение, которое прилетит в `message_callback` при нажатии |

### Реализация

```python
def send_message(chat_id: int, text: str, with_buttons: bool = False):
    url = f"{API_BASE}/messages?chat_id={chat_id}"
    payload = {"text": text, "notify": True}
    if with_buttons:
        payload["attachments"] = build_keyboard()
    return post_max(url, payload)
```

## Ответ на нажатие кнопки

### Эндпоинт

```http
POST /answers?callback_id={callback_id}
```

### Тело запроса

```json
{
  "message": {
    "text": "Текст ответа пользователю"
  }
}
```

### Поля

| Поле              | Тип    | Описание                            |
|-------------------|--------|--------------------------------------|
| `message.text`    | string | Текст, который придёт пользователю   |

### Реализация

```python
def answer_callback(callback_id: str, text: str):
    url = f"{API_BASE}/answers?callback_id={callback_id}"
    payload = {"message": {"text": text}}
    return post_max(url, payload)
```

## Поведение при ошибках

Хелпер `post_max` пробрасывает `requests.RequestException` наверх — обработчик `webhook` его не ловит, и FastAPI вернёт `500`. Для платформы это означает повторную доставку обновления через какое-то время. В большинстве случаев это правильное поведение: если сеть моргнула, ретрай чинит проблему сам.

```python
def post_max(url: str, payload: dict):
    try:
        resp = requests.post(url, headers=headers(), json=payload, timeout=20)
        logging.info("MAX %s -> %s %s", url, resp.status_code, resp.text)
        resp.raise_for_status()
        return resp.json() if resp.content else {}
    except requests.RequestException as e:
        logging.exception("MAX API request failed: %s", e)
        raise
```

## Чего пока нет

- Отправка медиа (изображения, видео, файлы).
- Редактирование уже отправленных сообщений.
- Удаление сообщений.
- Изменение инлайн-клавиатуры на лету.

Все эти возможности у API МАКС есть, но в текущем сценарии бота не используются.
