#!/usr/bin/env bash
# exit on error
set -o errexit

echo "===== Build Start ====="

# Build frontend
echo "Building frontend..."
cd frontend
# Remove existing lockfile and node_modules to fix native binding issues
rm -rf node_modules package-lock.json
npm install
npm run build
cd ..
echo "✓ Frontend built"

# Copy frontend build to backend static files
echo "Copying frontend build to backend staticfiles..."
mkdir -p backend/staticfiles/dist
cp -r frontend/dist/* backend/staticfiles/dist/
echo "✓ Frontend copied"

# Build backend
echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r backend/requirements.txt
echo "✓ Dependencies installed"

cd backend
echo "Running collectstatic..."
python3 manage.py collectstatic --no-input --clear
echo "✓ Static files collected"

echo "Running migrations..."
python3 manage.py migrate
echo "✓ Migrations applied"

cd ..
echo "===== Build Complete ====="


