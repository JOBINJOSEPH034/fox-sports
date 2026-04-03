#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Collecting static files and migrating database..."
python manage.py collectstatic --no-input
python manage.py migrate
