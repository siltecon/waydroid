# Waydroid SELinux Support

This directory contains SELinux policies and configuration for Waydroid, enabling enterprise-grade security for Android containers.

## Overview

Waydroid now supports multiple security modules with automatic detection:
- **SELinux** (priority 1) - Enterprise-grade mandatory access control
- **AppArmor** (priority 2) - Linux application security
- **None** (fallback) - Unconfined mode for systems without security modules

## Security Detection

### Automatic Detection

The system automatically detects available security modules in this priority order:

1. **SELinux** - If `/sys/fs/selinux` exists and status is "enabled"
2. **AppArmor** - If `/sys/kernel/security/apparmor` exists and profiles are loaded
3. **None** - If no security modules are available

### Detection Functions

- `is_selinux_enabled()` - Checks SELinux kernel support and runtime status
- `is_apparmor_enabled()` - Checks AppArmor kernel support and profile loading
- `get_security_module()` - Returns the highest priority available security module
- `generate_security_config()` - Generates appropriate LXC configuration

### Testing

Run the test script to verify security detection:

```bash
cd data/configs/selinux_policies
python3 test_security_detection.py
```

## File Descriptions

### Policy Files

- **`waydroid.te`** - Type enforcement policy defining Waydroid-specific types and rules
- **`waydroid.if`** - Interface definitions allowing other policies to interact with Waydroid
- **`waydroid.fc`** - File context policy mapping files to SELinux types
- **`Makefile`** - Build system for compiling and installing SELinux policies

### Configuration Files

- **`config_base`** - Base LXC configuration template (no hardcoded security)
- **`config_1`** - LXC v1/v2 compatibility template (no hardcoded security)
- **`config_3`** - LXC v3+ compatibility template (no hardcoded security)
- **`config_4`** - LXC v4+ specific options

## Implementation Details

### LXC Configuration Generation

Security configuration is now generated dynamically in `config_nodes`:

```bash
# SELinux mode
lxc.selinux.context = system_u:system_r:waydroid_t:s0
lxc.selinux.allow_nesting = 1
# AppArmor disabled - using SELinux

# AppArmor mode  
lxc.apparmor.profile = unconfined
# SELinux disabled - using AppArmor

# No security mode
# No security module - running unconfined
```

### Template Updates

- Removed hardcoded `lxc.apparmor.profile = unconfined` from templates
- Added dynamic security configuration generation
- Maintained backward compatibility with all LXC versions

## Build and Installation

### Prerequisites

- SELinux development tools: `setools`, `policycoreutils-devel`
- Python 3.6+ with `selinux` module

### Building Policies

```bash
cd data/configs/selinux_policies
make all
```

### Installing Policies

```bash
make install
```

### Reloading Policies

```bash
make reload
```

## Configuration

### SELinux Context

The default SELinux context for Waydroid containers is:
```
system_u:system_r:waydroid_t:s0
```

### Nesting Support

SELinux nesting is enabled by default:
```
lxc.selinux.allow_nesting = 1
```

## Migration from AppArmor

### Automatic Migration

The system automatically detects and migrates from AppArmor to SELinux when both are available.

### Manual Migration

Use the migration script:
```bash
python3 tools/helpers/migrate_to_selinux.py
```

## Troubleshooting

### Common Issues

1. **SELinux not detected**: Check if `/sys/fs/selinux` exists and SELinux is enabled
2. **AppArmor not detected**: Check if `/sys/kernel/security/apparmor` exists and profiles are loaded
3. **Policy loading fails**: Ensure SELinux development tools are installed

### Debug Information

Enable debug logging to see security detection details:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Security Detection

Run the test script to verify detection:
```bash
python3 test_security_detection.py
```

## Security Features

### Mandatory Access Control

- **Type enforcement** - Strict control over process and file access
- **Role-based access** - Controlled privilege escalation
- **Domain isolation** - Container processes run in restricted domains

### File Contexts

- **Structured labeling** - Consistent file and directory labeling
- **Type separation** - Different SELinux types for different data categories
- **Access control** - Granular permissions based on file contexts

### Process Security

- **Domain transitions** - Controlled process privilege changes
- **Capability management** - Restricted system call access
- **Resource limits** - Controlled access to system resources

## Performance Considerations

### SELinux Overhead

- **Minimal impact** - SELinux adds <1% overhead in most cases
- **Efficient policies** - Optimized policy rules for minimal performance impact
- **Caching** - SELinux caches access decisions for performance

### Optimization

- **Policy tuning** - Remove unnecessary rules for better performance
- **Context optimization** - Minimize context transitions
- **Audit reduction** - Disable unnecessary audit logging

## Future Enhancements

### Planned Features

- **Dynamic policy loading** - Runtime policy updates without reboot
- **Policy customization** - User-defined security rules
- **Integration tools** - Better integration with system management tools

### Contributing

- **Policy improvements** - Submit SELinux policy enhancements
- **Detection logic** - Improve security module detection
- **Documentation** - Help improve this documentation

## Support

For issues with SELinux support:
1. Check the troubleshooting section
2. Run the test script to verify detection
3. Review system logs for SELinux denials
4. Submit detailed bug reports with system information

---

**Note**: This implementation provides enterprise-grade security while maintaining compatibility with existing AppArmor systems and graceful fallback for systems without security modules.