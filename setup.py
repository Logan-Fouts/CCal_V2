#!/usr/bin/env python3
import os
import subprocess
import time
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Configuration
AP_SSID = "PiZeroW_Config"  # Name of the access point
AP_PASSWORD = "raspberry"   # Password for the access point
AP_CHANNEL = "6"            # WiFi channel for the access point
INTERFACE = "wlan0"         # WiFi interface name
CHECK_WAIT_TIME = 10        # Seconds to wait before checking connection
CONNECTION_TIMEOUT = 20     # Seconds to wait for connection before starting AP

# HTML Template (same as before)
HTML_TEMPLATE = """<!DOCTYPE html>...</html>"""

def check_wifi_connection():
    """Check if we're connected to a WiFi network"""
    try:
        result = subprocess.run(['iwconfig', INTERFACE], capture_output=True, text=True)
        return "ESSID:off/any" not in result.stdout
    except:
        return False

def wait_for_connection(timeout):
    """Wait for WiFi connection with timeout"""
    print(f"Waiting up to {timeout} seconds for WiFi connection...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if check_wifi_connection():
            print("Connected to WiFi!")
            return True
        time.sleep(5)  # Check every 5 seconds
    
    print("No WiFi connection detected.")
    return False

def setup_access_point():
    """Configure the Pi as an access point using NetworkManager"""
    print("Setting up access point using NetworkManager...")

    # Delete any existing AP connection
    subprocess.run(["nmcli", "connection", "delete", AP_SSID], check=False)

    # Add a new WiFi AP connection
    result = subprocess.run([
        "nmcli", "device", "wifi", "hotspot",
        "ifname", INTERFACE,
        "con-name", AP_SSID,
        "ssid", AP_SSID,
        "password", AP_PASSWORD
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Failed to create hotspot: {result.stderr}")
    else:
        print(f"Access point '{AP_SSID}' is now active. Connect to it with password '{AP_PASSWORD}'")

def configure_wifi(ssid, password):
    """Configure the Pi to connect to a WiFi network using NetworkManager"""
    print(f"Configuring WiFi to connect to {ssid} using NetworkManager")
    # Delete any existing connection with the same SSID
    subprocess.run(["nmcli", "connection", "delete", ssid], check=False)
    # Add new connection
    result = subprocess.run([
        "nmcli", "device", "wifi", "connect", ssid, "password", password, "ifname", INTERFACE
    ], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"nmcli error: {result.stderr}")

@app.route('/', methods=['GET', 'POST'])
def wifi_config():
    message = ""
    success = False
    
    if request.method == 'POST':
        ssid = request.form.get('ssid')
        password = request.form.get('password', '')
        
        if ssid:
            try:
                configure_wifi(ssid, password)
                message = f"Success! Configured to connect to {ssid}. The Pi will reboot to apply changes."
                success = True
                subprocess.Popen(["sudo", "sh", "-c", "sleep 5 && reboot"])
            except Exception as e:
                message = f"Error configuring WiFi: {str(e)}"
        else:
            message = "Please provide an SSID"
    
    return render_template_string(HTML_TEMPLATE, message=message, success=success)

def main():
    # Initial delay to allow normal boot process to complete
    print(f"Waiting {CHECK_WAIT_TIME} seconds before checking connection...")
    time.sleep(CHECK_WAIT_TIME)
    
    # Check for existing WiFi connection
    if check_wifi_connection():
        print("Already connected to WiFi. Exiting.")
        return
    
    # If not connected, wait for connection with timeout
    if wait_for_connection(CONNECTION_TIMEOUT):
        print("Successfully connected to WiFi. Exiting.")
        return
    
    # If still not connected, start configuration AP
    setup_access_point()
    print("Starting configuration web server...")
    app.run(host='0.0.0.0', port=80)

if __name__ == '__main__':
    main()
