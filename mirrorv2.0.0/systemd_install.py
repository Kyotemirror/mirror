import subprocess

SERVICE = """[Unit]
Description=Kyote Smart Mirror
After=graphical.target display-manager.service
Wants=graphical.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/mirror
ExecStart=/usr/bin/python3 /home/pi/mirror/app.py
Restart=always
RestartSec=2

Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=graphical.target
"""

with open("/etc/systemd/system/kyote-mirror.service", "w") as f:
    f.write(SERVICE)

subprocess.run("systemctl daemon-reload", shell=True, check=True)
subprocess.run("systemctl enable kyote-mirror", shell=True, check=True)