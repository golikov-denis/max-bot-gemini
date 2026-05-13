# Деплой на VPS

Вариант для тех, кто хочет полный контроль над сервером, экономии или объединения нескольких ботов на одной машине. Минимальная конфигурация: 1 vCPU, 512 МБ RAM, Ubuntu 22.04/24.04 LTS. Подойдёт любой провайдер: Selectel, Timeweb Cloud, Beget, Aeza.

## Чек-лист подготовки

- VPS с публичным IP
- Доменное имя, настроенное на этот IP (А-запись)
- SSH-доступ под пользователем с правами sudo
- Действующий токен МАКС

## Шаги

### 1. Поставить системные пакеты

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx certbot python3-certbot-nginx git
```

### 2. Клонировать репозиторий

```bash
sudo mkdir -p /opt/max-bot-gemini
sudo chown $USER:$USER /opt/max-bot-gemini
cd /opt/max-bot-gemini

git clone https://github.com/golikov-denis/max-bot-gemini.git .
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Файл с переменными окружения

```bash
sudo tee /etc/max-bot-gemini.env >/dev/null <<'EOF'
MAX_TOKEN=replace_me
EOF

sudo chmod 600 /etc/max-bot-gemini.env
```

Замените `replace_me` на реальный токен. Права `600` нужны, чтобы файл читал только root.

### 4. systemd-юнит

```bash
sudo tee /etc/systemd/system/max-bot-gemini.service >/dev/null <<'EOF'
[Unit]
Description=MAX Bot — Gemini Access
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/max-bot-gemini
EnvironmentFile=/etc/max-bot-gemini.env
ExecStart=/opt/max-bot-gemini/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo chown -R www-data:www-data /opt/max-bot-gemini
sudo systemctl daemon-reload
sudo systemctl enable --now max-bot-gemini
sudo systemctl status max-bot-gemini
```

### 5. Nginx как обратный прокси

```bash
sudo tee /etc/nginx/sites-available/max-bot-gemini >/dev/null <<'EOF'
server {
    listen 80;
    server_name bot.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/max-bot-gemini /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. HTTPS через Let's Encrypt

```bash
sudo certbot --nginx -d bot.example.com
```

Certbot подправит конфиг nginx и поставит автообновление сертификата в cron.

### 7. Зарегистрировать вебхук

В личном кабинете МАКС указать URL:

```
https://bot.example.com/webhook
```

Проверка:

```bash
curl https://bot.example.com/health
# {"ok":true}
```

## Управление сервисом

| Действие              | Команда                                       |
|-----------------------|------------------------------------------------|
| Перезапустить         | `sudo systemctl restart max-bot-gemini`        |
| Остановить            | `sudo systemctl stop max-bot-gemini`           |
| Посмотреть логи       | `journalctl -u max-bot-gemini -f`              |
| Логи за последний час | `journalctl -u max-bot-gemini --since "1 hour ago"` |

## Обновление кода

```bash
cd /opt/max-bot-gemini
sudo -u www-data git pull
sudo -u www-data ./.venv/bin/pip install -r requirements.txt
sudo systemctl restart max-bot-gemini
```

## Безопасность

- Не публикуйте `MAX_TOKEN` в репозитории. Используйте файл `/etc/max-bot-gemini.env` с правами `600`.
- Закройте UFW всё, кроме SSH, 80 и 443:
  ```bash
  sudo ufw allow OpenSSH
  sudo ufw allow 'Nginx Full'
  sudo ufw enable
  ```
- Включите автоматические обновления безопасности:
  ```bash
  sudo apt install -y unattended-upgrades
  sudo dpkg-reconfigure -plow unattended-upgrades
  ```

## Типичные проблемы

**Сервис не стартует, в логах `Permission denied`.** Не хватает прав у `www-data` на `/opt/max-bot-gemini` или на `.venv/bin/uvicorn`. Выполните `sudo chown -R www-data:www-data /opt/max-bot-gemini`.

**`502 Bad Gateway` от nginx.** Бот не слушает порт 8000. Проверьте `systemctl status max-bot-gemini` и `journalctl -u max-bot-gemini -f`.

**Сертификат не выдаётся.** Проверьте, что A-запись домена действительно указывает на IP сервера и что в файрволе открыт порт 80.
