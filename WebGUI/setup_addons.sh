#!/bin/bash

CONFIG_FILE="/home/ccalv2/CCal_V2/config.json"
echo "Starting setup_addons.sh script..."

# Parse config values using jq (install jq if not present)
if ! command -v jq >/dev/null 2>&1; then
    echo "jq is required. Please install jq."
    exit 1
fi

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use: sudo $0)"
    exit 1
fi

TAILSCALE_ENABLE=$(jq -r '.TAILSCALE_ENABLE' "$CONFIG_FILE")
PIHOLE_ENABLE=$(jq -r '.PIHOLE_ENABLE' "$CONFIG_FILE")

# Tailscale service management
if [ "$TAILSCALE_ENABLE" = "true" ]; then
    echo "Enabling and starting tailscaled.service..."
    systemctl enable --now tailscaled.service
    sudo tailscale up
else
    echo "Disabling and stopping tailscaled.service..."
    systemctl disable --now tailscaled.service
    sudo tailscale down
fi

# Pi-hole FTL service management
if [ "$PIHOLE_ENABLE" = "true" ]; then
    echo "Enabling and starting pihole-FTL.service..."
    systemctl enable --now pihole-FTL.service
    systemctl disable --now dnsmasq
else
    echo "Disabling and stopping pihole-FTL.service..."
    systemctl disable --now pihole-FTL.service
fi

# Syncthing service management (example: always enable for ccaluser)


# Syncthing service management
if [ "$SYNCTHING_ENABLE" = "true" ]; then
    echo "Enabling and starting syncthingservice..."
    systemctl enable --now syncthing@ccalv2.service
else
    echo "Disabling and stopping syncthing service..."
    systemctl disable --now syncthing@ccalv2.service
fi

echo "Restarting ccalpy.service to apply changes..."
sudo systemctl stop ccalpy.service
sudo systemctl start ccalpy.service


# ...existing code...

BASHRC="/home/ccalv2/.bashrc"

# Remove any previous CCal_V2 Service Info block
sed -i '/# === CCal_V2 Service Info ===/,$d' "$BASHRC"

INFO_BLOCK="# === CCal_V2 Service Info ===\n"

ANY_ENABLED=false

if [ "$TAILSCALE_ENABLE" = "true" ]; then
    TAILSCALE_IP=$(hostname -I | awk '{print $1}')
    INFO_BLOCK+="echo -e \"\033[1;36mTailscale is ENABLED. Access this device via Tailscale IP: \033[1;33m\$TAILSCALE_IP\033[0m\"\n"
    ANY_ENABLED=true
fi

if [ "$PIHOLE_ENABLE" = "true" ]; then
    INFO_BLOCK+="echo -e \"\033[1;36mPi-hole is ENABLED. Access the web UI at: \033[1;33mhttp://localhost/admin\033[0m\"\n"
    ANY_ENABLED=true
fi

SYNCTHING_ENABLE=$(jq -r '.SYNCTHING_ENABLE' "$CONFIG_FILE")
if [ "$SYNCTHING_ENABLE" = "true" ]; then
    INFO_BLOCK+="echo -e \"\033[1;36mSyncthing is ENABLED. Access the web UI at: \033[1;33mhttp://localhost:8384\033[0m\"\n"
    ANY_ENABLED=true
fi

INFO_BLOCK+="echo -e \"\033[1;36mTo remove these messages, delete the CCal_V2 Service Info block from your .bashrc\033[0m\"\n"

# Only append if any service is enabled
if [ "$ANY_ENABLED" = true ]; then
    echo -e "$INFO_BLOCK" >> "$BASHRC"
fi

echo "Service info in .bashrc updated."
source .bashrc

echo "Service management complete."
