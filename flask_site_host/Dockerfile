FROM python:3.12 AS builder
WORKDIR /app

COPY flask_site_host/requirements.txt flask_site_host/requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r flask_site_host/requirements.txt
COPY flask_site_host flask_site_host

FROM python:3.12-slim

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*
COPY --from=builder /app/flask_site_host app/flask_site_host

EXPOSE 8080

ENTRYPOINT ["python3", "-m", "app.flask_site_host"]
