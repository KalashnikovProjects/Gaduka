FROM python:3.9-slim-buster AS builder
WORKDIR /app

COPY gaduka_engine/requirements.txt gaduka_engine/requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r gaduka_engine/requirements.txt
COPY gaduka_engine gaduka_engine


FROM python:3.9-slim-buster

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*
COPY --from=builder /app/gaduka_engine app/gaduka_engine

EXPOSE 8081

ENTRYPOINT ["python3", "-m", "app.gaduka_engine"]
