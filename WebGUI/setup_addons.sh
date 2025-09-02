#!/bin/bash

USERNAME="ccal"
echo USERNAME: $USERNAME

IP_ADDR=$(hostname -I | awk '{print $1}')

CONFIG_FILE="/home/$USERNAME/CCal_V2/config.json"
BASHRC="/home/$USERNAME/.bashrc"



echo "Starting setup_addons.sh script..."

# --- Mode selection: prod (default), dev, debug ---
MODE="${MODE:-prod}"
if [[ $# -gt 0 && ( "$1" == "dev" || "$1" == "debug" ) ]]; then
    MODE="$1"
fi
echo "Running in MODE: $MODE"

# --- Root check ---
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use: sudo $0)"
    exit 1
fi

# --- Check config file existence ---
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Config file not found: $CONFIG_FILE"
    exit 1
fi

# --- Check jq existence ---
if ! command -v jq >/dev/null 2>&1; then
    echo "jq is required. Please install jq."
    exit 1
fi

# --- Service command wrappers for dev/debug mode ---
if [[ "$MODE" != "prod" ]]; then
    SYSTEMCTL() { echo "[DEBUG] Would run: systemctl $*"; }
    SUDO() { echo "[DEBUG] Would run: sudo $*"; }
else
    SYSTEMCTL() { systemctl "$@"; }
    SUDO() { sudo "$@"; }
fi

# --- Read config values, treat null as false ---
get_bool() {
    local val
    val=$(jq -r ".$1 // false" "$CONFIG_FILE")
    [[ "$val" == "true" ]]
}

TAILSCALE_ENABLE=false
PIHOLE_ENABLE=false
SYNCTHING_ENABLE=false
get_bool TAILSCALE_ENABLE && TAILSCALE_ENABLE=true
get_bool PIHOLE_ENABLE && PIHOLE_ENABLE=true
get_bool SYNCTHING_ENABLE && SYNCTHING_ENABLE=true

# --- Tailscale service management ---
if $TAILSCALE_ENABLE; then
    echo "Enabling and starting tailscaled.service..."
    SYSTEMCTL enable --now tailscaled.service
    if [[ "$MODE" == "prod" ]]; then
        if SUDO tailscale status &>/dev/null; then
            SUDO tailscale up
            TAILSCALE_UP_OUTPUT=""
        else
            TAILSCALE_UP_OUTPUT="Tailscale is not logged in. Please run 'sudo tailscale up' manually to authenticate."
        fi
    else
        echo "[DEBUG] Would run: sudo tailscale up"
        TAILSCALE_UP_OUTPUT="[DEBUG] Would check Tailscale login status"
    fi
else
    echo "Disabling and stopping tailscaled.service..."
    SYSTEMCTL disable --now tailscaled.service
    SUDO tailscale down || true
    TAILSCALE_UP_OUTPUT=""
fi

# --- Pi-hole FTL service management ---
if $PIHOLE_ENABLE; then
    echo "Enabling and starting pihole-FTL.service..."
    SYSTEMCTL enable --now pihole-FTL.service
    SYSTEMCTL disable --now dnsmasq || true
else
    echo "Disabling and stopping pihole-FTL.service..."
    SYSTEMCTL disable --now pihole-FTL.service
fi

# --- Syncthing service management ---
if $SYNCTHING_ENABLE; then
    echo "Enabling and starting syncthing@$USERNAME.service..."
    SYSTEMCTL enable --now syncthing@$USERNAME.service
    SYSTEMCTL start syncthing@$USERNAME.service
else
    echo "Disabling and stopping syncthing@$USERNAME.service..."
    SYSTEMCTL disable --now syncthing@$USERNAME.service
fi

# --- Restart ccalpy.service ---
echo "Restarting ccalpy.service to apply changes..."
SUDO systemctl restart ccalpy.service

# --- .bashrc block update ---
if [ ! -f "$BASHRC" ]; then
    echo "# .bashrc created by setup_addons.sh" > "$BASHRC"
fi

# Remove any previous CCal_V2 Service Info block
sed -i '/# === CCal_V2 Service Info ===/,$d' "$BASHRC"

INFO_BLOCK="# === CCal_V2 Service Info ===\n"
INFO_BLOCK+="echo -e \"\n\033[1;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\""
INFO_BLOCK+="\necho -e \"  \033[1;36m🚦 CCal_V2 Service Status:\033[0m\""
INFO_BLOCK+="\necho -e \"    \033[1;33mManagement GUI: http://$IP_ADDR:8080\033[0m\""
INFO_BLOCK+="\necho -e \"\033[1;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\""

ANY_ENABLED=false
if $TAILSCALE_ENABLE; then
    INFO_BLOCK+="\necho -e \"  \033[1;36mTailscale:\033[0m \033[1;32mENABLED\033[0m\""
    if [ -n "${TAILSCALE_UP_OUTPUT:-}" ]; then
        INFO_BLOCK+="\necho -e \"    \033[1;33m$(echo "$TAILSCALE_UP_OUTPUT" | sed 's/"/\\"/g')\033[0m\""
    else
        INFO_BLOCK+="\necho -e \"    \033[1;33mManage Tailscale: sudo tailscale web\033[0m\""
    fi
    ANY_ENABLED=true
fi

if $PIHOLE_ENABLE; then
    INFO_BLOCK+="\necho -e \"  \033[1;36mPi-hole:\033[0m   \033[1;32mENABLED\033[0m\""
    INFO_BLOCK+="\necho -e \"    \033[1;33mWeb UI: http://$IP_ADDR/admin\033[0m\""
    ANY_ENABLED=true
fi

if $SYNCTHING_ENABLE; then
    INFO_BLOCK+="\necho -e \"  \033[1;36mSyncthing:\033[0m \033[1;32mENABLED\033[0m\""
    INFO_BLOCK+="\necho -e \"    \033[1;33mWeb UI: http://$IP_ADDR:8384\033[0m\""
    INFO_BLOCK+="\necho -e \"    \033[1;33mNote: Syncthing only allows local IP connections by default.\""
    INFO_BLOCK+="\necho -e \"    \033[1;33mTo access remotely, use: ssh -L 8385:localhost:8384 $USERNAME@$IP_ADDR (then visit http://localhost:8385 on your computer)\""
    INFO_BLOCK+="\necho -e \"    \033[1;33mTo allow access via IP, change the Syncthing settings from '127.0.0.1' to '0.0.0.0' under GUI Listen Address.\""
    ANY_ENABLED=true
fi

INFO_BLOCK+="\necho -e \"\033[1;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n\""

echo -e "$INFO_BLOCK" >> "$BASHRC"


echo "Service info in .bashrc updated."
echo "SETUP_ADDONS_SUCCESS"
exit 0
