#!/bin/bash
set -e 

DEBUG=false

USERNAME=$(logname)
echo USERNAME: $USERNAME

# Color codes
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
RED='\033[1;31m'
NC='\033[0m' # No Color

run_cmd() {
    if [ "$DEBUG" = true ]; then
        echo -e "${YELLOW}[DEBUG] Would run: $*${NC}"
    else
        eval "$@"
    fi
}

print_section() {
    echo -e "\n${BLUE}========================================"
    echo -e "$1"
    echo -e "========================================${NC}\n"
}

print_status() {
    echo -e "${GREEN}✔ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✖ $1${NC}"
}

echo -e "${GREEN}"
echo "          _____                    _____                    _____                    _____  "
echo "         /\    \                  /\    \                  /\    \                  /\    \ "
echo "        /::\    \                /::\    \                /::\    \                /::\____\\"
echo "       /::::\    \              /::::\    \              /::::\    \              /:::/    /"
echo "      /::::::\    \            /::::::\    \            /::::::\    \            /:::/    / "
echo "     /:::/\:::\    \          /:::/\:::\    \          /:::/\:::\    \          /:::/    /  "
echo "    /:::/  \:::\    \        /:::/  \:::\    \        /:::/__\:::\    \        /:::/    /   "
echo "   /:::/    \:::\    \      /:::/    \:::\    \      /::::\   \:::\    \      /:::/    /    "
echo "  /:::/    / \:::\    \    /:::/    / \:::\    \    /::::::\   \:::\    \    /:::/    /     "
echo " /:::/    /   \:::\    \  /:::/    /   \:::\    \  /:::/\:::\   \:::\    \  /:::/    /      "
echo "/:::/____/     \:::\____\/:::/____/     \:::\____\/:::/  \:::\   \:::\____\/:::/____/       "
echo "\:::\    \      \::/    /\:::\    \      \::/    /\::/    \:::\  /:::/    /\:::\    \       "
echo " \:::\    \      \/____/  \:::\    \      \/____/  \/____/ \:::\/:::/    /  \:::\    \      "
echo "  \:::\    \               \:::\    \                       \::::::/    /    \:::\    \     "
echo "   \:::\    \               \:::\    \                       \::::/    /      \:::\    \    "
echo "    \:::\    \               \:::\    \                      /:::/    /        \:::\    \   "
echo "     \:::\    \               \:::\    \                    /:::/    /          \:::\    \  "
echo "      \:::\    \               \:::\    \                  /:::/    /            \:::\    \ "
echo "       \:::\____\               \:::\____\                /:::/    /              \:::\____\\"
echo "        \::/    /                \::/    /                \::/    /                \::/    /"
echo "         \/____/                  \/____/                  \/____/                  \/____/ "
echo "                                                                                             "
echo -e "${NC}"
echo -e "${BLUE}        CCal_V2 Automated Setup${NC}\n"


print_status "Systemd service files copied and customized."
print_section "System Update & Dependency Installation"
echo "Updating system and installing dependencies..."
run_cmd "sudo apt update"
run_cmd "sudo apt upgrade -y"
run_cmd "sudo apt install -y git nodejs npm portaudio19-dev python3-pip jq syncthing unattended-upgrades"
print_status "System packages installed."

# Enable unattended upgrades
run_cmd "sudo dpkg-reconfigure --priority=low unattended-upgrades"

print_section "Syncthing Service Setup"
run_cmd "sudo systemctl enable --now syncthing@$USERNAME.service"
run_cmd "sudo systemctl disable --now syncthing@$USERNAME.service"
print_status "Syncthing service toggled."

print_section "Installing Tailscale"
run_cmd "curl -fsSL https://tailscale.com/install.sh | sh"
print_status "Tailscale installed."

print_section "Installing Pi-hole"
run_cmd "curl -sSL https://install.pi-hole.net | bash"
print_status "Pi-hole installed."

# Just a temp password that needs to be changed by the user
run_cmd "sudo pihole setpassword raspberry"

print_section "Node.js Verification"
if ! command -v node &> /dev/null; then
    print_warning "Node.js not found, installing nodejs..."
    run_cmd "sudo apt install -y nodejs"
    print_status "nodejs-legacy installed."
