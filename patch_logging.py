#!/usr/bin/env python3
# Patch the logging module to add custom levels
# This script should be run before importing any other modules

import logging

def patch_logging():
    """Add custom logging levels to the logging module"""
    
    # SPAM level - Most detailed logging (value 5)
    logging.SPAM = 5
    logging.addLevelName(logging.SPAM, "SPAM")
    
    # VERBOSE level - Very detailed logging (value 15)
    logging.VERBOSE = 15
    logging.addLevelName(logging.VERBOSE, "VERBOSE")
    
    # NOTICE level - Important but not critical (value 25)
    logging.NOTICE = 25
    logging.addLevelName(logging.NOTICE, "NOTICE")
    
    # SUCCESS level - Successful operations (value 35)
    logging.SUCCESS = 35
    logging.addLevelName(logging.SUCCESS, "SUCCESS")
    
    # Keep backward compatibility
    logging.VERBOSE_OLD = 5
    logging.addLevelName(logging.VERBOSE_OLD, "VERBOSE_OLD")
    
    # Add custom logging functions to the logging module
    def spam(msg, *args, **kwargs):
        """Log at SPAM level (most detailed)"""
        logging.log(logging.SPAM, msg, *args, **kwargs)
    
    def verbose(msg, *args, **kwargs):
        """Log at VERBOSE level (very detailed)"""
        logging.log(logging.VERBOSE, msg, *args, **kwargs)
    
    def notice(msg, *args, **kwargs):
        """Log at NOTICE level (important but not critical)"""
        logging.log(logging.NOTICE, msg, *args, **kwargs)
    
    def success(msg, *args, **kwargs):
        """Log at SUCCESS level (successful operations)"""
        logging.log(logging.SUCCESS, msg, *args, **kwargs)
    
    # Add these functions to the logging module
    logging.spam = spam
    logging.verbose = verbose
    logging.notice = notice
    logging.success = success
    
    # Also add them to the Logger class
    logging.Logger.spam = lambda inst, msg, *args, **kwargs: inst.log(logging.SPAM, msg, *args, **kwargs)
    logging.Logger.verbose = lambda inst, msg, *args, **kwargs: inst.log(logging.VERBOSE, msg, *args, **kwargs)
    logging.Logger.notice = lambda inst, msg, *args, **kwargs: inst.log(logging.NOTICE, msg, *args, **kwargs)
    logging.Logger.success = lambda inst, msg, *args, **kwargs: inst.log(logging.SUCCESS, msg, *args, **kwargs)
    
    print("✅ Logging module patched successfully!")
    print(f"🔍 Custom levels: SPAM({logging.SPAM}), VERBOSE({logging.VERBOSE}), NOTICE({logging.NOTICE}), SUCCESS({logging.SUCCESS})")

if __name__ == "__main__":
    patch_logging()
