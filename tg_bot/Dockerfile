FROM python:3.12-slim AS builder
WORKDIR /app

COPY tg_bot/requirements.txt tg_bot/requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r tg_bot/requirements.txt
COPY tg_bot tg_bot


FROM python:3.12-slim

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*
COPY --from=builder /app/tg_bot app/tg_bot

CMD ["python3", "-m", "app.tg_bot"]
