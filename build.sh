#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt --break-system-packages

python manage.py collectstatic --no-input
python manage.py migrate