else
    print_status "Node.js is present."
fi

print_section "Cloning Repository"
if [ ! -d "CCal_V2" ]; then
    run_cmd "git clone https://github.com/Logan-Fouts/CCal_V2.git"
    print_status "Repository cloned."
else
    print_warning "CCal_V2 directory already exists, skipping clone."
fi

print_section "Installing WebGUI Dependencies"
run_cmd "cd CCal_V2/WebGUI && npm install express@4.17.1 body-parser@1.19.0 ejs@3.1.6 && cd -"
print_status "WebGUI dependencies installed."

print_section "Installing Python Dependencies"
run_cmd "cd CCal_V2/LedControl"
if pip install --help | grep -q -- '--break-system-packages'; then
    run_cmd "sudo pip install --upgrade pip --break-system-packages"
    run_cmd "sudo pip install -r requirements.txt --break-system-packages"
else
    run_cmd "sudo pip install --upgrade pip"
    run_cmd "sudo pip install -r requirements.txt"
fi
run_cmd "cd -"
print_status "Python dependencies installed."

print_section "Configuring System Services"
run_cmd "sudo cp CCal_V2/SystemdServices/ccalpy.service /etc/systemd/system/"
run_cmd "sudo cp CCal_V2/SystemdServices/ccalpy_gui.service /etc/systemd/system/"
print_status "Systemd service files copied."

# Modify systemd files with username
USERNAME=$(logname)
run_cmd "sed 's|__USERNAME__|$USERNAME|g' CCal_V2/SystemdServices/ccalpy.service > /tmp/ccalpy.service"
run_cmd "sudo mv /tmp/ccalpy.service /etc/systemd/system/ccalpy.service"
run_cmd "sed 's|__USERNAME__|$USERNAME|g' CCal_V2/SystemdServices/ccalpy_gui.service > /tmp/ccalpy_gui.service"
run_cmd "sudo mv /tmp/ccalpy_gui.service /etc/systemd/system/ccalpy_gui.service"
print_status "Systemd service files copied and customized."

# Patch setup_addons.sh
run_cmd "sed -i 's|USERNAME=\"username\"|USERNAME=\"$USERNAME\"|g' CCal_V2/WebGUI/setup_addons.sh"
print_status "setup_addons.sh username patched."

# Patch server.js
run_cmd "sed -i 's|USERNAME=\"username\"|USERNAME=\"$USERNAME\"|g' CCal_V2/WebGUI/server.js"
print_status "server.js username patched."

# Patch main.py
run_cmd "sed -i 's|USERNAME=\"username\"|USERNAME=\"$USERNAME\"|g' CCal_V2/LedControl/main.py"
print_status "main.py username patched."

run_cmd "touch /home/$USERNAME/CCal_V2/WebGUI/.env"
run_cmd "echo \"CCAL_WEBGUI_USER=$USERNAME\" >> /home/$USERNAME/CCal_V2/WebGUI/.env"
run_cmd "echo \"CCAL_WEBGUI_PASS=raspberry\" >> /home/$USERNAME/CCal_V2/WebGUI/.env"

print_section "Enabling and Starting Services"
run_cmd "sudo systemctl daemon-reload"
run_cmd "sudo systemctl enable --now ccalpy.service"
run_cmd "sudo systemctl enable --now ccalpy_gui.service"
print_status "Services enabled and started."

run_cmd "touch /home/$USERNAME/CCal_V2/config.json"

# Speed up boot time
run_cmd "sudo systemctl disable NetworkManager-wait-online.service"
run_cmd "sudo systemctl disable ModemManager.service"
run_cmd "sudo systemctl disable avahi-daemon.service"
run_cmd "sudo systemctl disable bluetooth.service"

# Run the setup_addons.sh script
run_cmd "sudo bash /home/$USERNAME/CCal_V2/WebGUI/setup_addons.sh"

print_section "Setup Completed Successfully"
echo -e "${GREEN}All done!${NC}"
echo "Services status:"
run_cmd "sudo systemctl status ccalpy.service ccalpy_gui.service --no-pager"
