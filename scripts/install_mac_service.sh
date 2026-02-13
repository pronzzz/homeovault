#!/bin/bash

# Configuration
APP_NAME="com.homeovault.server"
PROJECT_DIR="$(pwd)"
PYTHON_EXEC="$(which python3)"
PLIST_PATH="$HOME/Library/LaunchAgents/$APP_NAME.plist"

echo "Installing HomeoVault Auto-Launch Service..."
echo "Project Directory: $PROJECT_DIR"
echo "Python Executable: $PYTHON_EXEC"

# Create the plist file
cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$APP_NAME</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_EXEC</string>
        <string>-m</string>
        <string>uvicorn</string>
        <string>backend.main:app</string>
        <string>--host</string>
        <string>0.0.0.0</string>
        <string>--port</string>
        <string>8000</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/launch_out.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/launch_err.log</string>
</dict>
</plist>
EOF

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

# Load the service
launchctl unload "$PLIST_PATH" 2>/dev/null
launchctl load "$PLIST_PATH"

echo "Success! HomeoVault will now start automatically continuously."
echo "You can check status with: launchctl list | grep $APP_NAME"
echo "Logs are available in: $PROJECT_DIR/logs/"
