# Waydroid Custom Logger
# This module provides custom logging levels and functions

import logging
import os
import sys

class WaydroidLogger:
    """Custom logger with additional logging levels for Waydroid"""
    
    def __init__(self, name="waydroid"):
        self.logger = logging.getLogger(name)
        self._setup_custom_levels()
    
    def _setup_custom_levels(self):
        """Setup custom logging levels"""
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
    
    def spam(self, msg, *args, **kwargs):
        """Log at SPAM level (most detailed)"""
        self.logger.log(logging.SPAM, msg, *args, **kwargs)
    
    def verbose(self, msg, *args, **kwargs):
        """Log at VERBOSE level (very detailed)"""
        self.logger.log(logging.VERBOSE, msg, *args, **kwargs)
    
    def notice(self, msg, *args, **kwargs):
        """Log at NOTICE level (important but not critical)"""
        self.logger.log(logging.NOTICE, msg, *args, **kwargs)
    
    def success(self, msg, *args, **kwargs):
        """Log at SUCCESS level (successful operations)"""
        self.logger.log(logging.SUCCESS, msg, *args, **kwargs)
    
    def debug(self, msg, *args, **kwargs):
        """Log at DEBUG level"""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        """Log at INFO level"""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        """Log at WARNING level"""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        """Log at ERROR level"""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        """Log at CRITICAL level"""
        self.logger.critical(msg, *args, **kwargs)
    
    def setLevel(self, level):
        """Set the logging level"""
        self.logger.setLevel(level)
    
    def addHandler(self, handler):
        """Add a handler to the logger"""
        self.logger.addHandler(handler)
    
    def removeHandler(self, handler):
        """Remove a handler from the logger"""
        self.logger.removeHandler(handler)

# Create a global instance
waydroid_logger = WaydroidLogger()

# Export the custom logging functions
spam = waydroid_logger.spam
verbose = waydroid_logger.verbose
notice = waydroid_logger.notice
success = waydroid_logger.success
debug = waydroid_logger.debug
info = waydroid_logger.info
warning = waydroid_logger.warning
error = waydroid_logger.error
critical = waydroid_logger.critical

# Export the custom levels
SPAM = logging.SPAM
VERBOSE = logging.VERBOSE
NOTICE = logging.NOTICE
SUCCESS = logging.SUCCESS
VERBOSE_OLD = logging.VERBOSE_OLD
