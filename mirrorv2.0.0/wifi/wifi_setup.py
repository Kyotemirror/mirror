#!/usr/bin/env python3
"""
Kyote Wi‑Fi Setup (UI)
Path: /home/pi/mirror/wifi/wifi_setup.py

Shows SSID scan list, starts AP + server, and displays QR or URL.
"""

import json
import os
import platform
import subprocess
import time
import urllib.parse

import pygame

CONFIG_PATH = "/home/pi/mirror/config.json"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DIM = (120, 120, 120)
ACCENT = (60, 165, 250)


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def sh(cmd, check=False):
    return subprocess.run(cmd, shell=True, check=check,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def cmd(args, check=False):
    return subprocess.run(args, check=check,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def nmcli_available():
    try:
        r = cmd(["nmcli", "-t", "general", "status"], check=True)
        return r.returncode == 0
    except Exception:
        return False


def scan_ssids(iface="wlan0", limit=20):
    """Scan SSIDs using nmcli if available; else fallback to iw."""
    ssids = []

    if nmcli_available():
        r = cmd(["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi", "list"], check=False)
        seen = set()
        for line in r.stdout.splitlines():
            if not line.strip():
                continue
            ssid = line.split(":")[0].strip()
            if ssid and ssid not in seen:
                seen.add(ssid)
                ssids.append(ssid)
        return ssids[:limit]

    sh(f"ip link set {iface} up", check=False)
    r = sh(f"iw dev {iface} scan 2>/dev/null | grep 'SSID:' | sed 's/SSID: //g'", check=False)
    seen = set()
    for s in [l.strip() for l in r.stdout.splitlines() if l.strip()]:
        if s not in seen:
            seen.add(s)
            ssids.append(s)

    return ssids[:limit]


def try_start_services():
    """
    Start AP + Wi‑Fi server.
    Uses systemd services if they exist; otherwise runs scripts directly.
    """
    r1 = sh("systemctl start kyote-wifi-ap.service", check=False)
    r2 = sh("systemctl start kyote-wifi-server.service", check=False)
    if r1.returncode == 0 and r2.returncode == 0:
        return True, "Started kyote-wifi-ap + kyote-wifi-server"

    # fallback to direct execution (requires privileges)
    ap_py = "/home/pi/mirror/wifi/wifi_ap.py"
    srv_py = "/home/pi/mirror/wifi/wifi_server.py"

    ok = True
    msgs = []
    if os.path.exists(ap_py):
        rr = sh(f"python3 {ap_py} &", check=False)
        ok = ok and (rr.returncode == 0)
        msgs.append("wifi_ap.py started")
    else:
        ok = False
        msgs.append("wifi_ap.py missing")

    time.sleep(0.5)

    if os.path.exists(srv_py):
        rr = sh(f"python3 {srv_py} &", check=False)
        ok = ok and (rr.returncode == 0)
        msgs.append("wifi_server.py started")
    else:
        ok = False
        msgs.append("wifi_server.py missing")

    return ok, "; ".join(msgs)


def load_fonts(font_scale=1.0):
    return {
        "title": pygame.font.SysFont("sans", int(52 * font_scale)),
        "body": pygame.font.SysFont("sans", int(30 * font_scale)),
        "small": pygame.font.SysFont("sans", int(22 * font_scale)),
    }


def make_qr_surface(url, size_px=360):
    """Optional QR rendering (requires qrcode + pillow)."""
    try:
        import qrcode
        from PIL import Image
    except Exception:
        return None

    qr = qrcode.QRCode(border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((size_px, size_px))
    data = img.tobytes()
    return pygame.image.fromstring(data, img.size, "RGB")


def run():
    cfg = load_config()
    wifi_cfg = cfg.get("wifi", {})
    ap_cfg = wifi_cfg.get("access_point", {})
    qr_cfg = wifi_cfg.get("qr", {})

    iface = wifi_cfg.get("interface", "wlan0")
    ap_ip = ap_cfg.get("ip", "192.168.4.1")
    base_url = qr_cfg.get("url", f"http://{ap_ip}")

    pi_zero = (platform.machine() == "armv6l")
    font_scale = 0.9 if pi_zero else 1.0

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.mouse.set_visible(True)

    fonts = load_fonts(font_scale)
    clock = pygame.time.Clock()

    # Scan BEFORE AP starts
    ssids = scan_ssids(iface=iface, limit=20)
    if not ssids:
        ssids = ["(No networks found)"]

    selected = 0
    state = "select"  # select -> qr
    url_to_show = ""
    status_line = ""

    def draw_select():
        screen.fill(BLACK)
        screen.blit(fonts["title"].render("Wi‑Fi Setup", True, WHITE), (60, 40))
        screen.blit(fonts["small"].render("Select your Wi‑Fi network", True, GRAY), (60, 105))
        screen.blit(fonts["small"].render("Use ↑ ↓ and Enter (or tap) to choose", True, DIM), (60, 140))

        y = 200
        row_h = 44
        boxes = []
        for i, s in enumerate(ssids[:12]):
            is_sel = (i == selected)
            if is_sel:
                pygame.draw.rect(screen, (20, 20, 20), pygame.Rect(45, y - 6, screen.get_width() - 90, row_h))
            prefix = "▶ " if is_sel else "  "
            color = WHITE if is_sel else GRAY
            screen.blit(fonts["body"].render(prefix + s, True, color), (60, y))
            boxes.append((pygame.Rect(45, y - 6, screen.get_width() - 90, row_h), i))
            y += row_h

        if status_line:
            screen.blit(fonts["small"].render(status_line, True, ACCENT), (60, screen.get_height() - 70))

        pygame.display.flip()
        return boxes

    def draw_qr(url):
        screen.fill(BLACK)
        screen.blit(fonts["title"].render("Connect on your phone", True, WHITE), (60, 40))
        screen.blit(fonts["small"].render("Scan QR to enter Wi‑Fi password", True, GRAY), (60, 105))

        qr_surface = make_qr_surface(url, size_px=300 if pi_zero else 360)
        if qr_surface:
            rect = qr_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(qr_surface, rect)
        else:
            screen.blit(fonts["small"].render("(Install qrcode+pillow to show QR — URL below)", True, DIM), (60, 160))
            screen.blit(fonts["body"].render(url, True, WHITE), (60, 220))

        screen.blit(fonts["small"].render("After connecting, the mirror will continue automatically.", True, DIM),
                    (60, screen.get_height() - 70))
        pygame.display.flip()

    boxes = []
    while True:
        if state == "select":
            boxes = draw_select()
        else:
            draw_qr(url_to_show)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

                if state == "select":
                    if event.key == pygame.K_UP:
                        selected = max(0, selected - 1)
                    elif event.key == pygame.K_DOWN:
                        selected = min(len(ssids) - 1, selected + 1)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        chosen = ssids[selected]
                        if chosen.startswith("("):
                            status_line = "No selectable networks found."
                            continue

                        ok, msg = try_start_services()
                        status_line = msg if ok else f"Failed to start services: {msg}"

                        qs = urllib.parse.urlencode({"ssid": chosen})
                        url_to_show = f"{base_url}/?{qs}"
                        state = "qr"

            if event.type == pygame.MOUSEBUTTONDOWN and state == "select":
                mx, my = event.pos
                for rect, idx in boxes:
                    if rect.collidepoint(mx, my):
                        selected = idx
                        chosen = ssids[selected]
                        if chosen.startswith("("):
                            status_line = "No selectable networks found."
                            break

                        ok, msg = try_start_services()
                        status_line = msg if ok else f"Failed to start services: {msg}"

                        qs = urllib.parse.urlencode({"ssid": chosen})
                        url_to_show = f"{base_url}/?{qs}"
                        state = "qr"
                        break

        clock.tick(30)