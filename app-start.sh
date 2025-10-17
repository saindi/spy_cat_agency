#!/usr/bin/env bash


set -e
# Execute the main process
python -m alembic upgrade head
echo "Migrations applied."
python -m app.main
