#!/bin/sh

echo "Updating DB"

echo "Current directory: $(pwd)"
echo "Files in /app:"
ls -la

alembic upgrade head

echo "Starting FastAPI"
uvicorn src.main:app --host 0.0.0.0 --port 8000