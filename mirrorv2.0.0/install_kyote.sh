#!/usr/bin/env bash
set -e

echo "======================================"
echo " Kyote Smart Mirror – One‑Command Install"
echo "======================================"

PROJECT_ROOT="/home/kyote/mirror/mirrorv2.0.0"
VENV_PATH="$PROJECT_ROOT/venv"

if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root:"
  echo "   sudo bash install_kyote.sh"
  exit 1
fi

echo "📦 Updating system and installing APT dependencies..."
apt update && apt install -y \
  python3 \
  python3-venv \
  python3-pip \
  python3-dev \
  python3-setuptools \
  python3-wheel \
  libsdl2-2.0-0 \
  libsdl2-image-2.0-0 \
  libsdl2-mixer-2.0-0 \
  libsdl2-ttf-2.0-0 \
  libfreetype6 \
  libjpeg-dev \
  fonts-dejavu-core \
  hostapd \
  dnsmasq \
  plymouth \
  plymouth-themes

echo "✅ APT dependencies installed"

echo "🐍 Creating Python virtual environment..."
python3 -m venv "$VENV_PATH"

echo "📚 Installing Python packages inside venv..."
"$VENV_PATH/bin/pip" install --upgrade pip
"$VENV_PATH/bin/pip" install \
  pygame \
  requests \
  feedparser \
  icalendar \
  pytz \
  qrcode \
  pillow

echo "✅ Python dependencies installed"

echo "📁 Ensuring data directories exist..."
mkdir -p "$PROJECT_ROOT/data/cache"

echo "🧹 Fixing ownership (kyote user)..."
chown -R kyote:kyote "$PROJECT_ROOT"

echo "✅ Installation complete"
echo ""
echo "▶ To run the mirror manually:"
echo ""
echo "sudo $VENV_PATH/bin/python $PROJECT_ROOT/app.py"
echo ""
echo "🔁 Next steps:"
echo " • Configure config.json (calendar, weather, wifi)"
echo " • Optional: enable systemd service"
echo "=================YOUGOTITKID==============="
