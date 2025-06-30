#!/bin/bash
set -e  # Exit immediately if any command fails

echo "=== Setting up CCal_V2 ==="

# Update and install system packages
echo "Updating system and installing dependencies..."
sudo apt update
sudo apt upgrade -y
sudo apt install -y git nodejs npm portaudio19-dev python3-pip

# Verify Node.js installation (node package might be nodejs-legacy on some systems)
if ! command -v node &> /dev/null; then
    sudo apt install -y nodejs-legacy
fi

# Clone repository
echo "Cloning repository..."
if [ ! -d "CCal_V2" ]; then
    git clone https://github.com/Logan-Fouts/CCal_V2.git
else
    echo "CCal_V2 directory already exists, skipping clone"
fi

# Install WebGUI dependencies
echo "Installing WebGUI dependencies..."
cd CCal_V2/WebGUI && npm install && cd -

# Install Python dependencies
echo "Installing Python dependencies..."
cd CCal_V2/LedControl
sudo pip install --upgrade pip
sudo pip install -r requirements.txt
cd -

# Setup systemd services
echo "Configuring system services..."
sudo cp CCal_V2/SystemdServices/ccalpy.service /etc/systemd/system/
sudo cp CCal_V2/SystemdServices/ccalpy_gui.service /etc/systemd/system/

# Enable and start services
echo "Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable --now ccalpy.service
sudo systemctl enable --now ccalpy_gui.service

echo "=== Setup completed successfully ==="
echo "Services status:"
sudo systemctl status ccalpy.service ccalpy_gui.service --no-pager
