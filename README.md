# Kyote Smart Mirror

Kyote is a Raspberry Pi–based **smart mirror dashboard** designed to run as an appliance.
It provides a fullscreen, auto‑starting UI with:

- 🕒 Clock
- 🌤 Weather (Open‑Meteo, no API key)
- 📅 Calendar (iCloud / Google via ICS feed)
- 📰 News (RSS)
- 📶 Wi‑Fi onboarding (AP + QR code)
- 🚀 systemd auto‑start
- 🖼 Plymouth boot splash

The project is built to be **path‑agnostic**, **PEP‑668 compliant**, and stable on
**Raspberry Pi OS Bookworm**.

---

## ✅ Supported Hardware

- Raspberry Pi Zero 2 W
- Raspberry Pi 3 / 4 / 5
- HDMI display
- Onboard or USB Wi‑Fi adapter

---

## ✅ Operating System

- Raspberry Pi OS (Bookworm recommended)
- systemd required

---

## 📂 Project Layout
mirrorv2.0.0/
├── app.py                  # Main application
├── paths.py                # Path resolver (NO hard‑coded paths)
├── config.json              # Runtime configuration
├── assets/
│   ├── boot/               # Plymouth splash assets
│   └── fonts/              # Bundled fonts
├── data/
│   └── cache/              # Cached API data
├── pages/
│   ├── clock.py
│   ├── weather.py
│   ├── calendar.py
│   ├── news.py
│   └── wifi_setup.py
├── wifi/
│   ├── wifi_ap.py
│   ├── wifi_server.py
│   └── wifi_setup.py
├── system/
│   └── wifi_services.py
├── systemd_install.py
├── boot_config.py
├── install_kyote.sh        # One‑command installer
└── venv/                   # Python virtual environment
