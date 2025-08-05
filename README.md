# Contrib Cal v2

**Contrib Cal v2** is a customizable, hackable contribution tracker powered by a Raspberry Pi Zero W. Visualize your GitHub activity in real time with vibrant LEDs, and unlock a suite of features for makers, coders, and tinkerers.

---

## ✨ Why PCBWay?

🤝 **Sponsored by PCBWay**

- **Quality:** Crystal-clear silkscreen and precise tolerances for perfect fits.
- **Fast:** Rapid turnaround from design to doorstep.
- **Affordable:** Ideal for makers and small-batch projects.
- **Global Shipping:** Reliable delivery worldwide.

Professional PCB manufacturing makes all the difference for clean builds.

Want your own PCBs made? PCBWay offers high-quality PCB fabrication and 3D printing so you can build your own from scratch!  
[Get started at PCBWay.com](https://pcbway.com) — just upload your Gerber files.

---

## 🚀 Features

- **Real GitHub Sync:** Instantly visualize your GitHub activity with LED feedback via the GitHub API.
- **Weather Animations:** LEDs display animated weather effects (sun, rain, clouds, etc.) and show the current temperature in Celsius.
- **Event Alerts:** LEDs flash when new GitHub events are detected.
- **Tailscale Integration:** Secure remote access as a Tailscale node.
- **Syncthing Server:** Host a Syncthing node for seamless file sync.
- **Pi-hole Support:** Optionally run Pi-hole for network-wide ad blocking.
- **100% Hackable:** Customize animations and logic in Python.
- **DIY Build:** 3D-printable case & solder-free LED matrix, or use the custom PCB.
- **Guilt Mode:** LEDs glow red when you miss commits.
- **Web Interface:** Manage settings and addons from your browser.

---

## 🖥️ Web Interface

- **LED & Addon Control:** Easily manage CCal v2 settings and enable/disable features through a simple web UI.

---

## ⚡ Quick Start

Want to build your own?  
1. Flash a Pi Zero W with Raspbian.
2. Download the `setup.sh` script.
3. Make it executable:  
   `sudo chmod +x setup.sh`
4. Run the script:  
   `sudo ./setup.sh`

**Example `config.json`:**
```json
{
   "GITHUB_USERNAME": "Logan-Fouts",
   "GITHUB_TOKEN": "*",
   "STARTUP_ANIMATION": 3,
   "TAILSCALE_ENABLE": true,
   "TAILSCALE_AUTHKEY": "*",
   "PIHOLE_ENABLE": true,
   "SYNCTHING_ENABLE": true,
   "LAST_EVENT_ID": "*",
   "OPENWEATHERMAP_API_KEY": "*",
   "WEATHER_LAT": 0.000,
   "WEATHER_LON": 0.000,
   "BRIGHTNESS": 80
}
```

### Default Usernames and passwords
username: ccalv2
password: raspberry

**This needs to be changed when actually being used**

---

## 🛠️ Build Guide

**You’ll Need:**
- Raspberry Pi Zero W
- WS2812B NeoPixels (28+ recommended)
- Optional: Custom PCB for easy assembly
- 3D-printed case
- Micro-USB cable
- Soldering tools

---

## 🧑‍💻 Tech Stack

- Python
- HTML / CSS / JavaScript

---

Contrib Cal v2 makes your coding contributions visible and interactive.  
**Pull requests and contributions are always welcome!**

---


## Feature to come
- Ambient Weather Mode
- API