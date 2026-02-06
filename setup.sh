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
echo " ______   _______ "
echo "(  __  \ (  ____ \\"
echo "| (  \  )| (    \/"
echo "| |   ) || | \_  )"
echo "| (__/  )| (___) |"
echo "(______/ (_______)"
echo -e "${NC}"
echo -e "${BLUE}        Daily-Grid Automated Setup${NC}\n"


print_section "System Update & Dependency Installation"
echo "Updating system and installing dependencies..."
run_cmd "sudo apt update"
run_cmd "sudo apt upgrade -y"
run_cmd "sudo apt install -y git nodejs npm portaudio19-dev python3-pip python3-venv jq syncthing unattended-upgrades"
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
if [ ! -d "Daily-Grid" ]; then
    run_cmd "git clone https://github.com/Logan-Fouts/Daily-Grid.git"
    print_status "Repository cloned."
else
    print_warning "Daily-Grid directory already exists, skipping clone."
fi

print_section "Installing WebGUI Dependencies"
run_cmd "cd Daily-Grid/WebGUI && sudo npm install express@4.17.1 body-parser@1.19.0 ejs@3.1.6 && cd -"
print_status "WebGUI dependencies installed."

print_section "Installing Python Dependencies - GLOBALLY"
run_cmd "cd Daily-Grid/Controller"

# First ensure we have the latest pip and it's working
print_status "Checking/upgrading pip globally..."
run_cmd "sudo apt update && sudo apt install --reinstall -y python3-pip"

# Check Python version and use appropriate installation method
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)

if [[ "$PYTHON_VERSION" > "3.10" ]] || [[ "$PYTHON_VERSION" == "3.10" ]]; then
    # Python 3.10+ supports --break-system-packages
    print_status "Python $PYTHON_VERSION detected, using --break-system-packages flag"
    
    # Upgrade pip first using the new flag
    run_cmd "sudo python3 -m pip install pip --break-system-packages"
    
    # Install requirements globally with the flag
    run_cmd "sudo python3 -m pip install -r requirements.txt --break-system-packages"
    
    # Install package in development mode globally
    run_cmd "sudo python3 -m pip install -e . --break-system-packages"
else
    # For older Python versions, use alternate approach
    print_status "Python $PYTHON_VERSION detected, using global installation without flag"
    
    # First remove any problematic pip installation
    run_cmd "sudo apt remove -y python3-pip 2>/dev/null || true"
    run_cmd "sudo apt install --reinstall -y python3-pip"
    
    # Install using python3 -m pip (more reliable than pip command)
    run_cmd "sudo python3 -m pip install --upgrade pip"
    
    # Try installation with --no-deps first, then individual packages
    print_status "Installing requirements.txt..."
    while IFS= read -r line || [[ -n "$line" ]]; do
        if [[ ! -z "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
            echo "Installing: $line"
            run_cmd "sudo python3 -m pip install $line" || \
            run_cmd "sudo python3 -m pip install --no-deps $line" || \
            print_warning "Failed to install $line, continuing..."
        fi
    done < requirements.txt
    
    # Try to install the package in development mode
    print_status "Installing package in development mode..."
    run_cmd "sudo python3 -m pip install -e ." || \
    print_warning "Development mode installation failed, trying without -e flag..." && \
    run_cmd "sudo python3 -m pip install ."
fi

run_cmd "cd -"
print_status "Python dependencies installed globally."

print_section "Configuring System Services"
run_cmd "sudo cp Daily-Grid/SystemdServices/dailygrid.service /etc/systemd/system/"
run_cmd "sudo cp Daily-Grid/SystemdServices/dailygrid_gui.service /etc/systemd/system/"

# Modify systemd files with username
run_cmd "sed 's|__USERNAME__|$USERNAME|g' Daily-Grid/SystemdServices/dailygrid.service > /tmp/dailygrid.service"
run_cmd "sudo mv /tmp/dailygrid.service /etc/systemd/system/dailygrid.service"
run_cmd "sed 's|__USERNAME__|$USERNAME|g' Daily-Grid/SystemdServices/dailygrid_gui.service > /tmp/dailygrid_gui.service"
run_cmd "sudo mv /tmp/dailygrid_gui.service /etc/systemd/system/dailygrid_gui.service"
print_status "Systemd service files copied and customized."

# Patch setup_addons.sh
run_cmd "sudo sed -i 's|USERNAME=\"username\"|USERNAME=\"$USERNAME\"|g' Daily-Grid/WebGUI/setup_addons.sh"
print_status "setup_addons.sh username patched."

# Patch server.js
run_cmd "sudo sed -i 's|USERNAME=\"username\"|USERNAME=\"$USERNAME\"|g' Daily-Grid/WebGUI/server.js"
print_status "server.js username patched."

# Patch main.py
run_cmd "sudo sed -i 's|USERNAME = \"username\"|USERNAME = \"$USERNAME\"|g' Daily-Grid/Controller/src/led_control/cli/main.py"
print_status "main.py username patched."

# Prompt for WebGUI username and password
read -p "Enter WebGUI username [default: $USERNAME]: " WEBGUI_USER
WEBGUI_USER=${WEBGUI_USER:-$USERNAME}
read -s -p "Enter WebGUI password [default: raspberry]: " WEBGUI_PASS
echo
WEBGUI_PASS=${WEBGUI_PASS:-raspberry}

run_cmd "touch /home/$USERNAME/Daily-Grid/WebGUI/.env"
run_cmd "echo \"DAILYGRID_WEBGUI_USER=$WEBGUI_USER\" > /home/$USERNAME/Daily-Grid/WebGUI/.env"
run_cmd "echo \"DAILYGRID_WEBGUI_PASS=$WEBGUI_PASS\" >> /home/$USERNAME/Daily-Grid/WebGUI/.env"

print_section "Enabling and Starting Services"
run_cmd "sudo systemctl daemon-reload"
run_cmd "sudo systemctl enable --now dailygrid.service"
run_cmd "sudo systemctl enable --now dailygrid_gui.service"
print_status "Services enabled and started."

run_cmd "touch /home/$USERNAME/Daily-Grid/config.json"

# Speed up boot time
run_cmd "sudo systemctl disable NetworkManager-wait-online.service"
run_cmd "sudo systemctl disable ModemManager.service"
run_cmd "sudo systemctl disable avahi-daemon.service"
run_cmd "sudo systemctl disable bluetooth.service"

# Run the setup_addons.sh script
run_cmd "sudo bash /home/$USERNAME/Daily-Grid/WebGUI/setup_addons.sh"

print_section "Setup Completed Successfully"
echo -e "${GREEN}All done!${NC}"
echo "Services status:"
run_cmd "sudo systemctl status dailygrid.service dailygrid_gui.service --no-pager"
