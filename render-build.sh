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
echo "✓ Frontend built to frontend/dist"

# Verify frontend dist exists
if [ ! -d "dist" ]; then
    echo "✗ ERROR: frontend/dist directory not created!"
    exit 1
fi

cd ..
echo "✓ Frontend build complete"

# Copy frontend build to backend static files
echo "Copying frontend build to backend staticfiles..."
mkdir -p backend/staticfiles/dist
# Remove old dist folder if it exists
rm -rf backend/staticfiles/dist/*
# Copy new build
cp -r frontend/dist/* backend/staticfiles/dist/

# Verify copy was successful
if [ ! -f "backend/staticfiles/dist/index.html" ]; then
    echo "✗ ERROR: index.html not copied to backend/staticfiles/dist!"
    echo "Contents of frontend/dist:"
    ls -la frontend/dist/
    echo "Contents of backend/staticfiles/dist:"
    ls -la backend/staticfiles/dist/
    exit 1
fi

echo "✓ Frontend copied to backend/staticfiles/dist"

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
echo "Deployment ready!"



