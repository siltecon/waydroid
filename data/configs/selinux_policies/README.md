# Waydroid SELinux Policies

This directory contains SELinux policy modules for Waydroid, providing mandatory access control for the Waydroid container and Android applications.

## Overview

The SELinux policies provide equivalent security controls to the AppArmor profiles, ensuring that:
- The Waydroid container runs in a confined domain
- Android applications are restricted to appropriate resources
- ADB daemon has controlled debugging access
- System integrity is maintained through mandatory access controls

## Policy Modules

### 1. `waydroid.te` / `waydroid.fc`
Main policy for the Waydroid LXC container:
- Defines the `waydroid_t` domain for container processes
- Controls access to system resources, networking, and devices
- Manages mount operations and container lifecycle
- File contexts for Waydroid installation and data directories

### 2. `waydroid_app.te` / `waydroid_app.fc`
Policy for Android applications running within Waydroid:
- Defines the `waydroid_app_t` domain for Android apps
- Restricts app access to appropriate data directories
- Controls network and IPC capabilities
- File contexts for app data and cache directories

### 3. `waydroid_adbd.te` / `waydroid_adbd.fc`
Policy for Android Debug Bridge daemon:
- Defines the `waydroid_adbd_t` domain for ADB
- Provides debugging capabilities with appropriate restrictions
- Controls ptrace and signal permissions
- File contexts for ADB sockets and data

## Installation

### Automatic Installation
```bash
# Install SELinux policies along with Waydroid
sudo make install_selinux
```

### Manual Installation
```bash
# Navigate to the SELinux policies directory
cd /usr/share/selinux/packages/waydroid

# Build and install the policy modules
make install

# Set file contexts
sudo /usr/lib/waydroid/data/scripts/waydroid-selinux.sh setup
```

## Management

A helper script is provided for managing SELinux policies:

```bash
# Setup contexts and load policies
sudo waydroid-selinux.sh setup

# Check policy status
sudo waydroid-selinux.sh status

# View SELinux denials
sudo waydroid-selinux.sh denials

# Set permissive mode for debugging
sudo waydroid-selinux.sh permissive

# Return to enforcing mode
sudo waydroid-selinux.sh enforce

# Remove policies
sudo waydroid-selinux.sh remove
```

## Troubleshooting

### Checking SELinux Status
```bash
# Check if SELinux is enabled
getenforce

# Check loaded Waydroid policies
semodule -l | grep waydroid

# View file contexts
semanage fcontext -l | grep waydroid
```

### Debugging Denials
```bash
# View recent denials
ausearch -m avc -ts recent | grep waydroid

# Generate policy from denials
sudo waydroid-selinux.sh generate
```

### Common Issues

1. **Container fails to start**: Check SELinux denials and ensure policies are loaded
2. **Apps cannot access storage**: Verify file contexts on `/storage` directories
3. **Network issues**: Check network-related SELinux booleans
4. **Binder device access**: Ensure binder devices have correct contexts

## File Contexts

Key directories and their SELinux contexts:
- `/usr/lib/waydroid`: `waydroid_exec_t` (executables)
- `/var/lib/waydroid`: `waydroid_data_t` (data files)
- `/var/lib/lxc/waydroid0`: `waydroid_data_t` (container files)
- `~/.local/share/waydroid`: `waydroid_data_t` (user session data)
- `/dev/*binder`: `waydroid_data_t` (binder devices)

## Compatibility

These policies are designed to work with:
- SELinux in enforcing or permissive mode
- Standard SELinux policy development tools
- Both targeted and mls policy types
- RHEL/CentOS/Fedora and Debian/Ubuntu with SELinux

## Development

To modify or extend the policies:

1. Edit the `.te` files for type enforcement rules
2. Update `.fc` files for file context mappings
3. Rebuild the policies: `make clean && make`
4. Test in permissive mode first
5. Check for denials and adjust as needed

## Notes

- SELinux and AppArmor are mutually exclusive - use one or the other
- The policies are designed to be as restrictive as possible while allowing normal operation
- Custom policies can be added to handle specific use cases
- Always test policy changes in permissive mode first