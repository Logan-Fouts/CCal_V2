# Getting Started with CCal

This guide will help you set up your Contribution Calendar.  
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
    - **Note:** The first boot can take a while as the Pi sets itself up and connects to WiFi. Be patient—it may take several minutes.
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
*Or just edit the file with whatever text editor you want*
You'll need to use sudo since the files are owned by the root user. You of course can modify the permisions so you dont need to use sudo.
```sh
sudo vim ~/CCal_V2/WebGUI/.env
```

---

## Build Your Own

If you want to build CCal v2 yourself:

1. **Flash Raspbian**
    - Install the latest Raspbian OS on a Pi Zero W (using Pi Imager is recommended).

**Recommended:**  
Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) for the easiest setup.  
- Open Raspberry Pi Imager and select the OS (choose "Raspberry Pi OS Lite (32-bit)" or similar).
- Click the gear icon (⚙️) to set your username, password, WiFi info, and enable SSH.
- Write the image to your micro SD card.
- *(If you’re not using Pi Imager, you can manually edit or create the `wpa_supplicant.conf` file in the boot partition for WiFi setup.)* Take a look at step one from teh quick start above for more help.

2. **SSH into the pi**
    - Wait for it to connect to your wifi then ssh into the pi using the command below *(replace usrename and ip)*:
    ```sh
    ssh username@ip
    ```

3. **Download & Run the Setup Script**
    ```sh
    sudo curl https://raw.githubusercontent.com/Logan-Fouts/CCal_V2/refs/heads/main/setup.sh | sh
    ```
    Or if you are having issues with the interactive shell then use the steps here:
    1. ```sh
       sudo wget https://raw.githubusercontent.com/Logan-Fouts/CCal_V2/refs/heads/main/setup.sh
       ```
    2. ```sh
       sudo chmod +x setup.sh
       ```
    3. ```sh
       sudo ./setup.sh
       ```
    - **Note:** This command will take quite a while to run, as it installs all dependencies and sets up the system.

5. **Source the updated bashrc**
    - Either exit the ssh session then rejoin or run:
    ```sh
    source ~/.bashrc
    ```

4. **Configure Your Device**
    - Follow the Quick Start steps above starting at step 3.
    - If you enable Pi-hole during setup, the only thing you need to do is click through the Pi-hole options when prompted.

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
- Be patient during the first boot and setup—some steps can take several minutes.

---

Thanks for trying out CCal v2! Enjoy your new Contribution Calendar.
