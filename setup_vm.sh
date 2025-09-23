#!/bin/bash
# Setup PSI service on VM with correct Python version

echo "🔧 Setting up PSI service on VM..."

# Remove old virtual environment
echo "Removing old virtual environment..."
rm -rf venv

# Check Python version
echo "Python version:"
python3 --version

# Create new virtual environment with system Python
echo "Creating new virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo "Now you can run: ./start_prod.sh"