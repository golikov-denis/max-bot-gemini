from fastapi import FastAPI, Request, HTTPException
import requests
import os
import json
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("MAX_TOKEN")
API_BASE = "https://platform-api.max.ru"

START_TEXT = """Привет! 👋 Как и обещал, лови свой доступ к Gemini — просто жми на кнопку в нижнем левом углу. ↙️

Вступай в группу в МАКС чтобы не пропустить бесплатные вебинары.
https://max.ru/join/xXpP5puLml652lTRKuiAXvCccnjI_AJjPNVNmeN4NsY

А ниже я подготовил для тебя подробности о 3-дневном интенсиве по нейросетям. Заглядывай почитать или сразу занимай место, если готов врываться! 🚀✨"""

ABOUT_TEXT = """Обучение нейросетям с полного нуля 🎓

Никакой предварительной подготовки не нужно!

Что вас ждёт:
🔹 Разберём возможности нейросетей на практике
🔹 Покажу реальные способы заработка с их помощью 💰
🔹 Всё наглядно — рассказываю и показываю в прямом эфире

Формат:
- Вебинары по вторникам в 18:00 по 1,5 часа
💵 Стоимость — 1 500 ₽ за живой вебинар

- Записи прошлых вебинаров
💵 Стоимость — от 290₽ за записи уроков и вебинаров

Как всё устроено:
1️⃣ За день до занятия пришлю ссылку на вебинар в МАХ
https://max.ru/join/xXpP5puLml652lTRKuiAXvCccnjI_AJjPNVNmeN4NsY

2️⃣ Оплачиваете 1 500 ₽ перед входом
3️⃣ Заходите в эфир и получаете знания 🚀

Вступите в группу в МАХ чтобы узнавать о бесплатных вебинарах.
https://max.ru/join/xXpP5puLml652lTRKuiAXvCccnjI_AJjPNVNmeN4NsY

👇 А пока посмотрите это видео о том, что мы будем изучать:
https://vkvideo.ru/video-236745998_456239017"""

SIGNUP_TEXT = """Чтобы записаться на обучение по нейросетям с полного нуля следует вступить в группу в МАКС.
https://max.ru/join/xXpP5puLml652lTRKuiAXvCccnjI_AJjPNVNmeN4NsY

Никакой предварительной подготовки не нужно!

Что вас ждёт:
🔹 Разберём возможности нейросетей на практике
🔹 Покажу реальные способы заработка с их помощью 💰
🔹 Всё наглядно — рассказываю и показываю в прямом эфире

👇 А пока посмотрите это видео о том, что мы будем изучать:
https://vkvideo.ru/video-236745998_456239017

Или пообщайтесь с бесплатным ИИ Gemini
https://max-miniapp-2.vercel.app/"""


def headers():
    if not TOKEN:
        raise RuntimeError("MAX_TOKEN is missing")
    return {
        "Authorization": TOKEN,
        "Content-Type": "application/json",
    }


def build_keyboard():
    return [
        {
            "type": "inline_keyboard",
            "payload": {
                "buttons": [
                    [
                        {
                            "type": "callback",
                            "text": "Про обучение",
                            "payload": "about"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "Записаться",
                            "payload": "signup"
                        }
                    ]
                ]
            }
        }
    ]


def post_max(url: str, payload: dict):
    try:
        resp = requests.post(url, headers=headers(), json=payload, timeout=20)
        logging.info("MAX %s -> %s %s", url, resp.status_code, resp.text)
        resp.raise_for_status()
        return resp.json() if resp.content else {}
    except requests.RequestException as e:
        logging.exception("MAX API request failed: %s", e)
        raise


def send_message(chat_id: int, text: str, with_buttons: bool = False):
    url = f"{API_BASE}/messages?chat_id={chat_id}"
    payload = {
        "text": text,
        "notify": True
    }
    if with_buttons:
        payload["attachments"] = build_keyboard()
    return post_max(url, payload)


def answer_callback(callback_id: str, text: str):
    url = f"{API_BASE}/answers?callback_id={callback_id}"
    payload = {
        "message": {
            "text": text
        }
    }
    return post_max(url, payload)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/webhook")
async def webhook(req: Request):
    if not TOKEN:
        raise HTTPException(status_code=500, detail="MAX_TOKEN is missing")

    try:
        body = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    logging.info("INCOMING_UPDATE: %s", json.dumps(body, ensure_ascii=False))

    update_type = body.get("update_type") or body.get("type")

    if update_type == "message_created":
        message = body.get("message") or {}
        recipient = message.get("recipient") or {}
        chat_id = recipient.get("chat_id")
        text = ((message.get("body") or {}).get("text") or "").strip().lower()

        if chat_id and text in ("/start", "/старт"):
            send_message(chat_id, START_TEXT, with_buttons=True)

    elif update_type == "message_callback":
        callback = body.get("callback") or {}
        callback_id = callback.get("callback_id")
        payload = callback.get("payload")

        if callback_id and payload == "about":
            answer_callback(callback_id, ABOUT_TEXT)
        elif callback_id and payload == "signup":
            answer_callback(callback_id, SIGNUP_TEXT)

    return {"ok": True}