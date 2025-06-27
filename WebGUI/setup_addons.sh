#!/bin/bash

CONFIG_FILE="$(dirname "$0")/config.json"

# Parse config values using jq (install jq if not present)
if ! command -v jq >/dev/null 2>&1; then
    echo "jq is required. Please install jq."
    exit 1
fi

TAILSCALE_ENABLE=$(jq -r '.TAILSCALE_ENABLE' "$CONFIG_FILE")
TAILSCALE_AUTHKEY=$(jq -r '.TAILSCALE_AUTHKEY' "$CONFIG_FILE")
PIHOLE_ENABLE=$(jq -r '.PIHOLE_ENABLE' "$CONFIG_FILE")
PIHOLE_WEBPASSWORD=$(jq -r '.PIHOLE_WEBPASSWORD' "$CONFIG_FILE")
GITEA_ENABLE=$(jq -r '.GITEA_ENABLE' "$CONFIG_FILE")
GITEA_ADMIN_USER=$(jq -r '.GITEA_ADMIN_USER' "$CONFIG_FILE")
GITEA_ADMIN_PASS=$(jq -r '.GITEA_ADMIN_PASS' "$CONFIG_FILE")

# Tailscale setup
if [ "$TAILSCALE_ENABLE" = "true" ]; then
    echo "Setting up Tailscale..."
    if ! command -v tailscale >/dev/null 2>&1; then
        curl -fsSL https://tailscale.com/install.sh | sh
    fi
    sudo tailscale up --authkey "$TAILSCALE_AUTHKEY"
else
    echo "Tailscale not enabled."
fi

# Pi-hole setup
if [ "$PIHOLE_ENABLE" = "true" ]; then
    echo "Setting up Pi-hole..."
    if ! command -v pihole >/dev/null 2>&1; then
        curl -sSL https://install.pi-hole.net | bash /dev/stdin --unattended
    fi
    if [ -n "$PIHOLE_WEBPASSWORD" ]; then
        sudo pihole -a -p "$PIHOLE_WEBPASSWORD" "$PIHOLE_WEBPASSWORD"
    fi
else
    echo "Pi-hole not enabled."
fi

# Gitea setup
if [ "$GITEA_ENABLE" = "true" ]; then
    echo "Setting up Gitea..."
    if ! id -u git >/dev/null 2>&1; then
        sudo adduser --system --group --disabled-password --home /home/git git
    fi
    if [ ! -f /usr/local/bin/gitea ]; then
        wget -O /usr/local/bin/gitea https://dl.gitea.io/gitea/1.21.11/gitea-1.21.11-linux-arm-6
        chmod +x /usr/local/bin/gitea
    fi
    # Add more setup here, such as creating a service or initial admin user
    echo "Gitea binary installed. Please complete setup via web interface."
else
    echo "Gitea not enabled."
fi