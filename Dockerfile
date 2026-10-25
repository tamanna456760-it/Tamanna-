
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-server.txt ./requirements-server.txt

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements-server.txt

COPY . .

RUN useradd --create-home --uid 10001 tamanna \
    && mkdir -p /app/data \
    && chown -R tamanna:tamanna /app

USER tamanna

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "Main:app", "--host", "0.0.0.0", "--port", "8000"]
