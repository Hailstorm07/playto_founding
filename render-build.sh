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

# Copy frontend build to backend static files
echo "Copying frontend build to backend staticfiles..."
mkdir -p backend/staticfiles/dist
cp -r frontend/dist/* backend/staticfiles/dist/

# Build backend
echo "Building backend..."
# Use python3 -m pip as it's more reliable in Linux environments
python3 -m pip install --upgrade pip
python3 -m pip install -r backend/requirements.txt

cd backend
python3 manage.py collectstatic --no-input
python3 manage.py migrate

