FROM python:3.10-slim-bullseye
MAINTAINER Sarvesh Patil

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]