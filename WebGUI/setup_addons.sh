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
    if sudo tailscale status &>/dev/null; then
        sudo tailscale up
    else
        TAILSCALE_UP_OUTPUT="Tailscale is not logged in. Please run 'sudo tailscale up' manually to authenticate."
    fi
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

# Syncthing service management
if [ "$SYNCTHING_ENABLE" = "true" ]; then
    echo "Enabling and starting syncthingservice..."
    systemctl enable --now syncthing@ccalv2.service
    systemctl start syncthing@ccalv2.service
else
    echo "Disabling and stopping syncthing service..."
    systemctl disable --now syncthing@ccalv2.service
fi

echo "Restarting ccalpy.service to apply changes..."
sudo systemctl stop ccalpy.service
sudo systemctl start ccalpy.service


BASHRC="/home/ccalv2/.bashrc"

# Remove any previous CCal_V2 Service Info block
sed -i '/# === CCal_V2 Service Info ===/,$d' "$BASHRC"

INFO_BLOCK="# === CCal_V2 Service Info ===\n"
INFO_BLOCK+="echo -e \"\n\033[1;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\""
INFO_BLOCK+="\necho -e \"  \033[1;36m🚦 CCal_V2 Service Status:\033[0m\""
INFO_BLOCK+="\necho -e \"\033[1;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\""

ANY_ENABLED=false
if [ "$TAILSCALE_ENABLE" = "true" ]; then
    INFO_BLOCK+="\necho -e \"  \033[1;36mTailscale:\033[0m \033[1;32mENABLED\033[0m\""
    if [ -n "$TAILSCALE_UP_OUTPUT" ]; then
        INFO_BLOCK+="\necho -e \"    \033[1;33m$(echo "$TAILSCALE_UP_OUTPUT" | sed 's/"/\\"/g')\033[0m\""
    else
        INFO_BLOCK+="\necho -e \"    \033[1;33mManage Tailscale: sudo tailscale web\033[0m\""
    fi
    ANY_ENABLED=true
fi

if [ "$PIHOLE_ENABLE" = "true" ]; then
    INFO_BLOCK+="\necho -e \"  \033[1;36mPi-hole:\033[0m   \033[1;32mENABLED\033[0m\""
    INFO_BLOCK+="\necho -e \"    \033[1;33mWeb UI: http://<ip>/admin\033[0m\""
    ANY_ENABLED=true
fi

SYNCTHING_ENABLE=$(jq -r '.SYNCTHING_ENABLE' "$CONFIG_FILE")
if [ "$SYNCTHING_ENABLE" = "true" ]; then
    INFO_BLOCK+="\necho -e \"  \033[1;36mSyncthing:\033[0m \033[1;32mENABLED\033[0m\""
    INFO_BLOCK+="\necho -e \"    \033[1;33mWeb UI: http://localhost:8384\033[0m\""
    INFO_BLOCK+="\necho -e \"    \033[1;33mRemote: ssh -L 8385:localhost:8384 ccalv2@<ip> (then visit http://localhost:8385)\033[0m\""
    ANY_ENABLED=true
fi

INFO_BLOCK+="\necho -e \"\033[1;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\""
INFO_BLOCK+="\necho -e \"  \033[1;90mTo remove these messages, delete the CCal_V2 Service Info block from your .bashrc\033[0m\""
INFO_BLOCK+="\necho -e \"\033[1;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n\""

# Only append if any service is enabled
if [ "$ANY_ENABLED" = true ]; then
    echo -e "$INFO_BLOCK" >> "$BASHRC"
fi

echo "Service info in .bashrc updated."

echo "Service management complete."
