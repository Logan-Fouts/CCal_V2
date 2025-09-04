# Contrib Cal v2

Contrib Cal v2 is a contribution tracker built around a Raspberry Pi Zero W. It shows your GitHub activity using LEDs and includes a web interface for easy setup and control. The project is open, hackable, and designed for anyone interested in building their own contribution calendar.

---

## Sponsored by PCBWay

[![PCBWay](https://www.pcbway.com/project/img/images/logo.png)](https://pcbway.com)

PCBWay provided the PCBs for this project. They offer PCB fabrication and 3D printing with quick turnaround and worldwide shipping.  
[Check out PCBWay.com](https://pcbway.com) if you want to order your own boards.

---

## Features

- **GitHub Sync:** Shows your GitHub activity on an LED matrix.
- **Weather Animations:** Displays weather effects and temperature.
- **Event Alerts:** LEDs flash for new GitHub events.
- **Tailscale:** Optionally connect your Pi to a Tailscale network.
- **Syncthing:** Optionally run a Syncthing node for file sync.
- **Pi-hole:** Optionally run Pi-hole for ad blocking.
- **Customizable:** Animations and logic are written in Python.
- **DIY Build:** Use a 3D-printed case and a custom or hand-wired LED matrix.
- **Web Interface:** Configure settings and add-ons from your browser.

---

## Hardware Files

- **3D Print Files:** Available on Thingiverse at [https://www.thingiverse.com/thing:7136260](https://www.thingiverse.com/thing:7136260)
- **KiCad PCB Design Files:** Located in the `KiCad` folder in this repository.
- **PCBWay Order Zip:** The `PCBWay file.zip` in this repo can be uploaded directly to PCBWay—just drag and drop it on their site to order your board.

---

## Hardware Used

- **LEDs:** 28x SMD5050 RGB addressable LEDs (SK6812 or similar)
- **Microcontroller:** 1x Raspberry Pi Zero W (Pi Zero 2 W may work, but not tested)
- **Power Adapter:** 5V PD Decoy USB TYPE-C QC PD 2.0 3.0 3.1 Voltage Triggers Adapter (Fast Charge Power Supply, PD to DC Charging)

You can substitute

---

## Web Interface

You can manage most settings and add-ons through a simple web page hosted on the Pi.

---

## Build Guide

### What You’ll Need

- Raspberry Pi Zero W
- SMD 5050 NeoPixels (28 or more recommended)
- 3D-printed case (optional)
- Soldering tools

---

## Getting Started

See [GettingStarted.md](./GettingStarted.md) for step-by-step instructions on flashing, setup, and configuration.

---

## Contributing

Pull requests and suggestions are welcome.  
If you run into issues or have ideas, feel free to open an issue on GitHub.

---

## Coming Soon

- API for controlling the LED matrix over the network

---

Thanks for checking out Contrib Cal