# Copyright 2021 Oliver Smith
# SPDX-License-Identifier: GPL-3.0-or-later
# PYTHON_ARGCOMPLETE_OK
import sys
import logging
import os
import traceback
import dbus.mainloop.glib
import dbus
import dbus.exceptions

from . import actions
from . import config
from . import helpers
from .helpers import logging as tools_logging


def main():
    def actionNeedRoot(action):
        if os.geteuid() != 0:
            raise RuntimeError(
                "Action \"{}\" needs root access".format(action))

    # Wrap everything to display nice error messages
    args = None
    try:
        logging.verbose("Waydroid main function started")
        
        # Parse arguments, set up logging
        logging.verbose("Parsing command line arguments...")
        args = helpers.arguments()
        logging.verbose(f"Action: {args.action}, Subaction: {getattr(args, 'subaction', 'N/A')}")
        
        args.cache = {}
        args.work = config.defaults["work"]
        args.config = args.work + "/waydroid.cfg"
        args.log = args.work + "/waydroid.log"
        args.sudo_timer = True
        args.timeout = 1800
        
        logging.verbose(f"Work directory: {args.work}")
        logging.verbose(f"Config file: {args.config}")
        logging.verbose(f"Log file: {args.log}")

        if os.geteuid() == 0:
            logging.verbose("Running as root user")
            if not os.path.exists(args.work):
                logging.verbose(f"Creating work directory: {args.work}")
                os.mkdir(args.work)
            else:
                logging.verbose(f"Work directory already exists: {args.work}")
        elif not os.path.exists(args.log):
            logging.verbose(f"Log directory doesn't exist, using temporary log: /tmp/tools.log")
            args.log = "/tmp/tools.log"
        else:
            logging.verbose(f"Using log file: {args.log}")

        logging.verbose("Initializing logging system...")
        tools_logging.init(args)
        logging.verbose("Logging system initialized")

        logging.verbose("Setting up DBus main loop...")
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        dbus.mainloop.glib.threads_init()
        logging.verbose("DBus main loop configured")
        dbus_name_scope = None

        logging.verbose("Checking if Waydroid is initialized...")
        is_initialized = actions.initializer.is_initialized(args)
        logging.verbose(f"Initialization status: {is_initialized}")
        
        if not is_initialized and \
                args.action and args.action not in ("init", "first-launch", "log"):
            logging.verbose("Waydroid not initialized, checking wait_for_init option...")
            if args.wait_for_init:
                logging.verbose("wait_for_init enabled, waiting for initialization...")
                try:
                    logging.verbose("Registering DBus service name for initialization wait...")
                    dbus_name_scope = dbus.service.BusName("id.waydro.Container", dbus.SystemBus(), do_not_queue=True)
                    logging.verbose("DBus service name registered, waiting for initialization...")
                    actions.wait_for_init(args)
                    logging.verbose("Initialization wait completed")
                except dbus.exceptions.NameExistsException:
                    logging.error("WayDroid service is already awaiting initialization")
                    print('ERROR: WayDroid service is already awaiting initialization')
                    return 1
            else:
                logging.error("Waydroid is not initialized, run 'waydroid init'")
                print('ERROR: WayDroid is not initialized, run "waydroid init"')
                return 0
        else:
            logging.verbose("Waydroid is initialized or action doesn't require initialization")

        # Initialize or require config
        logging.verbose("Processing action: {}".format(args.action))
        
        if args.action == "init":
            logging.verbose("Executing init action")
            actionNeedRoot(args.action)
            actions.init(args)
            logging.verbose("Init action completed")
        elif args.action == "upgrade":
            logging.verbose("Executing upgrade action")
            actionNeedRoot(args.action)
            actions.upgrade(args)
            logging.verbose("Upgrade action completed")
        elif args.action == "session":
            logging.verbose(f"Executing session action: {args.subaction}")
            if args.subaction == "start":
                logging.verbose("Starting Waydroid session...")
                actions.session_manager.start(args)
                logging.verbose("Session start completed")
            elif args.subaction == "stop":
                logging.verbose("Stopping Waydroid session...")
                actions.session_manager.stop(args)
                logging.verbose("Session stop completed")
            else:
                logging.info(
                    "Run waydroid {} -h for usage information.".format(args.action))
        elif args.action == "container":
            logging.verbose(f"Executing container action: {args.subaction}")
            actionNeedRoot(args.action)
            if args.subaction == "start":
                logging.verbose("Starting Waydroid container...")
                if dbus_name_scope is None:
                    try:
                        logging.verbose("Registering DBus service name for container...")
                        dbus_name_scope = dbus.service.BusName("id.waydro.Container", dbus.SystemBus(), do_not_queue=True)
                        logging.verbose("DBus service name registered successfully")
                    except dbus.exceptions.NameExistsException:
                        logging.error("WayDroid container service is already running")
                        print('ERROR: WayDroid container service is already running')
                        return 1
                logging.verbose("Calling container manager start...")
                actions.container_manager.start(args)
                logging.verbose("Container start completed")
            elif args.subaction == "stop":
                logging.verbose("Stopping Waydroid container...")
                actions.container_manager.stop(args)
                logging.verbose("Container stop completed")
            elif args.subaction == "restart":
                logging.verbose("Restarting Waydroid container...")
                actions.container_manager.restart(args)
                logging.verbose("Container restart completed")
            elif args.subaction == "freeze":
                logging.verbose("Freezing Waydroid container...")
                actions.container_manager.freeze(args)
                logging.verbose("Container freeze completed")
            elif args.subaction == "unfreeze":
                logging.verbose("Unfreezing Waydroid container...")
                actions.container_manager.unfreeze(args)
                logging.verbose("Container unfreeze completed")
            else:
                logging.info(
                    "Run waydroid {} -h for usage information.".format(args.action))
        elif args.action == "app":
            if args.subaction == "install":
                actions.app_manager.install(args)
            elif args.subaction == "remove":
                actions.app_manager.remove(args)
            elif args.subaction == "launch":
                actions.app_manager.launch(args)
            elif args.subaction == "intent":
                actions.app_manager.intent(args)
            elif args.subaction == "list":
                actions.app_manager.list(args)
            else:
                logging.info(
                    "Run waydroid {} -h for usage information.".format(args.action))
        elif args.action == "prop":
            if args.subaction == "get":
                actions.prop.get(args)
            elif args.subaction == "set":
                actions.prop.set(args)
            else:
                logging.info(
                    "Run waydroid {} -h for usage information.".format(args.action))
        elif args.action == "shell":
            actionNeedRoot(args.action)
            helpers.lxc.shell(args)
        elif args.action == "logcat":
            actionNeedRoot(args.action)
            helpers.lxc.logcat(args)
        elif args.action == "show-full-ui":
            actions.app_manager.showFullUI(args)
        elif args.action == "first-launch":
            actions.remote_init_client(args)
            if actions.initializer.is_initialized(args):
                actions.app_manager.showFullUI(args)
        elif args.action == "status":
            actions.status.print_status(args)
        elif args.action == "adb":
            if args.subaction == "connect":
                helpers.net.adb_connect(args)
            elif args.subaction == "disconnect":
                helpers.net.adb_disconnect(args)
            else:
                logging.info("Run waydroid {} -h for usage information.".format(args.action))
        elif args.action == "log":
            if args.clear_log:
                helpers.run.user(args, ["truncate", "-s", "0", args.log])
            try:
                helpers.run.user(
                    args, ["tail", "-n", args.lines, "-F", args.log], output="tui")
            except KeyboardInterrupt:
                pass
        else:
            logging.info("Run waydroid -h for usage information.")

        #logging.info("Done")

    except Exception as e:
        # Dump log to stdout when args (and therefore logging) init failed
        if not args:
            logging.getLogger().setLevel(logging.DEBUG)

        logging.info("ERROR: " + str(e))
        logging.info("See also: <https://github.com/waydroid>")
        logging.debug(traceback.format_exc())

        # Hints about the log file (print to stdout only)
        log_hint = "Run 'waydroid log' for details."
        if not args or not os.path.exists(args.log):
            log_hint += (" Alternatively you can use '--details-to-stdout' to"
                         " get more output, e.g. 'waydroid"
                         " --details-to-stdout init'.")
        print(log_hint)
        return 1


if __name__ == "__main__":
    sys.exit(main())
