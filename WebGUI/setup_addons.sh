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
# echo "Ensuring syncthing@ccaluser.service is enabled and started..."
# systemctl enable --now syncthing@ccaluser.service

echo "Restarting ccalpy.service to apply changes..."
sudo systemctl stop ccalpy.service
sudo systemctl start ccalpy.service

echo "Service management complete."
