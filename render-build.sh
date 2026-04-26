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
# Install Python packages globally (not in a venv)
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r backend/requirements.txt

cd backend
echo "Running collectstatic..."
python3 manage.py collectstatic --no-input --clear
echo "Running migrations..."
python3 manage.py migrate
cd ..

echo "Build complete!"

