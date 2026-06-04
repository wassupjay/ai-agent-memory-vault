# Secrets Access Policy

> Access policy only. NEVER store actual values here. Values live in ~/.secrets/master.env (chmod 600).

## Rule
- Dir: `~/.secrets/` → chmod 700
- Each file: chmod 600
- Services load via systemd `EnvironmentFile=`
- Code reads via `os.environ["KEY_NAME"]` — never hardcoded

## Key Registry
| Key Name | Stored In | Used By |
|----------|-----------|---------|
| TELEGRAM_BOT_TOKEN | ~/.secrets/master.env | your-telegram-bot |
| OPENAI_API_KEY | ~/.secrets/master.env | your-openai-service |
| YOUR_KEY_NAME | ~/.secrets/your-service.env | your-service |

## Injecting Into Services
```ini
# ~/.config/systemd/user/your-service.service
[Service]
EnvironmentFile=%h/.secrets/your-service.env
ExecStart=/usr/bin/python3 /path/to/your/script.py
```
