#!/usr/bin/env python3
# Simple test for direct logging patch

import sys
import os

# Add the tools/helpers directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools', 'helpers'))

# Import the logging module - this should have the custom levels
import logging

def test_simple_logging():
    """Test if custom logging levels are available"""
    
    print("🔍 Testing Simple Logging Patch")
    print("=" * 40)
    
    # Check if custom levels exist
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
        logging.spam("This is a SPAM level message")
        print("✅ logging.spam() call successful")
    except Exception as e:
        print(f"❌ logging.spam() call failed: {e}")
        
    try:
        logging.verbose("This is a VERBOSE level message")
        print("✅ logging.verbose() call successful")
    except Exception as e:
        print(f"❌ logging.verbose() call failed: {e}")
        
    try:
        logging.notice("This is a NOTICE level message")
        print("✅ logging.notice() call successful")
    except Exception as e:
        print(f"❌ logging.notice() call failed: {e}")
        
    try:
        logging.success("This is a SUCCESS level message")
        print("✅ logging.success() call successful")
    except Exception as e:
        print(f"❌ logging.success() call failed: {e}")

if __name__ == "__main__":
    test_simple_logging()
