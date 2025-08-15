# Modular Waydroid Container Manager

This directory now contains a modular version of Waydroid that allows you to run each step of the container startup process individually. This is designed to help with debugging, customization, and creating specialized versions for specific use cases.

## 🚀 New Tools Available

### 1. **waydroid-modular.py** - Step-by-Step Container Management
Allows you to run each startup step individually:

```bash
# Run individual steps
waydroid-modular.py step1                    # Environment setup only
waydroid-modular.py step2                    # Container preparation only  
waydroid-modular.py step3                    # Container start only
waydroid-modular.py step4                    # Hardware services only

# Run all steps
waydroid-modular.py all                      # Complete startup

# Run all steps except hardware services
waydroid-modular.py all --skip-hardware      # Skip problematic step

# Status and diagnostics
waydroid-modular.py status                   # Show step status
waydroid-modular.py diagnose                 # Diagnose failures
waydroid-modular.py reset                    # Reset step results
```

### 2. **waydroid-simplified.py** - Simplified Container Manager
A simplified version that skips the hardware manager entirely:

```bash
# Basic container operations (no hardware manager)
waydroid-simplified.py start                 # Start container
waydroid-simplified.py stop                  # Stop container
waydroid-simplified.py restart               # Restart container
waydroid-simplified.py status                # Check status
waydroid-simplified.py freeze                # Freeze container
waydroid-simplified.py unfreeze              # Unfreeze container

# With session management
waydroid-simplified.py start --session       # Start with session
```

## 🔧 What Each Step Does

### **Step 1: Environment Setup**
- Load binder and ashmem drivers
- Set device permissions for `/dev/binder*`
- Create necessary directories
- Validate Android images

### **Step 2: Container Preparation**
- Setup basic networking bridge
- Generate LXC configuration
- Mount Android rootfs
- Set protocol version

### **Step 3: Container Start**
- Start LXC container
- Wait for Android boot
- Verify container status

### **Step 4: Hardware Services (Optional)**
- Start hardware manager
- Initialize Binder services
- Setup hardware interfaces
- Enable Android hardware control

## 🎯 Use Cases

### **For Debugging:**
```bash
# Test each step individually to find where it fails
waydroid-modular.py step1 --verbose
waydroid-modular.py step2 --verbose
waydroid-modular.py step3 --verbose
```

### **For Simplified Operation:**
```bash
# Skip hardware manager entirely
waydroid-simplified.py start
```

### **For Development:**
```bash
# Run core functionality without complex features
waydroid-modular.py all --skip-hardware
```

## ⚠️ Important Notes

### **Hardware Manager Issues:**
- The original hardware manager can hang during startup
- Step 4 is optional and can be skipped
- Simplified version runs without hardware manager

### **Dependencies:**
- Steps must be run in order (1 → 2 → 3 → 4)
- Each step depends on the previous step's success
- Hardware services (Step 4) are completely optional

### **Configuration:**
- Uses standard Waydroid configuration files
- Default config path: `/etc/waydroid/waydroid.conf`
- Can specify custom config with `--config` option

## 🔍 Troubleshooting

### **Check Step Status:**
```bash
waydroid-modular.py status
```

### **Diagnose Failures:**
```bash
waydroid-modular.py diagnose
```

### **Reset and Start Over:**
```bash
waydroid-modular.py reset
waydroid-modular.py step1
```

### **Verbose Logging:**
```bash
waydroid-modular.py step1 --verbose
waydroid-simplified.py start --verbose
```

## 📁 File Structure

```
tmp/waydroid-main/
├── tools/actions/
│   ├── modular_container_manager.py      # Modular step-by-step manager
│   ├── simplified_container_manager.py   # Simplified version (no hardware)
│   └── container_manager.py              # Original (modified to support modular)
├── waydroid-modular.py                   # Modular CLI interface
├── waydroid-simplified.py                # Simplified CLI interface
└── MODULAR_README.md                     # This file
```

## 🚀 Getting Started

### **1. Test Individual Steps:**
```bash
cd tmp/waydroid-main
./waydroid-modular.py step1 --verbose
./waydroid-modular.py step2 --verbose
./waydroid-modular.py step3 --verbose
```

### **2. Run Simplified Version:**
```bash
./waydroid-simplified.py start --verbose
```

### **3. Check Status:**
```bash
./waydroid-modular.py status
./waydroid-simplified.py status
```

## 🎯 Benefits

- **Debugging**: Isolate failures to specific steps
- **Customization**: Skip problematic components
- **Development**: Test individual components
- **Reliability**: Avoid hardware manager hangs
- **Flexibility**: Choose which features to enable

## 🔧 Integration with Original Waydroid

The modular system is designed to work alongside the original Waydroid:

- **Original commands still work** (with hardware manager disabled)
- **New modular commands** provide step-by-step control
- **Simplified version** offers reliable alternative
- **Backward compatibility** maintained

This modular approach gives you complete control over the Waydroid startup process while maintaining compatibility with existing systems.
