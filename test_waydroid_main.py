#!/usr/bin/env python3
# Test script for the updated waydroid.py main entry point

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the main waydroid module - this should patch logging first
import waydroid

def test_main_import():
    """Test that the main waydroid module imports without errors"""
    
    print("🔍 Testing Waydroid Main Import")
    print("=" * 40)
    
    # Check if custom levels exist in the logging module
    import logging
    
    if hasattr(logging, 'SPAM'):
        print(f"✅ SPAM level available: {logging.SPAM}")
    else:
        print("❌ SPAM level NOT available")
        
    if hasattr(logging, 'VERBOSE'):
        print(f"✅ VERBOSE level available: {logging.VERBOSE}")
    else:
        print("❌ VERBOSE level NOT available")
        
    if hasattr(logging, 'NOTICE'):
        print(f"✅ NOTICE level available: {logging.NOTICE}")
    else:
        print("❌ NOTICE level NOT available")
        
    if hasattr(logging, 'SUCCESS'):
        print(f"✅ SUCCESS level available: {logging.SUCCESS}")
    else:
        print("❌ SUCCESS level NOT available")
    
    # Test if functions exist
    if hasattr(logging, 'spam'):
        print("✅ logging.spam function available")
    else:
        print("❌ logging.spam function NOT available")
        
    if hasattr(logging, 'verbose'):
        print("✅ logging.verbose function available")
    else:
        print("❌ logging.verbose function NOT available")
        
    if hasattr(logging, 'notice'):
        print("✅ logging.notice function available")
    else:
        print("❌ logging.notice function NOT available")
        
    if hasattr(logging, 'success'):
        print("✅ logging.success function available")
    else:
        print("❌ logging.success function NOT available")
    
    print("\n🎯 Testing Function Calls:")
    print("-" * 25)
    
    try:
        logging.spam("This is a SPAM level message from main import")
        print("✅ logging.spam() call successful")
    except Exception as e:
        print(f"❌ logging.spam() call failed: {e}")
        
    try:
        logging.verbose("This is a VERBOSE level message from main import")
        print("✅ logging.verbose() call successful")
    except Exception as e:
        print(f"❌ logging.verbose() call failed: {e}")
        
    try:
        logging.notice("This is a NOTICE level message from main import")
        print("✅ logging.notice() call successful")
    except Exception as e:
        print(f"❌ logging.notice() call failed: {e}")
        
    try:
        logging.success("This is a SUCCESS level message from main import")
        print("✅ logging.success() call successful")
    except Exception as e:
        print(f"❌ logging.success() call failed: {e}")

if __name__ == "__main__":
    test_main_import()
