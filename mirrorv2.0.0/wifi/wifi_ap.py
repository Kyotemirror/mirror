"""
wifi_ap.py
Controls the temporary Wi‑Fi Access Point used for provisioning.
"""

import json
import os
import subprocess
import time

CONFIG_PATH = "/home/pi/mirror/config.json"
HOSTAPD_CONF = "/etc/hostapd/kyote.conf"
DNSMASQ_CONF = "/etc/dnsmasq.d/kyote.conf"
IFACE = "wlan0"

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def write_hostapd(conf):
    with open(HOSTAPD_CONF, "w") as f:
        f.write(conf)

def write_dnsmasq(conf):
    with open(DNSMASQ_CONF, "w") as f:
        f.write(conf)

def start_ap():
    cfg = load_config()["wifi"]["access_point"]

    ssid = cfg["ssid"]
    channel = cfg.get("channel", 6)
    ip = cfg["ip"]
    netmask = cfg["netmask"]

    print("📡 Starting Wi‑Fi Access Point:", ssid)

    # Stop services if already running
    run("systemctl stop hostapd || true")
    run("systemctl stop dnsmasq || true")

    # Configure static IP
    run(f"ip link set {IFACE} down")
    run(f"ip addr flush dev {IFACE}")
    run(f"ip addr add {ip}/24 dev {IFACE}")
    run(f"ip link set {IFACE} up")

    # hostapd config
    hostapd_conf = f"""
interface={IFACE}
driver=nl80211
ssid={ssid}
hw_mode=g
channel={channel}
wmm_enabled=0
auth_algs=1
ignore_broadcast_ssid=0
"""
    write_hostapd(hostapd_conf.strip())

    # dnsmasq config
    dnsmasq_conf = f"""
interface={IFACE}
dhcp-range=192.168.4.10,192.168.4.100,12h
"""
    write_dnsmasq(dnsmasq_conf.strip())

    # Start services
    run("systemctl start dnsmasq")
    run("systemctl start hostapd")

    print("✅ Wi‑Fi AP started")

def stop_ap():
    print("🛑 Stopping Wi‑Fi Access Point")
    run("systemctl stop hostapd || true")
    run("systemctl stop dnsmasq || true")
    run(f"ip addr flush dev {IFACE}")

if __name__ == "__main__":
    start_ap()