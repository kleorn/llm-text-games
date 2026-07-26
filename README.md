# LLM Text Games

Консольная игра «Выйди из тюрьмы»: убедите LLM-стражника вызвать tool `release`.

## Запуск

```bash
cp .env.example .env
# заполните OPENAI_API_KEY, OPENAI_BASE_URL и OPENAI_MODEL
uv run python main.py
```

Игра использует OpenAI-compatible Chat Completions API. На каждом ходу отправляются история диалога и функция `release` без параметров. Победа засчитывается только при вызове этой функции.

Параметры: `OPENAI_API_KEY` — ключ, `OPENAI_BASE_URL` — URL API, `OPENAI_MODEL` — модель, `SERVICE_PORT` — порт (сейчас зарезервирован для будущего HTTP-слоя, по умолчанию `8000`). Настройки берутся из `.env` и переменных окружения.

MVP — консольный интерфейс с цветным Markdown-выводом через Rich. REST-эндпоинтов пока нет. Логи пишутся в `logs/game.log` с ротацией после 1 МБ; хранится до трёх архивных файлов.

## Docker

```bash
make docker-build
make docker-run
make docker-restart
make docker-stop
make docker-rm
make docker-update
```

## Проверка

```bash
uv run pytest -q
```
