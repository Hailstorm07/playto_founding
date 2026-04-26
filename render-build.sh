#!/usr/bin/env bash
# exit on error
set -o errexit

# Build frontend
echo "Building frontend..."
cd frontend
# Remove existing lockfile and node_modules to fix native binding issues
rm -rf node_modules package-lock.json
npm install
npm run build
cd ..

# Build backend
echo "Building backend..."
pip install -r backend/requirements.txt

cd backend
python manage.py collectstatic --no-input
python manage.py migrate
