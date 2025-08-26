## ⚡ Quick Start
If you have the prebuilt version all you need to do is the following:

1. Plug the micro sd into your computer
2. Open the boot part of the drive and update the:
    - **country**
    - **ssid**
    - **psk**
    variables with your country code, ssid, and wifi password.
3. Safely remove the micro sd and insert it into the pi
4. Power it on and wait for it to show up on your network!
*Tip you can use the ping command to know when it is ready to be used*
5. Naviagate in a browser to (http://itsIP:3000)
6. Go through the settings and configure it.

### Default Usernames and passwords
username: ccalv2
password: raspberry



### Build your own
Heres some information so you can build your own Contrib Cal v2!

Want to build your own?  
1. Flash a Pi Zero W with Raspbian.
2. Download and run the setup script.
    `sudo curl https://raw.githubusercontent.com/Logan-Fouts/CCal_V2/refs/heads/main/setup.sh | sh`

**Example `config.json`:**
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


**This needs to be changed when actually being used**