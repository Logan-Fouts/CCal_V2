#!/bin/bash

echo "Setting up CCal_V2..."
sudo apt install git

# Clone the repository
git clone https://github.com/Logan-Fouts/CCal_V2.git

# Install npm dependencies
cd CCal_V2/WebGUI
npm install

# Install Python dependencies
cd ../LedControl
sudo apt install python3-pip
sudo pip install -r requirements.txt

# Copy systemd service files
sudo cp ../SystemdServices/ccalpy.service /etc/systemd/system/ccalpy.service
sudo cp ../SystemdServices/ccalpy_gui.service /etc/systemd/system/ccalpy_gui.service

# Enable and start the services
sudo systemctl enable --now ccalpy_gui.service
sudo systemctl enable --now ccalpy.service
