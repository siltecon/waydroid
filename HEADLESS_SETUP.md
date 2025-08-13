# Headless Waydroid Setup Guide

## Overview

Waydroid **requires** a Wayland compositor to function - it cannot run without one. However, you can run it with a **headless Wayland compositor** that doesn't require a physical display or GUI environment.

## Requirements

### Wayland Socket
Waydroid needs:
- A valid `WAYLAND_DISPLAY` environment variable
- An accessible Wayland socket (typically in `$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY`)
- The socket defaults to `wayland-0` if not set

## Headless Wayland Compositors

### 1. Weston (Headless Backend)
```bash
# Install weston
sudo apt install weston

# Run weston with headless backend
weston --backend=headless-backend.so --socket=wayland-1 &

# Or with virtual output
weston --backend=headless-backend.so --width=1920 --height=1080 --socket=wayland-1 &

# Set environment for Waydroid
export WAYLAND_DISPLAY=wayland-1
```

### 2. Cage (Minimal Compositor)
```bash
# Install cage
sudo apt install cage

# Run cage with headless backend
cage -d -s -- sleep infinity &

# Cage creates wayland-0 by default
export WAYLAND_DISPLAY=wayland-0
```

### 3. Sway (Headless Mode)
```bash
# Install sway
sudo apt install sway

# Create headless sway config
cat > ~/.config/sway/headless <<EOF
# Headless Sway config for Waydroid
output HEADLESS-1 {
    mode 1920x1080
}
exec sleep infinity
EOF

# Run sway headless
WLR_BACKENDS=headless sway -c ~/.config/sway/headless &
```

### 4. wayvnc + Headless Compositor (Remote Access)
```bash
# Install wayvnc and sway
sudo apt install wayvnc sway

# Start headless sway
WLR_BACKENDS=headless sway &

# Start VNC server (access on port 5900)
wayvnc 0.0.0.0 5900 &

# Now you can connect via VNC to see the Android UI
```

## Complete Headless Setup

### Step 1: Install Dependencies
```bash
# Core requirements
sudo apt update
sudo apt install waydroid weston

# Optional: for remote access
sudo apt install wayvnc
```

### Step 2: Start Headless Compositor
```bash
# Create a systemd service for headless weston
sudo tee /etc/systemd/system/weston-headless.service <<EOF
[Unit]
Description=Weston Headless Compositor for Waydroid
After=multi-user.target

[Service]
Type=simple
Environment="XDG_RUNTIME_DIR=/run/user/1000"
ExecStart=/usr/bin/weston --backend=headless-backend.so --socket=wayland-headless --width=1920 --height=1080
Restart=always
User=YOUR_USERNAME

[Install]
WantedBy=multi-user.target
EOF

# Start the service
sudo systemctl daemon-reload
sudo systemctl enable --now weston-headless
```

### Step 3: Configure Waydroid
```bash
# Initialize Waydroid (with software rendering for headless)
sudo waydroid init -n

# Start container
sudo systemctl start waydroid-container

# Set display environment
export WAYLAND_DISPLAY=wayland-headless
export XDG_RUNTIME_DIR=/run/user/$(id -u)

# Start session
waydroid session start

# The Android system is now running headless!
```

### Step 4: Interact with Headless Waydroid

#### Option A: Command Line Only
```bash
# Install apps
waydroid app install /path/to/app.apk

# Launch apps (will run but not display)
waydroid app launch com.example.app

# Access shell
waydroid shell

# Use Android Debug Bridge
adb connect 192.168.240.112:5555
adb shell
```

#### Option B: Remote GUI Access (VNC)
```bash
# Start wayvnc on the headless compositor
wayvnc -C /path/to/wayvnc.config 0.0.0.0 5900

# Connect from another machine
vncviewer YOUR_SERVER_IP:5900

# Now you can see and interact with the Android UI
```

