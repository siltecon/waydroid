# Copyright 2021 Oliver Smith
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import os
import sys


class log_handler(logging.StreamHandler):
    """
    Write to stdout and to the already opened log file.
    """
    _args = None

    def emit(self, record):
        try:
            msg = self.format(record)

            # INFO or higher: Write to stdout
            if (not self._args.details_to_stdout and
                not self._args.quiet and
                    record.levelno >= logging.INFO):
                stream = self.stream
                stream.write(msg)
                stream.write(self.terminator)
                self.flush()

            # Everything: Write to logfd
            msg = "(" + str(os.getpid()).zfill(6) + ") " + msg
            self._args.logfd.write(msg + "\n")
            self._args.logfd.flush()

        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException:
            self.handleError(record)


def add_verbose_log_level():
    """
    Add a new log level "verbose", which is below "debug". Also monkeypatch
    logging, so it can be used with logging.verbose().

    This function is based on work by Voitek Zylinski and sleepycal:
    https://stackoverflow.com/a/20602183
    All stackoverflow user contributions are licensed as CC-BY-SA:
    https://creativecommons.org/licenses/by-sa/3.0/
    """
    # Custom levels are now added at the main entry point
    # This function is kept for backward compatibility
    pass


def init(args):
    """
    Set log format and add the log file descriptor to args.logfd, add the
    maximum possible logging levels for ultra-detailed debugging.
    """
    # Set log file descriptor (logfd)
    if args.details_to_stdout:
        setattr(args, "logfd", sys.stdout)
    else:
        # Require containing directory to exist (so we don't create the work
        # folder and break the folder migration logic, which needs to set the
        # version upon creation)
        dir = os.path.dirname(args.log)
        if os.path.exists(dir):
            setattr(args, "logfd", open(args.log, "a+"))
            try:
                os.chmod(args.log, 0o666)
            except PermissionError:
                pass
        else:
            setattr(args, "logfd", open(os.devnull, "a+"))
            if args.action != "init":
                print("WARNING: Can't create log file in '" + dir + "', path"
                      " does not exist!")

    # Set log format with enhanced detail
    root_logger = logging.getLogger()
    root_logger.handlers = []
    
    # Enhanced formatter with more detail
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                                  datefmt="%H:%M:%S.%f")

    # Set log level with maximum granularity
    add_verbose_log_level()
    
    # Set the most detailed logging level possible
    if hasattr(args, 'ultra_verbose') and args.ultra_verbose:
        root_logger.setLevel(logging.SPAM)  # Most detailed - SPAM level
        print("🔍 ULTRA VERBOSE MODE: SPAM level logging enabled")
    elif hasattr(args, 'verbose') and args.verbose:
        root_logger.setLevel(logging.VERBOSE)  # Very detailed - VERBOSE level
        print("📝 VERBOSE MODE: Detailed logging enabled")
    else:
        root_logger.setLevel(logging.DEBUG)  # Standard debug level
        print("🐛 DEBUG MODE: Standard debug logging enabled")

    # Add a custom log handler
    handler = log_handler()
    log_handler._args = args
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    # Log the logging configuration
    if hasattr(logging, 'success'):
        logging.success("Maximum logging system initialized successfully")
    if hasattr(logging, 'spam'):
        logging.spam(f"Log levels available: SPAM({logging.SPAM}), VERBOSE({logging.VERBOSE}), NOTICE({logging.NOTICE}), SUCCESS({logging.SUCCESS}), DEBUG({logging.DEBUG})")


def disable():
    logger = logging.getLogger()
    logger.disabled = True
