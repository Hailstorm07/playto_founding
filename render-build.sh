#!/usr/bin/env bash
# exit on error
set -o errexit

# Build frontend
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Build backend
echo "Building backend..."
pip install -r backend/requirements.txt

cd backend
python manage.py collectstatic --no-input
python manage.py migrate