#### Option C: Web-based Access (noVNC)
```bash
# Install noVNC
git clone https://github.com/novnc/noVNC.git
cd noVNC

# Start wayvnc
wayvnc 127.0.0.1 5900 &

# Start websockify
./utils/novnc_proxy --vnc localhost:5900 --listen 6080

# Access via browser at http://YOUR_SERVER_IP:6080/vnc.html
```

## Docker Container Setup

```dockerfile
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    waydroid \
    weston \
    wayvnc \
    systemd \
    && rm -rf /var/lib/apt/lists/*

# Setup headless weston
RUN mkdir -p /run/user/1000
ENV XDG_RUNTIME_DIR=/run/user/1000
ENV WAYLAND_DISPLAY=wayland-0

# Start script
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 5900
CMD ["/start.sh"]
```

`start.sh`:
```bash
#!/bin/bash
# Start headless weston
weston --backend=headless-backend.so &
sleep 2

# Initialize and start Waydroid
waydroid init -n
systemctl start waydroid-container
waydroid session start &

# Start VNC server
wayvnc 0.0.0.0 5900

# Keep container running
tail -f /dev/null
```

## Configuration Tips

### 1. Multi-Window Mode
```bash
# Enable multi-window mode for better headless operation
waydroid prop set persist.waydroid.multi_windows true
```

### 2. Set Resolution
```bash
# Set custom resolution
waydroid prop set persist.waydroid.width 1920
waydroid prop set persist.waydroid.height 1080
```

### 3. Disable GPU (Recommended for Headless)
```bash
# Re-initialize with software rendering
sudo waydroid init -f -n
```

### 4. Network Access
```bash
# The Android container uses its own network (192.168.240.0/24)
# Access services via the container IP
CONTAINER_IP=$(waydroid status | grep IP | awk '{print $2}')
```

## Use Cases for Headless Waydroid

1. **CI/CD Testing**: Automated Android app testing
2. **App Servers**: Running Android apps as services
3. **Cloud Gaming**: Stream Android games
4. **Development**: Remote Android development environment
5. **Automation**: Running Android automation tools

## Troubleshooting

### Issue: "Wayland socket doesn't exist"
```bash
# Check if compositor is running
ps aux | grep weston

# Check socket exists
ls -la $XDG_RUNTIME_DIR/wayland-*

# Ensure XDG_RUNTIME_DIR is set
export XDG_RUNTIME_DIR=/run/user/$(id -u)
```

### Issue: "Session already running"
```bash
# Stop existing session
waydroid session stop

# Kill any remaining processes
pkill -f waydroid
```

### Issue: "Cannot connect to display"
```bash
# Ensure WAYLAND_DISPLAY matches compositor socket
export WAYLAND_DISPLAY=wayland-headless

# Verify with
ls -la $XDG_RUNTIME_DIR/$WAYLAND_DISPLAY
```

## Minimal Script Example

```bash
#!/bin/bash
# Simple headless Waydroid setup

# Start headless compositor
weston --backend=headless-backend.so --socket=wayland-headless &
WESTON_PID=$!

# Wait for socket
sleep 3

# Configure environment
export WAYLAND_DISPLAY=wayland-headless
export XDG_RUNTIME_DIR=/run/user/$(id -u)

# Initialize Waydroid (first time only)
[ ! -f /var/lib/waydroid/waydroid.cfg ] && sudo waydroid init -n

# Start services
sudo systemctl start waydroid-container
waydroid session start

# Your automation/testing code here
waydroid app install /path/to/test.apk
waydroid app launch com.test.app

# Cleanup
waydroid session stop
kill $WESTON_PID
```

## Key Points

- ✅ Waydroid **always** needs a Wayland compositor
- ✅ Headless compositors work perfectly (weston, cage, sway)
- ✅ Software rendering (`-n` flag) recommended for headless
- ✅ Remote access possible via VNC/RDP
- ✅ Suitable for automation and CI/CD
- ❌ Cannot run without any Wayland compositor
- ❌ X11 not supported (Wayland only)
