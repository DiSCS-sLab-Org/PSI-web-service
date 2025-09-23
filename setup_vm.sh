#!/bin/bash
echo "🔧 Setting up PSI service on VM..."
echo "Removing old virtual environment..."
rm -rf venv
echo "Python version:"
/usr/local/bin/python3.11 --version
echo "Creating new virtual environment..."
/usr/local/bin/python3.11 -m venv venv
echo "Activating virtual environment..."
source venv/bin/activate
echo "Upgrading pip..."
pip install --upgrade pip
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✅ Setup complete!"
echo "Now you can run: ./start_prod.sh"
