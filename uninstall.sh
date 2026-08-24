#!/bin/bash
echo "Uninstalling AGY Switcher..."

APP_DIR="/Applications/AGY Switcher.app"
BACKUP_DIR="$HOME/.gemini/auth_backups"

# Remove from Login Items
echo "Removing from Login Items..."
osascript -e 'tell application "System Events" to delete login item "AGY Switcher"' 2>/dev/null

# Kill the background widget
echo "Stopping background processes..."
pkill -f "AGY_Switcher.py" || true
pkill -f "Native_Mac_Widget.py" || true

# Delete App and Backups
echo "Deleting App and Auth Backups..."
rm -rf "$APP_DIR"
rm -rf "$BACKUP_DIR"

echo "Uninstall Complete. All AGY Switcher files and tokens have been securely removed."
