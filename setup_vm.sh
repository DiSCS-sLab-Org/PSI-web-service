# Install Python 3.11 on your VM
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# Update your setup script to use Python 3.11
#!/bin/bash
echo "🔧 Setting up PSI service on VM..."
echo "Removing old virtual environment..."
rm -rf venv
echo "Python version:"
python3.11 --version
echo "Creating new virtual environment..."
python3.11 -m venv venv
echo "Activating virtual environment..."
source venv/bin/activate
echo "Upgrading pip..."
pip install --upgrade pip
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✅ Setup complete!"
