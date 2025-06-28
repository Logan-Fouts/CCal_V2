# Contrib Cal v2

Contrib Cal v2 is a customizable, hackable contribution tracking device powered by a Raspberry Pi Zero W. It visualizes your GitHub activity with real-time LED feedback and integrates with various services for enhanced functionality.

---

## Why PCBWay?

🤝 **Sponsored by PCBWay**

- **Quality:** Crystal-clear silkscreen and precise tolerances for perfect fits.
- **Fast:** Quick turnaround from design to doorstep.
- **Affordable:** Great for makers and small-batch projects.
- **Global Shipping:** Reliable delivery worldwide.

Professional PCB manufacturing makes all the difference for clean builds.

Want your own PCBs made? PCBWay offers high-quality PCB fabrication and 3D printing so you can build your own from scratch!  
Get started: [Go to PCBWay.com](https://pcbway.com) and upload your Gerber files.

---

## Features

- **Real GitHub Sync:** Visualize your GitHub activity with real-time LED feedback via the GitHub API.
- **Guilt Mode:** LEDs glow red when you miss commits.
- **Tailscale Integration:** Operate as a Tailscale node for secure remote access.
- **Git Webhooks:** LEDs blink on commit, push, or other repository events.
- **Pi-hole Support:** Optionally run Pi-hole for network-wide ad blocking.
- **100% Hackable:** Customize animations and logic in Python.
- **Beginner-Friendly:** Program with Thonny IDE (no toolchains needed).
- **DIY Build:** 3D-printable case & hand-solderable LED matrix.

---

## Web Interface

- **LED and Addons Control:** Manage LED settings and enable addons through a web interface built with plain HTML, CSS, and JavaScript, served by an Apache web server.

---

## Quick Start

1. **Install Thonny** (Python IDE for beginners)
2. **Connect your Raspberry Pi Zero W** via USB or network
3. **Clone the repo** and open `/src/main.py` in Thonny
4. **Run and configure:**  
	- Save `main.py` and `config.json` to your device
	- Edit `config.json` with your WiFi and GitHub credentials

```json
{
  "WIFI_SSID": "*",
  "WIFI_PASSWORD": "*",
  "GITHUB_USERNAME": "*",
  "GITHUB_TOKEN": "*",
  "STARTUP_ANIMATION": 3
}
```

---

## Build Guide

**You'll Need:**
- Raspberry Pi Zero W
- WS2812B NeoPixels (28+)
- 3D-printed case
- Micro-USB cable
- Soldering tools

---

## Tech Stack

- Python
- HTML
- CSS
- JavaScript

---

Contrib Cal v2 makes your coding contributions visible and interactive. Contributions welcome!
