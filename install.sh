#!/bin/bash
echo "Installing AGY Switcher..."

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install it first."
    exit 1
fi

APP_DIR="/Applications/AGY Switcher.app"
BACKUP_DIR="$HOME/.gemini/auth_backups"
RES_DIR="$APP_DIR/Contents/Resources"
VENV_DIR="$BACKUP_DIR/venv"

mkdir -p "$BACKUP_DIR"

# Create a Virtual Environment to comply with macOS PEP 668
echo "Setting up Python Virtual Environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install dependencies securely inside the venv
pip install --upgrade pip
pip install rumps Pillow pyobjc-framework-Cocoa

# Build App Bundle
echo "Building Native Mac App..."
# The osacompile script must use the python binary from our venv!
osacompile -e 'do shell script "nohup '$VENV_DIR'/bin/python3 '$BACKUP_DIR'/AGY_Switcher.py >/dev/null 2>&1 &"' -o "$APP_DIR"

# Convert script to launch silently (LSUIElement)
plutil -insert LSUIElement -bool true "$APP_DIR/Contents/Info.plist"
plutil -replace CFBundleName -string "AGY Switcher" "$APP_DIR/Contents/Info.plist"

# Copy Assets and Script
cp src/AGY_Switcher.py "$BACKUP_DIR/AGY_Switcher.py"
cp assets/*.png "$RES_DIR/"

# Make the squircle mask for the main app icon
cat << 'PY_EOF' > /tmp/set_icon.py
from PIL import Image, ImageDraw, ImageFilter
import Cocoa
import sys, os

img_path = "assets/logo.png"
if not os.path.exists(img_path): sys.exit(1)

img = Image.open(img_path).convert("RGBA")
width, height = img.size
margin = int(width * 0.12)
img = img.crop((margin, margin, width - margin, height - margin))
width, height = img.size
mask = Image.new("L", (width, height), 0)
draw = ImageDraw.Draw(mask)
radius = int(width * 0.225)
draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(1))
img.putalpha(mask)

canvas = Image.new("RGBA", (width + 40, height + 40), (0,0,0,0))
shadow = Image.new("RGBA", (width + 40, height + 40), (0,0,0,0))
s_draw = ImageDraw.Draw(shadow)
s_draw.rounded_rectangle((20, 30, width + 20, height + 30), radius=radius, fill=(0,0,0, 60))
shadow = shadow.filter(ImageFilter.GaussianBlur(10))
canvas = Image.alpha_composite(canvas, shadow)
canvas.paste(img, (20, 20), img)

out_path = "/tmp/agy_squircle.png"
canvas.save(out_path)

app_path = "/Applications/AGY Switcher.app"
cocoa_img = Cocoa.NSImage.alloc().initWithContentsOfFile_(out_path)
Cocoa.NSWorkspace.sharedWorkspace().setIcon_forFile_options_(cocoa_img, app_path, 0)
PY_EOF

echo "Applying Icons..."
python3 /tmp/set_icon.py

# Resign
codesign --force --deep --sign - "$APP_DIR"

# Add to Login Items
echo "Adding to Login Items..."
osascript -e 'tell application "System Events" to make login item at end with properties {path:"/Applications/AGY Switcher.app", hidden:false}'

echo "Starting AGY Switcher..."
open "$APP_DIR"
echo "Done! Look at your Menu Bar!"
