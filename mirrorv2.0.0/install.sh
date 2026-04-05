# ------------------------------
# Data files
# ------------------------------
echo "📁 Creating data files..."

mkdir -p "$DATA_DIR/cache"

if [[ ! -f "$DATA_DIR/calendar.ics" ]]; then
  cat > "$DATA_DIR/calendar.ics" <<EOF
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Kyote Smart Mirror//EN
END:VCALENDAR
EOF
fi

echo "✅ Data files ready"

# ------------------------------
# Verification
# ------------------------------
echo "🔍 Verifying installs..."

python3 <<EOF
import pygame, feedparser, icalendar, pytz
print("✅ pygame", pygame.__version__)
print("✅ feedparser", feedparser.__version__)
print("✅ icalendar", icalendar.__version__)
print("✅ pytz", pytz.__version__)
EOF

echo "==============================="
echo " ✅ Kyote Smart Mirror Installed "
echo "==============================="
echo ""
echo "Next steps:"
echo "  • Verify config.json"
echo "  • Reboot the Pi"
echo "  • Mirror will auto-start"