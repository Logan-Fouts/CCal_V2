# Getting Started with CCal v2

This guide will help you set up your Contribution Calendar v2.  
Follow the steps below to get everything working.

---

## Quick Start (Prebuilt Image)

1. **Prepare Your SD Card**
    - Insert the micro SD card into your computer.
    - Open the **boot** partition on the SD card and locate the `wpa_supplicant.conf` file (if it does not exist, create it in the root of the boot partition).
    - Update these fields:
        - `country` — your country code (like US, GB, DE)
        - `ssid` — your WiFi network name
        - `psk` — your WiFi password

2. **Insert & Power On**
    - Safely eject the SD card and put it in your Pi Zero.
    - Power on the Pi and wait for it to connect to your network.
    - *(Tip: You can use the `ping` command to check when the device is online.)*

3. **Access the Web Interface**
    - Open a browser and go to:  
      `http://<device-ip>:8080`
    - Replace `<device-ip>` with your Pi's IP address.

4. **Configure Settings**
    - Log in with the default credentials below.
    - Use the web interface to finish setup.

---

### Default WebGUI Credentials

- **Username:** `ccal`
- **Password:** `raspberry`

---

### Set Your Own WebGUI Login

To set your own username and password for the WebGUI, run this command (replace `yourusername` and `yourpassword`):

```sh
echo -e "CCAL_WEBGUI_USER=yourusername\nCCAL_WEBGUI_PASS=yourpassword" > ~/CCal_V2/WebGUI/.env
```

---

## Build Your Own

If you want to build CCal v2 yourself:

1. **Flash Raspbian**
    - Install the latest Raspbian OS on a Pi Zero W.

2. **Download & Run the Setup Script**
    ```sh
    sudo curl https://raw.githubusercontent.com/Logan-Fouts/CCal_V2/refs/heads/main/setup.sh | sh
    ```

3. **Configure Your Device**
    - Follow the Quick Start steps above.

---

### Example `config.json`

Here’s an example configuration file you can use or edit:

```json
{
   "GITHUB_USERNAME": "Logan-Fouts",
   "GITHUB_TOKEN": "*",
   "STARTUP_ANIMATION": 3,
   "TAILSCALE_ENABLE": true,
   "PIHOLE_ENABLE": true,
   "SYNCTHING_ENABLE": true,
   "LAST_EVENT_ID": "*",
   "OPENWEATHERMAP_API_KEY": "*",
   "WEATHER_LAT": 0.000,
   "WEATHER_LON": 0.000,
   "BRIGHTNESS": 80
}
```

---

## Tips

- **Change your WebGUI password** after your first login.
- Make sure your Pi and your computer are on the same network.
- If you need help, open an issue on the [GitHub repository](https://github.com/Logan-Fouts/CCal_V2).

---

Thanks for trying out CCal v2! Enjoy your new Contribution Calendar.