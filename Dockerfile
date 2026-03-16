FROM python:3.10.14-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1 \
	WEB_CONCURRENCY=1 \
	GUNICORN_TIMEOUT=120

WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY . /app

EXPOSE 8080

CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:8080 --workers ${WEB_CONCURRENCY} --timeout ${GUNICORN_TIMEOUT} --max-requests 500 --max-requests-jitter 50"]