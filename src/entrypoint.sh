#!/bin/bash

while ! nc -z db 5432; do
  sleep 0.1
done

bash -c "cd app && alembic revision --autogenerate && alembic upgrade head"
bash -c "cd app && python initial_data.py"
exec "$@"