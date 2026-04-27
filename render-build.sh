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

if [ ! -f "dist/index.html" ]; then
    echo "✗ ERROR: frontend/dist/index.html not created!"
    ls -la dist/
    exit 1
fi

cd ..
echo "✓ Frontend build complete"

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

# Copy frontend build to backend static files AFTER collectstatic
# (so it doesn't get deleted by the --clear flag)
echo "Copying frontend build to backend staticfiles..."
mkdir -p backend/staticfiles/dist
# Copy the entire dist folder
cp -r frontend/dist/* backend/staticfiles/dist/

# Verify copy was successful
if [ ! -f "backend/staticfiles/dist/index.html" ]; then
    echo "✗ ERROR: index.html not in backend/staticfiles/dist after copy!"
    echo "Contents of frontend/dist:"
    ls -la frontend/dist/
    echo "Contents of backend/staticfiles/dist:"
    ls -la backend/staticfiles/dist/
    exit 1
fi

echo "✓ Frontend copied to backend/staticfiles/dist"
echo "✓ index.html verified at: backend/staticfiles/dist/index.html"

echo "===== Build Complete ====="
echo "Deployment ready!"




