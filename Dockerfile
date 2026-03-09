FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY ./migrations ./migrations
COPY start.sh .
COPY ./alembic.ini .

ENV PYTHONPATH=/app


RUN chmod +x start.sh
CMD ["./start.sh"]