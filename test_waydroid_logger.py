#!/usr/bin/env python3
# Test script for waydroid_logger

import sys
import os

# Add the tools/helpers directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools', 'helpers'))

# Import the waydroid_logger
import waydroid_logger

def test_waydroid_logger():
    """Test the waydroid_logger module"""
    
    print("🔍 Testing Waydroid Logger")
    print("=" * 40)
    
    # Check if custom levels exist
    if hasattr(waydroid_logger, 'SPAM'):
        print(f"✅ SPAM level available: {waydroid_logger.SPAM}")
    else:
        print("❌ SPAM level NOT available")
        
    if hasattr(waydroid_logger, 'VERBOSE'):
        print(f"✅ VERBOSE level available: {waydroid_logger.VERBOSE}")
    else:
        print("❌ VERBOSE level NOT available")
        
    if hasattr(waydroid_logger, 'NOTICE'):
        print(f"✅ NOTICE level available: {waydroid_logger.NOTICE}")
    else:
        print("❌ NOTICE level NOT available")
        
    if hasattr(waydroid_logger, 'SUCCESS'):
        print(f"✅ SUCCESS level available: {waydroid_logger.SUCCESS}")
    else:
        print("❌ SUCCESS level NOT available")
    
    # Test if functions exist
    if hasattr(waydroid_logger, 'spam'):
        print("✅ spam function available")
    else:
        print("❌ spam function NOT available")
        
    if hasattr(waydroid_logger, 'verbose'):
        print("✅ verbose function available")
    else:
        print("❌ verbose function NOT available")
        
    if hasattr(waydroid_logger, 'notice'):
        print("✅ notice function available")
    else:
        print("❌ notice function NOT available")
        
    if hasattr(waydroid_logger, 'success'):
        print("✅ success function available")
    else:
        print("❌ success function NOT available")
    
    print("\n🎯 Testing Function Calls:")
    print("-" * 25)
    
    try:
        waydroid_logger.spam("This is a SPAM level message")
        print("✅ spam() call successful")
    except Exception as e:
        print(f"❌ spam() call failed: {e}")
        
    try:
        waydroid_logger.verbose("This is a VERBOSE level message")
        print("✅ verbose() call successful")
    except Exception as e:
        print(f"❌ verbose() call failed: {e}")
        
    try:
        waydroid_logger.notice("This is a NOTICE level message")
        print("✅ notice() call successful")
    except Exception as e:
        print(f"❌ notice() call failed: {e}")
        
    try:
        waydroid_logger.success("This is a SUCCESS level message")
        print("✅ success() call successful")
    except Exception as e:
        print(f"❌ success() call failed: {e}")

if __name__ == "__main__":
    test_waydroid_logger()
