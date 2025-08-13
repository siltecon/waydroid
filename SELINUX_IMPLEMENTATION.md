# Waydroid SELinux Implementation

This document describes the complete implementation of SELinux support for Waydroid, replacing the default AppArmor-based security.

## Overview

The implementation provides a complete SELinux security framework for Waydroid containers, offering:

- **Mandatory Access Control (MAC)** - Granular security policies
- **Type Enforcement** - Strict separation between data types
- **Enhanced Auditing** - Comprehensive security event logging
- **Better Integration** - Native Linux security framework

## Architecture

### 1. SELinux Policy Files

Located in `data/configs/selinux_policies/`:

- **`waydroid.te`** - Type enforcement policy (main security rules)
- **`waydroid.if`** - Interface definitions for other policies
- **`waydroid.fc`** - File context definitions (security labeling)
- **`Makefile`** - Build and installation system

### 2. LXC Integration

- **`lxc_selinux.py`** - SELinux-aware LXC configuration helper
- **`migrate_to_selinux.py`** - Migration script from AppArmor

### 3. Security Domains

The policy defines several security domains:

```
waydroid_t          - Main Waydroid process domain
waydroid_container_t - Container management
waydroid_data_t     - Data files and directories
waydroid_config_t   - Configuration files
waydroid_log_t      - Log files
waydroid_shared_t   - Shared data
waydroid_cert_t     - Certificate files
waydroid_vpn_t      - VPN profiles
waydroid_net_t      - Network interfaces
```

## File Structure

```
data/configs/selinux_policies/
├── waydroid.te          # Type enforcement policy
├── waydroid.if          # Interface definitions
├── waydroid.fc          # File contexts
├── Makefile             # Build system
└── README.md            # Documentation

tools/helpers/
├── lxc_selinux.py       # SELinux LXC helper
└── migrate_to_selinux.py # Migration script
```

## Implementation Details

### 1. Type Enforcement Policy (`waydroid.te`)

Defines security rules for:
- **Process permissions** - What Waydroid can do
- **File access** - Which files can be read/written
- **Network access** - Network interface management
- **Container management** - LXC container operations
- **System capabilities** - Required system privileges

### 2. File Contexts (`waydroid.fc`)

Maps file paths to security contexts:
- **`/data/waydroid/*`** → `waydroid_data_t`
- **`/var/lib/waydroid/*`** → `waydroid_data_t` (symlink support)
- **`/data/shared/*`** → `waydroid_shared_t`
- **`/data/shared/certificates/*`** → `waydroid_cert_t`
- **`/data/shared/vpn/*`** → `waydroid_vpn_t`

### 3. LXC Configuration

Automatically configures LXC containers for SELinux:
```bash
lxc.selinux.context = system_u:system_r:waydroid_t:s0
lxc.selinux.allow_nesting = 1
```

## Installation

### Prerequisites

```bash
# Debian/Ubuntu
sudo apt-get install selinux-policy-dev checkpolicy

# CentOS/RHEL/Fedora
sudo yum install selinux-policy-devel checkpolicy
```

### Build and Install

```bash
cd data/configs/selinux_policies
make
sudo make install
```

### Verify Installation

```bash
sudo semodule -l | grep waydroid
sestatus
```

## Migration from AppArmor

### Automatic Migration

```bash
sudo python3 tools/helpers/migrate_to_selinux.py
```

### Manual Migration

1. **Stop AppArmor**
   ```bash
   sudo systemctl stop apparmor
   sudo systemctl disable apparmor
   sudo aa-teardown
   ```

2. **Enable SELinux**
   ```bash
   sudo setenforce 0  # Set to permissive
   sudo sed -i 's/^SELINUX=.*/SELINUX=permissive/' /etc/selinux/config
   ```

3. **Install SELinux Policy**
   ```bash
   cd data/configs/selinux_policies
   make && sudo make install
   ```

4. **Update Waydroid Config**
   ```bash
   echo "security = selinux" >> /etc/waydroid/waydroid.cfg
   ```

## Configuration

### Waydroid Configuration

Add to `/etc/waydroid/waydroid.cfg`:
```ini
security = selinux
selinux_policy = /etc/selinux/targeted/policy/waydroid.pp
```

### LXC Configuration

The system automatically adds SELinux configuration to LXC container configs.

### SELinux Mode

Initially use permissive mode for testing:
```bash
sudo setenforce 0  # Permissive
sudo setenforce 1  # Enforcing (after testing)
```

## Security Features

### 1. Process Isolation

- Waydroid processes run in `waydroid_t` domain
- Restricted access to system resources
- Controlled interaction with other processes

### 2. File Access Control

- Different security contexts for different data types
- Strict separation between Waydroid and system files
- Controlled access to shared resources

### 3. Network Security

- Isolated network interfaces
- Controlled network access
- Secure VPN and certificate handling

### 4. Container Security

- SELinux-aware LXC containers
- Nested container support
- Secure container communication

## Monitoring and Debugging

### Audit Logs

```bash
# View SELinux denials
sudo ausearch -m avc -ts recent

# Monitor specific paths
sudo auditctl -w /var/lib/waydroid -p wa -k waydroid
```

### Policy Information

```bash
# List loaded policies
sudo semodule -l

# Check file contexts
ls -Z /var/lib/waydroid/

# View SELinux status
sestatus
```

### Troubleshooting

1. **Permission Denied Errors**
   - Check file contexts: `ls -Z /path/to/file`
   - View denials: `sudo ausearch -m avc -ts recent`

2. **Policy Loading Issues**
   - Verify syntax: `checkmodule -M -m -o test.mod waydroid.te`
   - Check SELinux status: `sestatus`

3. **Container Issues**
   - Check LXC logs: `journalctl -u lxc@waydroid`
   - Verify SELinux contexts: `ls -Z /var/lib/waydroid/`

## Performance Considerations

### SELinux Overhead

- **Minimal impact** - SELinux adds negligible performance overhead
- **Efficient policies** - Optimized rules for common operations
- **Caching** - SELinux caches policy decisions

### Optimization

- **Policy tuning** - Remove unnecessary rules
- **Context optimization** - Minimize context transitions
- **Audit reduction** - Limit audit events in production

## Security Hardening

### 1. Principle of Least Privilege

- Only grant necessary permissions
- Restrict access to sensitive resources
- Minimize attack surface

### 2. Domain Separation

- Keep different data types isolated
- Prevent cross-domain access
- Secure inter-process communication

### 3. Audit and Monitoring

- Comprehensive security logging
- Regular policy review
- Incident response procedures

## Future Enhancements

### 1. Policy Modularization

- Split policy into functional modules
- Enable/disable specific features
- Custom policy extensions

### 2. Advanced Features

- Multi-level security (MLS)
- Role-based access control (RBAC)
- Container-specific policies

### 3. Integration

- Systemd integration
- Network security policies
- Hardware security module (HSM) support

## Support and Maintenance

### Policy Updates

- Regular security reviews
- Policy versioning
- Backward compatibility

### Documentation

- Comprehensive user guides
- Troubleshooting procedures
- Best practices

### Community

- Policy sharing and collaboration
- Bug reports and feature requests
- Security advisories

## Conclusion

This SELinux implementation provides Waydroid with enterprise-grade security while maintaining ease of use. The modular design allows for easy customization and extension, making it suitable for both development and production environments.

The migration tools ensure a smooth transition from AppArmor, and the comprehensive documentation supports ongoing maintenance and enhancement.
