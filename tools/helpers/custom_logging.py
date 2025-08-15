# Custom logging levels for Waydroid
# This module adds custom logging levels to the standard logging module

import logging

def add_custom_log_levels():
    """Add custom logging levels to the logging module"""
    
    # SPAM level - Most detailed logging (value 5)
    logging.SPAM = 5
    logging.addLevelName(logging.SPAM, "SPAM")
    logging.Logger.spam = lambda inst, msg, * \
        args, **kwargs: inst.log(logging.SPAM, msg, *args, **kwargs)
    logging.spam = lambda msg, *args, **kwargs: logging.log(logging.SPAM,
                                                           msg, *args, **kwargs)
    
    # VERBOSE level - Very detailed logging (value 15)
    logging.VERBOSE = 15
    logging.addLevelName(logging.VERBOSE, "VERBOSE")
    logging.Logger.verbose = lambda inst, msg, * \
        args, **kwargs: inst.log(logging.VERBOSE, msg, *args, **kwargs)
    logging.verbose = lambda msg, *args, **kwargs: logging.log(logging.VERBOSE,
                                                             msg, *args, **kwargs)
    
    # NOTICE level - Important but not critical (value 25)
    logging.NOTICE = 25
    logging.addLevelName(logging.NOTICE, "NOTICE")
    logging.Logger.notice = lambda inst, msg, * \
        args, **kwargs: inst.log(logging.NOTICE, msg, *args, **kwargs)
    logging.notice = lambda msg, *args, **kwargs: logging.log(logging.NOTICE,
                                                            msg, *args, **kwargs)
    
    # SUCCESS level - Successful operations (value 35)
    logging.SUCCESS = 35
    logging.addLevelName(logging.SUCCESS, "SUCCESS")
    logging.Logger.success = lambda inst, msg, * \
        args, **kwargs: inst.log(logging.SUCCESS, msg, *args, **kwargs)
    logging.success = lambda msg, *args, **kwargs: logging.log(logging.SUCCESS,
                                                             msg, *args, **kwargs)
    
    # Keep backward compatibility
    logging.VERBOSE_OLD = 5
    logging.addLevelName(logging.VERBOSE_OLD, "VERBOSE_OLD")

# Add custom levels immediately when this module is imported
add_custom_log_levels()
