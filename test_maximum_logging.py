#!/usr/bin/env python3
# Test script to demonstrate maximum logging levels

import sys
import os

# Add the tools directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from tools.helpers import logging

def test_maximum_logging():
    """Test all available logging levels"""
    
    # Create a mock args object
    class MockArgs:
        def __init__(self):
            self.work = "/tmp/test"
            self.log = "/tmp/test.log"
            self.details_to_stdout = True
            self.verbose = True
            self.ultra_verbose = True
            self.quiet = False
    
    args = MockArgs()
    
    print("🔍 Testing Maximum Logging Levels")
    print("=" * 50)
    
    # Initialize logging with maximum detail
    logging.init(args)
    
    print("\n📝 Testing All Logging Levels:")
    print("-" * 30)
    
    # Test SPAM level (most detailed)
    logging.spam("This is SPAM level - the most detailed logging possible")
    logging.spam("SPAM level shows every tiny detail for debugging")
    
    # Test VERBOSE level
    logging.verbose("This is VERBOSE level - very detailed logging")
    logging.verbose("VERBOSE level shows detailed operation information")
    
    # Test NOTICE level
    logging.notice("This is NOTICE level - important but not critical")
    logging.notice("NOTICE level for significant but non-error events")
    
    # Test SUCCESS level
    logging.success("This is SUCCESS level - successful operations")
    logging.success("SUCCESS level for completed operations")
    
    # Test DEBUG level
    logging.debug("This is DEBUG level - standard debug information")
    logging.debug("DEBUG level for general debugging information")
    
    # Test INFO level
    logging.info("This is INFO level - general information")
    logging.info("INFO level for general application information")
    
    # Test WARNING level
    logging.warning("This is WARNING level - potential issues")
    logging.warning("WARNING level for concerning but non-fatal issues")
    
    # Test ERROR level
    logging.error("This is ERROR level - error conditions")
    logging.error("ERROR level for error conditions that need attention")
    
    # Test CRITICAL level
    logging.critical("This is CRITICAL level - critical errors")
    logging.critical("CRITICAL level for severe errors that may cause failure")
    
    print("\n✅ Maximum logging test completed!")
    print(f"🔍 Log levels available: SPAM({logging.SPAM}), VERBOSE({logging.VERBOSE}), NOTICE({logging.NOTICE}), SUCCESS({logging.SUCCESS})")
    print(f"🐛 Standard levels: DEBUG({logging.DEBUG}), INFO({logging.INFO}), WARNING({logging.WARNING}), ERROR({logging.ERROR}), CRITICAL({logging.CRITICAL})")

if __name__ == "__main__":
    test_maximum_logging()
