#!/usr/bin/env python3
import os
import subprocess
import sys
import time

LOGO = """
██╗  ██╗██╗   ██╗ ██████╗ ████████╗███████╗
██║ ██╔╝╚██╗ ██╔╝██╔═══██╗╚══██╔══╝██╔════╝
█████╔╝  ╚████╔╝ ██║   ██║   ██║   █████╗  
██╔═██╗   ╚██╔╝  ██║   ██║   ██║   ██╔══╝  
██║  ██╗   ██║   ╚██████╔╝   ██║   ███████╗
╚═╝  ╚═╝   ╚═╝    ╚═════╝    ╚═╝   ╚══════╝
"""

def run(cmd):
    print(f"→ {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def header(msg):
    print("\n" + "=" * 40)
    print(msg)
    print("=" * 40 + "\n")

def main():
    if os.geteuid() != 0:
        print("Please run with sudo:")
        print("  sudo python3 installer.py")
        sys.exit(1)

    print(LOGO)
    time.sleep(1)

    # ----------------------------
    # System dependencies
    # ----------------------------
    header("Installing system dependencies")
    run("apt update")
    run(
        "apt install -y "
        "python3 python3-pip python3-dev python3-setuptools python3-wheel "
        "libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0 "
        "libatlas-base-dev libjpeg-dev libfreetype6-dev libglib2.0-0 "
        "hostapd dnsmasq"
    )

    # ----------------------------
    # Python dependencies
    # ----------------------------
    header("Installing Python dependencies")
    run("pip3 install --no-cache-dir pygame feedparser icalendar pytz")

    # Optional but recommended (QR codes)
    run("pip3 install --no-cache-dir qrcode pillow || true")

    # ----------------------------
    # Directory structure
    # ----------------------------
    header("Ensuring directory structure")
    run("mkdir -p /home/pi/mirror/data/cache")
    run("mkdir -p /home/pi/mirror/wifi")
    run("mkdir -p /home/pi/mirror/pages")
    run("touch /home/pi/mirror/wifi/__init__.py")
    run("touch /home/pi/mirror/pages/__init__.py")
    run("chown -R pi:pi /home/pi/mirror")

    # ----------------------------
    # Quiet boot + splash
    # ----------------------------
    header("Configuring quiet boot + splash")
    run("python3 boot_config.py")

    # ----------------------------
    # systemd services
    # ----------------------------
    header("Installing systemd services")
    run("python3 systemd_install.py")

    # Wi‑Fi services (if present)
    if os.path.exists("/home/pi/mirror/system/wifi_services.py"):
        run("python3 /home/pi/mirror/system/wifi_services.py")
    else:
        print("⚠️  wifi_services.py not found — Wi‑Fi services will need to be enabled manually")

    # ----------------------------
    # Done
    # ----------------------------
    header("Installation complete")
    print("Rebooting in 5 seconds...")
    time.sleep(5)
    run("reboot")

if __name__ == "__main__":
    main()