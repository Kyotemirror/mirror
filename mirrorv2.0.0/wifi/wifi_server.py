#!/usr/bin/env python3
"""
wifi_server.py
Minimal local web server for Wi‑Fi provisioning.

Flow:
- User connects phone to Kyote-Setup AP
- Phone opens http://192.168.4.1 (via QR)
- User enters SSID + password
- Server stops AP (hostapd/dnsmasq), switches wlan0 back to client mode
- Connects using NetworkManager (nmcli) if available, else wpa_supplicant
- Verifies connection, then optionally restarts kyote-mirror

No external Python deps (standard library only).
"""

import json
import os
import subprocess
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

CONFIG_PATH = "/home/pi/mirror/config.json"
WPA_CONF = "/etc/wpa_supplicant/wpa_supplicant.conf"
IFACE_DEFAULT = "wlan0"

# Captive portal friendly endpoints (optional)
CAPTIVE_PATHS = {
    "/generate_204",           # Android
    "/hotspot-detect.html",    # Apple
    "/ncsi.txt",               # Windows
    "/connecttest.txt",        # Windows
    "/fwlink",                 # Windows
}

def sh(cmd, check=True):
    """Run shell command string."""
    return subprocess.run(cmd, shell=True, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def cmd(args, check=True):
    """Run command list."""
    return subprocess.run(args, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def nm_available():
    """True if nmcli exists and NetworkManager is active."""
    try:
        cmd(["nmcli", "-t", "general", "status"], check=True)
        r = sh("systemctl is-active NetworkManager", check=False)
        return (r.stdout.strip() == "active")
    except Exception:
        return False

def stop_ap_services():
    """
    Stop AP services.
    We try kyote services first if you create them, then fall back to hostapd/dnsmasq.
    """
    sh("systemctl stop kyote-wifi-ap.service", check=False)
    sh("systemctl stop kyote-wifi-server.service", check=False)  # will stop this if it’s managed by systemd (ignored here)
    sh("systemctl stop hostapd", check=False)
    sh("systemctl stop dnsmasq", check=False)

def restore_client_mode(iface: str):
    """
    Bring interface back to a normal client state.
    """
    sh(f"ip addr flush dev {iface}", check=False)
    sh(f"ip link set {iface} down", check=False)
    sh(f"ip link set {iface} up", check=False)
    # dhcpcd is common on Raspberry Pi OS
    sh("systemctl restart dhcpcd", check=False)

def connect_with_nmcli(iface: str, ssid: str, password: str) -> bool:
    """
    Connect using NetworkManager.
    nmcli dev wifi connect <SSID> password <password>
    NetworkManager saves the profile and auto-connects on reboot. [1](https://www.makeuseof.com/connect-to-wifi-with-nmcli/)
    """
    try:
        sh("nmcli radio wifi on", check=False)
        # Use iface explicitly in case multiple radios exist
        cmd(["nmcli", "dev", "wifi", "connect", ssid, "password", password, "ifname", iface], check=True)
        return True
    except Exception:
        return False

def ensure_wpa_conf_header():
    """
    Ensure wpa_supplicant.conf has sane global settings.
    Typical header includes ctrl_interface and update_config. [2](https://fleetstack.io/blog/raspberry-pi-etc-wpa-supplicant-wpa-supplicant-conf-file)
    """
    if not os.path.exists(WPA_CONF):
        os.makedirs(os.path.dirname(WPA_CONF), exist_ok=True)
        with open(WPA_CONF, "w") as f:
            f.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n")
            f.write("update_config=1\n")
            f.write("country=US\n")

def connect_with_wpasupplicant(iface: str, ssid: str, password: str) -> bool:
    """
    Connect using wpa_supplicant config + wpa_cli reconfigure.
    Uses wpa_passphrase to generate a proper network block and appends it. [3](https://www.raspberrypi-spy.co.uk/2017/04/manually-setting-up-pi-wifi-using-wpa_supplicant-conf/)[2](https://fleetstack.io/blog/raspberry-pi-etc-wpa-supplicant-wpa-supplicant-conf-file)
    """
    try:
        ensure_wpa_conf_header()

        # Append network block
        # Note: For a first-test installer, appending is OK. Later we can dedupe SSIDs.
        block = cmd(["wpa_passphrase", ssid, password], check=True).stdout

        with open(WPA_CONF, "a") as f:
            f.write("\n# --- Kyote Wi-Fi Provisioning ---\n")
            f.write(block)
            f.write("\n")

        # Ask wpa_supplicant to reload config
        sh(f"wpa_cli -i {iface} reconfigure", check=False)

        # Some systems benefit from restarting wpa_supplicant service
        sh("systemctl restart wpa_supplicant", check=False)

        return True
    except Exception:
        return False

def is_connected_to(ssid: str) -> bool:
    """
    Check current Wi-Fi SSID.
    """
    try:
        r = cmd(["iwgetid", "-r"], check=True).stdout.strip()
        return r == ssid
    except Exception:
        return False

def restart_mirror_service(service_name: str):
    sh(f"systemctl restart {service_name}", check=False)

HTML_FORM = """<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Kyote Wi‑Fi Setup</title>
  <style>
    body { font-family: sans-serif; background:#0b0b0b; color:#fff; padding:20px; }
    .card { max-width:420px; margin:auto; background:#161616; padding:18px; border-radius:12px; }
    input, button { width:100%; padding:12px; margin-top:10px; border-radius:10px; border:0; }
    input { background:#222; color:#fff; }
    button { background:#3b82f6; color:#fff; font-weight:600; }
    .muted { color:#aaa; font-size: 0.95em; margin-top:10px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>Kyote Wi‑Fi Setup</h2>
    <form method="POST" action="/connect">
      <label>Network (SSID)</label>
      <input name="ssid" value="{ssid}" {ssid_lock} required />
      <label>Password</label>
      <input type="password" name="password" placeholder="Wi‑Fi password" required />
      <button type="submit">Connect</button>
    </form>
    <div class="muted">
      After connecting, the mirror will switch back to normal mode automatically.
    </div>
  </div>
</body>
</html>
"""

def result_page(title: str, message: str) -> str:
    return f"""<!doctype html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body {{ font-family: sans-serif; background:#0b0b0b; color:#fff; padding:20px; }}
.card {{ max-width:420px; margin:auto; background:#161616; padding:18px; border-radius:12px; }}
a {{ color:#60a5fa; }}
</style>
</head>
<body><div class="card">
<h2>{title}</h2>
<p>{message}</p>
</div></body></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        cfg = load_config()
        ap_cfg = cfg.get("wifi", {}).get("access_point", {})
        mirror_service = cfg.get("systemd", {}).get("mirror_service", "kyote-mirror.service")

        path = urlparse(self.path)

        # Captive portal probes: redirect to /
        if path.path in CAPTIVE_PATHS:
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        if path.path == "/":
            qs = parse_qs(path.query)
            ssid = (qs.get("ssid", [""])[0] or "").strip()
            ssid_lock = "readonly" if ssid else ""
            html = HTML_FORM.format(ssid=ssid, ssid_lock=ssid_lock)

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        if path.path == "/status":
            # Basic status endpoint
            connected = False
            cur = ""
            try:
                cur = cmd(["iwgetid", "-r"], check=False).stdout.strip()
                connected = bool(cur)
            except Exception:
                pass

            body = json.dumps({"connected": connected, "ssid": cur}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        cfg = load_config()
        wifi_cfg = cfg.get("wifi", {})
        iface = wifi_cfg.get("interface", IFACE_DEFAULT)
        mirror_service = cfg.get("systemd", {}).get("mirror_service", "kyote-mirror.service")

        if self.path != "/connect":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8", errors="ignore")
        form = parse_qs(raw)

        ssid = (form.get("ssid", [""])[0] or "").strip()
        password = (form.get("password", [""])[0] or "")

        if not ssid or not password:
            html = result_page("Missing info", "Please provide both SSID and password.")
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        # Stop AP and restore client mode
        stop_ap_services()
        restore_client_mode(iface)

        # Connect
        ok = False
        if nm_available():
            ok = connect_with_nmcli(iface, ssid, password)
        if not ok:
            ok = connect_with_wpasupplicant(iface, ssid, password)

        # Wait a bit for association/DHCP
        for _ in range(15):
            if is_connected_to(ssid):
                ok = True
                break
            time.sleep(1)

        if ok:
            # Restart mirror app (back to normal pages)
            restart_mirror_service(mirror_service)

            html = result_page(
                "Connected!",
                f"Successfully connected to <b>{ssid}</b>.<br><br>"
                "You can close this page. The mirror should return to normal mode."
            )
            self.send_response(200)
        else:
            html = result_page(
                "Connection failed",
                f"Could not connect to <b>{ssid}</b>. "
                "Double-check the password and try again."
            )
            self.send_response(200)

        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        # Silence default HTTP logs (prevents password leaks in logs)
        return


def main():
    cfg = load_config()
    ap_cfg = cfg.get("wifi", {}).get("access_point", {})
    ip = ap_cfg.get("ip", "192.168.4.1")
    port = 80

    # Bind to all interfaces so phone can reach it on AP subnet
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Kyote Wi‑Fi server listening on http://{ip}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    main()