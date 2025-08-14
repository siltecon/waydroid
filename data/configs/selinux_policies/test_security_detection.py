#!/usr/bin/env python3
"""
Test script for security detection functions.
Run this to verify SELinux/AppArmor detection works correctly.
"""

import sys
import os

# Add the tools directory to the path so we can import the lxc module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../tools'))

try:
    import helpers.lxc as lxc
    print("✓ Successfully imported lxc module")
except ImportError as e:
    print(f"✗ Failed to import lxc module: {e}")
    sys.exit(1)

def test_security_detection():
    """Test the security detection functions"""
    print("\n🔍 Testing Security Detection Functions")
    print("=" * 50)
    
    # Test SELinux detection
    print("\n1. Testing SELinux detection:")
    selinux_enabled = lxc.is_selinux_enabled()
    print(f"   SELinux enabled: {selinux_enabled}")
    
    # Test AppArmor detection
    print("\n2. Testing AppArmor detection:")
    apparmor_enabled = lxc.is_apparmor_enabled()
    print(f"   AppArmor enabled: {apparmor_enabled}")
    
    # Test security module selection
    print("\n3. Testing security module selection:")
    security_module = lxc.get_security_module()
    print(f"   Selected security module: {security_module}")
    
    # Test security configuration generation
    print("\n4. Testing security configuration generation:")
    security_config = lxc.generate_security_config()
    print("   Generated configuration:")
    for line in security_config:
        print(f"     {line}")
    
    print("\n✅ Security detection test completed!")

if __name__ == "__main__":
    test_security_detection()
