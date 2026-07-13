FROM python:3.12-slim

WORKDIR /app

# install runtime deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY . .

ENV ORCHESTRATOR_TOKEN=change-this-token

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]