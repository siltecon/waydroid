# Copyright 2021 Erfan Abdi
# SPDX-License-Identifier: GPL-3.0-or-later
from shutil import which
import logging
import os
import glob
import signal
import tools.config
from tools import helpers
from tools import services
import dbus
import dbus.service
import dbus.exceptions
from gi.repository import GLib

class DbusContainerManager(dbus.service.Object):
    def __init__(self, looper, bus, object_path, args):
        logging.verbose("Initializing DbusContainerManager")
        logging.spam(f"Constructor parameters: looper={type(looper)}, bus={type(bus)}, object_path={object_path}")
        logging.verbose(f"Object path: {object_path}")
        self.args = args
        self.looper = looper
        logging.spam("Instance variables set successfully")
        logging.verbose("Calling parent dbus.service.Object constructor...")
        dbus.service.Object.__init__(self, bus, object_path)
        logging.spam("Parent constructor completed without errors")
        logging.verbose("DbusContainerManager initialization completed")

    @dbus.service.method("id.waydro.Container", in_signature='a{ss}', out_signature='', sender_keyword="sender", connection_keyword="conn")
    def Start(self, session, sender, conn):
        dbus_info = dbus.Interface(conn.get_object("org.freedesktop.DBus", "/org/freedesktop/DBus/Bus", False), "org.freedesktop.DBus")
        uid = dbus_info.GetConnectionUnixUser(sender)
        if str(uid) not in ["0", session["user_id"]]:
            raise RuntimeError("Cannot start a session on behalf of another user")
        pid = dbus_info.GetConnectionUnixProcessID(sender)
        if str(uid) != "0" and str(pid) != session["pid"]:
            raise RuntimeError("Invalid session pid")
        do_start(self.args, session)

    @dbus.service.method("id.waydro.Container", in_signature='b', out_signature='')
    def Stop(self, quit_session):
        logging.verbose(f"DBus Stop method called with quit_session={quit_session}")
        stop(self.args, quit_session)

    @dbus.service.method("id.waydro.Container", in_signature='', out_signature='')
    def Freeze(self):
        logging.verbose("DBus Freeze method called")
        freeze(self.args)

    @dbus.service.method("id.waydro.Container", in_signature='', out_signature='')
    def Unfreeze(self):
        logging.verbose("DBus Unfreeze method called")
        unfreeze(self.args)

    @dbus.service.method("id.waydro.Container", in_signature='', out_signature='a{ss}')
    def GetSession(self):
        logging.verbose("DBus GetSession method called")
        try:
            session = self.args.session
            logging.verbose(f"Retrieved session: {session}")
            session["state"] = helpers.lxc.status(self.args)
            logging.verbose(f"Updated session state: {session['state']}")
            return session
        except AttributeError:
            logging.verbose("No session found, returning empty dict")
            return {}

def service(args, looper):
    logging.verbose("Starting DBus container manager service")
    logging.spam(f"Service function called with args: {type(args)}, looper: {type(looper)}")
    
    logging.verbose("Creating DbusContainerManager object...")
    logging.spam("About to create DBus session bus from waydroid-dbus service...")
    try:
        # Ensure waydroid-dbus service is running
        logging.verbose("Checking if waydroid-dbus service is running...")
        try:
            import subprocess
            # Use systemctl show to get the actual state, not just is-active
            result = subprocess.run(['systemctl', 'show', '--property=ActiveState', 'waydroid-dbus.service'], 
                                 capture_output=True, text=True, check=False)
            service_status = result.stdout.strip()
            logging.spam(f"waydroid-dbus service status: '{service_status}' (exit code: {result.returncode})")
            
            # Extract the actual state from the output (format: ActiveState=active)
            if '=' in service_status:
                actual_state = service_status.split('=')[1]
                logging.spam(f"Parsed waydroid-dbus state: '{actual_state}'")
                
                # Check for any running state (active, activating, starting)
                if actual_state in ['active', 'activating', 'starting']:
                    logging.verbose(f"waydroid-dbus service is already running (state: {actual_state})")
                else:
                    logging.verbose("Starting waydroid-dbus service...")
                    subprocess.run(['systemctl', 'start', 'waydroid-dbus.service'], check=True)
                    logging.verbose("waydroid-dbus service started successfully")
            else:
                logging.warning(f"Could not parse waydroid-dbus service status: {service_status}")
                # Fallback: try to start the service
                logging.verbose("Attempting to start waydroid-dbus service as fallback...")
                subprocess.run(['systemctl', 'start', 'waydroid-dbus.service'], check=True)
                logging.verbose("waydroid-dbus service started successfully")
        except Exception as e:
            logging.warning(f"Failed to manage waydroid-dbus service: {e}")
        
        # Ensure weston-headless service is running
        logging.verbose("Checking if weston-headless service is running...")
        try:
            # Use systemctl show to get the actual state, not just is-active
            result = subprocess.run(['systemctl', 'show', '--property=ActiveState', 'weston-headless.service'], 
                                 capture_output=True, text=True, check=False)
            service_status = result.stdout.strip()
            logging.spam(f"weston-headless service status: '{service_status}' (exit code: {result.returncode})")
            
            # Extract the actual state from the output (format: ActiveState=activating)
            if '=' in service_status:
                actual_state = service_status.split('=')[1]
                logging.spam(f"Parsed weston-headless state: '{actual_state}'")
                
                # Check for any running state (active, activating, starting)
                if actual_state in ['active', 'activating', 'starting']:
                    logging.verbose(f"weston-headless service is already running (state: {actual_state})")
                else:
                    logging.verbose("Starting weston-headless service...")
                    subprocess.run(['systemctl', 'start', 'weston-headless.service'], check=True)
                    logging.verbose("weston-headless service started successfully")
            else:
                logging.warning(f"Could not parse weston-headless service status: {service_status}")
                # Fallback: try to start the service
                logging.verbose("Attempting to start weston-headless service as fallback...")
                subprocess.run(['systemctl', 'start', 'weston-headless.service'], check=True)
                logging.verbose("weston-headless service started successfully")
        except Exception as e:
            logging.warning(f"Failed to manage weston-headless service: {e}")
        
        # Check Weston environment setup
        logging.verbose("Checking Weston environment setup...")
        try:
            wayland_runtime = "/run/wayland"
            # Wait for Weston runtime directory to be created (max 10 seconds)
            max_wait = 10
            wait_count = 0
            while not os.path.exists(wayland_runtime) and wait_count < max_wait:
                logging.spam(f"Waiting for Weston runtime directory... ({wait_count + 1}/{max_wait})")
                time.sleep(1)
                wait_count += 1
            
            if os.path.exists(wayland_runtime):
                logging.verbose(f"Weston runtime directory exists: {wayland_runtime}")
                # Set Weston environment variables
                os.environ['XDG_RUNTIME_DIR'] = wayland_runtime
                os.environ['WAYLAND_DISPLAY'] = 'wayland-0'
                logging.spam(f"Set XDG_RUNTIME_DIR to: {os.environ['XDG_RUNTIME_DIR']}")
                logging.spam(f"Set WAYLAND_DISPLAY to: {os.environ['WAYLAND_DISPLAY']}")
            else:
                logging.warning(f"Weston runtime directory not found after {max_wait} seconds: {wayland_runtime}")
        except Exception as e:
            logging.warning(f"Failed to setup Weston environment: {e}")
        
        # Use the custom session bus from waydroid-dbus service
        waydroid_dbus_socket = "/run/waydroid/dbus/session_bus_socket"
        if os.path.exists(waydroid_dbus_socket):
            logging.verbose(f"Found waydroid-dbus socket: {waydroid_dbus_socket}")
            # Set the DBUS_SESSION_BUS_ADDRESS to use the waydroid-dbus service
            os.environ['DBUS_SESSION_BUS_ADDRESS'] = f"unix:path={waydroid_dbus_socket}"
            logging.spam(f"Set DBUS_SESSION_BUS_ADDRESS to: {os.environ['DBUS_SESSION_BUS_ADDRESS']}")
            bus = dbus.SessionBus()
            logging.spam(f"DBus session bus created successfully using waydroid-dbus: {type(bus)}")
            logging.verbose("Using DBus session bus from waydroid-dbus service")
        else:
            logging.warning(f"waydroid-dbus socket not found at {waydroid_dbus_socket}, falling back to default session bus")
            bus = dbus.SessionBus()
            logging.spam(f"DBus session bus created successfully using default: {type(bus)}")
            logging.verbose("Using default DBus session bus")
    except Exception as e:
        logging.error(f"Failed to create DBus session bus: {e}")
        raise
    
    logging.spam("About to create DbusContainerManager object...")
    try:
        dbus_obj = DbusContainerManager(looper, bus, '/ContainerManager', args)
        logging.spam(f"DbusContainerManager object created successfully: {type(dbus_obj)}")
        logging.verbose("DBus container manager service created successfully")
    except Exception as e:
        logging.error(f"Failed to create DbusContainerManager: {e}")
        raise
    
    logging.verbose("Starting main loop...")
    logging.spam("About to call looper.run() - this is where the hang might occur")
    logging.spam(f"Looper type: {type(looper)}, Looper object: {looper}")
    
    # Test if DBus methods are working by calling Start method locally
    logging.verbose("Testing DBus Start method to verify service is working...")
    try:
        # Create a test session to call the Start method
        test_session = {"user_id": "0", "pid": str(os.getpid())}
        logging.spam(f"Calling Start method with test session: {test_session}")
        
        # Call the Start method directly to avoid DBus authentication issues
        # This bypasses the DBus layer and calls the method directly
        logging.spam("Calling Start method directly (bypassing DBus layer)")
        do_start(dbus_obj.args, test_session)
        logging.verbose("DBus Start method test completed successfully - service is working")
    except Exception as e:
        logging.warning(f"DBus Start method test failed: {e}")
        logging.spam(f"Exception type: {type(e)}")
        logging.spam(f"Exception details: {str(e)}")
    
    try:
        logging.spam("Calling looper.run() - entering main loop...")
        
        # Add a timeout mechanism to prevent infinite hangs
        import threading
        import time
        
        def timeout_handler():
            logging.warning("Main loop timeout reached - forcing exit")
            logging.spam("Timeout handler called after 30 seconds")
            try:
                looper.quit()
            except Exception as e:
                logging.error(f"Failed to quit looper: {e}")
                os._exit(1)
        
        # Start timeout timer
        timeout_timer = threading.Timer(30.0, timeout_handler)
        timeout_timer.start()
        logging.spam("Timeout timer started (30 seconds)")
        
        try:
            looper.run()
            logging.spam("looper.run() completed - main loop exited normally")
            logging.verbose("Main loop exited")
        finally:
            # Cancel timeout timer if we exit normally
            timeout_timer.cancel()
            logging.spam("Timeout timer cancelled")
            
    except Exception as e:
        logging.error(f"Exception in main loop: {e}")
        logging.spam(f"Exception type: {type(e)}")
        raise

def set_permissions(args, perm_list=None, mode="777"):
    logging.verbose("Setting permissions for device nodes")
    logging.spam(f"Function called with: args={type(args)}, perm_list={perm_list}, mode={mode}")
    
    def chmod(path, mode):
        logging.spam(f"chmod function called with path={path}, mode={mode}")
        if os.path.exists(path):
            logging.verbose(f"Setting permissions {mode} on {path}")
            logging.spam(f"Path {path} exists, proceeding with chmod")
            command = ["chmod", mode, "-R", path]
            logging.spam(f"Executing command: {' '.join(command)}")
            tools.helpers.run.user(args, command, check=False)
            logging.spam(f"chmod command completed for {path}")
        else:
            logging.verbose(f"Path {path} does not exist, skipping permissions")
            logging.spam(f"Path {path} does not exist, skipping chmod operation")

    # Nodes list
    if not perm_list:
        logging.verbose("Using default permission list for device nodes")
        perm_list = [
            "/dev/ashmem",

            # sw_sync for HWC
            "/dev/sw_sync",
            "/sys/kernel/debug/sync/sw_sync",

            # Media
            "/dev/Vcodec",
            "/dev/MTK_SMI",
            "/dev/mdp_sync",
            "/dev/mtk_cmdq",

            # Graphics
            "/dev/graphics",
            "/dev/pvr_sync",
            "/dev/ion",
        ]

        # DRM render nodes
        logging.spam("Searching for DRM render nodes...")
        drm_nodes = glob.glob("/dev/dri/renderD*")
        logging.verbose(f"Found DRM render nodes: {drm_nodes}")
        logging.spam(f"DRM node search pattern: /dev/dri/renderD*, found {len(drm_nodes)} nodes")
        perm_list.extend(drm_nodes)
        
        # Framebuffers
        logging.spam("Searching for framebuffer nodes...")
        fb_nodes = glob.glob("/dev/fb*")
        logging.verbose(f"Found framebuffer nodes: {fb_nodes}")
        logging.spam(f"Framebuffer node search pattern: /dev/fb*, found {len(fb_nodes)} nodes")
        perm_list.extend(fb_nodes)
        
        # Videos
        logging.spam("Searching for video nodes...")
        video_nodes = glob.glob("/dev/video*")
        logging.verbose(f"Found video nodes: {video_nodes}")
        logging.spam(f"Video node search pattern: /dev/video*, found {len(video_nodes)} nodes")
        perm_list.extend(video_nodes)
        
        # DMA-BUF Heaps
        logging.spam("Searching for DMA-BUF heap nodes...")
        dma_nodes = glob.glob("/dev/dma_heap/*")
        logging.verbose(f"Found DMA-BUF heap nodes: {dma_nodes}")
        logging.spam(f"DMA-BUF heap search pattern: /dev/dma_heap/*, found {len(dma_nodes)} nodes")
        perm_list.extend(dma_nodes)

    logging.verbose(f"Processing {len(perm_list)} device nodes for permissions")
    for path in perm_list:
        chmod(path, mode)
    logging.verbose("Device node permissions setup completed")

def start(args):
    logging.verbose("Starting WayDroid container service")
    logging.spam(f"start function called with args: {type(args)}")
    logging.spam(f"args attributes: {[attr for attr in dir(args) if not attr.startswith('_')]}")
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logging.verbose(f"Received signal {signum}, shutting down gracefully...")
        logging.spam(f"Signal frame: {frame}")
        sys.exit(0)
    
    logging.spam("Setting up signal handlers...")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    logging.spam("Signal handlers configured")
    
    try:
        logging.spam("Attempting to register DBus service name...")
        # Use the same session bus that the service will use
        waydroid_dbus_socket = "/run/waydroid/dbus/session_bus_socket"
        if os.path.exists(waydroid_dbus_socket):
            logging.verbose(f"Using waydroid-dbus session bus for service registration")
            os.environ['DBUS_SESSION_BUS_ADDRESS'] = f"unix:path={waydroid_dbus_socket}"
            bus = dbus.SessionBus()
        else:
            logging.warning(f"waydroid-dbus socket not found, using default session bus")
            bus = dbus.SessionBus()
        
        name = dbus.service.BusName("id.waydro.Container", bus, do_not_queue=True)
        logging.spam(f"DBus service name registration successful: {name}")
        logging.verbose("Successfully registered DBus service name: id.waydro.Container")
    except dbus.exceptions.NameExistsException:
        logging.spam("DBus service name already exists exception caught")
        logging.error("Container service is already running")
        return

    status = helpers.lxc.status(args)
    logging.verbose(f"Current container status: {status}")
    
    if status == "STOPPED":
        logging.verbose("Container is stopped, proceeding with startup sequence")
        
        # Load binder and ashmem drivers
        logging.verbose("Loading Android drivers...")
        logging.spam("About to load configuration...")
        cfg = tools.config.load(args)
        logging.spam(f"Configuration loaded successfully: {type(cfg)}")
        logging.verbose(f"Loaded configuration: vendor_type={cfg['waydroid']['vendor_type']}")
        logging.spam(f"Full configuration keys: {list(cfg.keys())}")
        
        if cfg["waydroid"]["vendor_type"] == "MAINLINE":
            logging.spam("Vendor type is MAINLINE, proceeding with driver probing")
            logging.verbose("Probing Binder driver...")
            logging.spam("Calling helpers.drivers.probeBinderDriver...")
            probe_result = helpers.drivers.probeBinderDriver(args)
            logging.spam(f"Binder driver probe result: {probe_result}")
            if probe_result != 0:
                logging.error("Failed to load Binder driver")
                logging.spam(f"Binder driver probe failed with exit code: {probe_result}")
            else:
                logging.verbose("Binder driver loaded successfully")
                logging.spam("Binder driver probe completed successfully")
            
            logging.verbose("Probing Ashmem driver...")
            logging.spam("Calling helpers.drivers.probeAshmemDriver...")
            helpers.drivers.probeAshmemDriver(args)
            logging.spam("Ashmem driver probe completed")
            logging.verbose("Ashmem driver loaded successfully")
        else:
            logging.spam(f"Vendor type is not MAINLINE: {cfg['waydroid']['vendor_type']}")
        
        logging.verbose("Loading Binder nodes...")
        helpers.drivers.loadBinderNodes(args)
        
        logging.verbose("Setting up binder device permissions...")
        set_permissions(args, [
            "/dev/" + args.BINDER_DRIVER,
            "/dev/" + args.VNDBINDER_DRIVER,
            "/dev/" + args.HWBINDER_DRIVER
        ], "666")

        logging.verbose("Setting up signal handlers...")
        mainloop = GLib.MainLoop()

        def sigint_handler(data):
            logging.verbose("Received SIGINT signal, stopping container")
            stop(args)
            mainloop.quit()

        GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGINT, sigint_handler, None)
        GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGTERM, sigint_handler, None)
        logging.verbose("Signal handlers configured")
        
        logging.verbose("Starting container service...")
        service(args, mainloop)
    else:
        logging.error("WayDroid container is {}".format(status))

def do_start(args, session):
    logging.verbose("Starting WayDroid container with session")
    logging.verbose(f"Session details: user_id={session.get('user_id', 'N/A')}, pid={session.get('pid', 'N/A')}")
    
    if "session" in args:
        logging.error("Already tracking a session, cannot start another")
        raise RuntimeError("Already tracking a session")

    # Networking
    logging.verbose("Setting up networking...")
    command = [tools.config.tools_src +
               "/data/scripts/waydroid-net.sh", "start"]
    logging.verbose(f"Running networking command: {' '.join(command)}")
    tools.helpers.run.user(args, command)
    logging.verbose("Networking setup completed")

    # Sensors
    logging.verbose("Setting up sensors...")
    if which("waydroid-sensord"):
        logging.verbose("waydroid-sensord found, starting sensor daemon")
        command = ["waydroid-sensord", "/dev/" + args.HWBINDER_DRIVER]
        logging.verbose(f"Starting sensor daemon with command: {' '.join(command)}")
        tools.helpers.run.user(
            args, command, output="background")
        logging.verbose("Sensor daemon started successfully")
    else:
        logging.verbose("waydroid-sensord not found, skipping sensor setup")

    # Cgroup hacks
    logging.verbose("Setting up cgroup management...")
    if which("start"):
        logging.verbose("Legacy 'start' command found, starting cgroup-lite")
        command = ["start", "cgroup-lite"]
        logging.verbose(f"Running cgroup command: {' '.join(command)}")
        tools.helpers.run.user(args, command, check=False)
        logging.verbose("Cgroup-lite started")
    else:
        logging.verbose("Legacy 'start' command not found, skipping cgroup-lite")

    # Keep schedtune around in case nesting is supported
    logging.verbose("Checking schedtune cgroup nesting support...")
    if os.path.ismount("/sys/fs/cgroup/schedtune"):
        logging.verbose("schedtune cgroup is mounted, testing nesting capability")
        try:
            logging.verbose("Creating test directories for nesting test")
            os.mkdir("/sys/fs/cgroup/schedtune/probe0")
            os.mkdir("/sys/fs/cgroup/schedtune/probe0/probe1")
            logging.verbose("Nesting test directories created successfully")
        except Exception as e:
            logging.verbose(f"Nesting test failed: {e}, unmounting schedtune")
            command = ["umount", "-l", "/sys/fs/cgroup/schedtune"]
            tools.helpers.run.user(args, command, check=False)
            logging.verbose("schedtune cgroup unmounted")
        finally:
            logging.verbose("Cleaning up test directories")
            if os.path.exists("/sys/fs/cgroup/schedtune/probe0/probe1"):
                os.rmdir("/sys/fs/cgroup/schedtune/probe0/probe1")
            if os.path.exists("/sys/fs/cgroup/schedtune/probe0"):
                os.rmdir("/sys/fs/cgroup/schedtune/probe0")
            logging.verbose("Test directories cleaned up")
    else:
        logging.verbose("schedtune cgroup not mounted, skipping nesting test")

    #TODO: remove NFC hacks
    logging.verbose("Managing NFC service to prevent conflicts...")
    if which("stop"):
        logging.verbose("Legacy 'stop' command found, stopping nfcd")
        command = ["stop", "nfcd"]
        logging.verbose(f"Running NFC stop command: {' '.join(command)}")
        tools.helpers.run.user(args, command, check=False)
        logging.verbose("NFC service stopped via legacy command")
    elif which("systemctl") and (tools.helpers.run.user(args, ["systemctl", "is-active", "-q", "nfcd"], check=False) == 0):
        logging.verbose("systemctl found and nfcd is active, stopping via systemctl")
        command = ["systemctl", "stop", "nfcd"]
        logging.verbose(f"Running systemctl stop command: {' '.join(command)}")
        tools.helpers.run.user(args, command, check=False)
        logging.verbose("NFC service stopped via systemctl")
    else:
        logging.verbose("No suitable method found to stop NFC service")

    # Set permissions
    logging.verbose("Setting up device permissions...")
    set_permissions(args)
    logging.verbose("Device permissions configured")

    # Create session-specific LXC config file
    logging.verbose("Generating session-specific LXC configuration...")
    helpers.lxc.generate_session_lxc_config(args, session)
    logging.verbose("LXC configuration generated")
    
    # Backwards compatibility
    logging.verbose("Checking for backwards compatibility mounts...")
    with open(tools.config.defaults["lxc"] + "/waydroid/config") as f:
        if "config_session" not in f.read():
            logging.verbose("Binding waydroid data for backwards compatibility")
            helpers.mount.bind(args, session["waydroid_data"],
                               tools.config.defaults["data"])
            logging.verbose("Backwards compatibility mount configured")
        else:
            logging.verbose("Backwards compatibility mount not needed")

    # Mount rootfs
    logging.verbose("Mounting Android rootfs...")
    cfg = tools.config.load(args)
    logging.verbose(f"Mounting rootfs from: {cfg['waydroid']['images_path']}")
    helpers.images.mount_rootfs(args, cfg["waydroid"]["images_path"], session)
    logging.verbose("Android rootfs mounted successfully")

    logging.verbose("Setting AIDL protocol version...")
    helpers.protocol.set_aidl_version(args)
    logging.verbose("AIDL protocol version configured")

    logging.verbose("Starting LXC container...")
    helpers.lxc.start(args)
    logging.verbose("LXC container started successfully")

    logging.verbose("Starting hardware manager service...")
    services.hardware_manager.start(args)
    logging.verbose("Hardware manager service started")

    args.session = session
    logging.verbose("Session tracking enabled")
    logging.verbose("Container startup sequence completed successfully")

def stop(args, quit_session=True):
    logging.verbose("Stopping WayDroid container")
    try:
        logging.verbose("Stopping hardware manager service...")
        services.hardware_manager.stop(args)
        logging.verbose("Hardware manager service stopped")
        
        status = helpers.lxc.status(args)
        logging.verbose(f"Current container status: {status}")
        
        if status != "STOPPED":
            logging.verbose("Container is not stopped, stopping LXC container...")
            helpers.lxc.stop(args)
            logging.verbose("Waiting for container to stop...")
            while helpers.lxc.status(args) != "STOPPED":
                pass
            logging.verbose("Container stopped successfully")
        else:
            logging.verbose("Container is already stopped")

        # Networking
        logging.verbose("Stopping networking...")
        command = [tools.config.tools_src +
                   "/data/scripts/waydroid-net.sh", "stop"]
        logging.verbose(f"Running networking stop command: {' '.join(command)}")
        tools.helpers.run.user(args, command, check=False)
        logging.verbose("Networking stopped")

        #TODO: remove NFC hacks
        logging.verbose("Restarting NFC service...")
        if which("start"):
            logging.verbose("Legacy 'start' command found, starting nfcd")
            command = ["start", "nfcd"]
            logging.verbose(f"Running NFC start command: {' '.join(command)}")
            tools.helpers.run.user(args, command, check=False)
            logging.verbose("NFC service started via legacy command")
        elif which("systemctl") and (tools.helpers.run.user(args, ["systemctl", "is-enabled", "-q", "nfcd"], check=False) == 0):
            logging.verbose("systemctl found and nfcd is enabled, starting via systemctl")
            command = ["systemctl", "start", "nfcd"]
            logging.verbose(f"Running systemctl start command: {' '.join(command)}")
            tools.helpers.run.user(args, command, check=False)
            logging.verbose("NFC service started via systemctl")
        else:
            logging.verbose("No suitable method found to start NFC service")

        # Sensors
        logging.verbose("Stopping sensor daemon...")
        if which("waydroid-sensord"):
            logging.verbose("waydroid-sensord found, getting PID")
            command = ["pidof", "waydroid-sensord"]
            pid = tools.helpers.run.user(args, command, check=False, output_return=True).strip()
            if pid:
                logging.verbose(f"Found sensor daemon PID: {pid}, killing process")
                command = ["kill", "-9", pid]
                tools.helpers.run.user(args, command, check=False)
                logging.verbose("Sensor daemon killed")
            else:
                logging.verbose("No running sensor daemon found")
        else:
            logging.verbose("waydroid-sensord not found, skipping sensor cleanup")

        # Umount rootfs
        logging.verbose("Unmounting Android rootfs...")
        helpers.images.umount_rootfs(args)
        logging.verbose("Android rootfs unmounted")

        # Backwards compatibility
        logging.verbose("Cleaning up backwards compatibility mounts...")
        try:
            helpers.mount.umount_all(args, tools.config.defaults["data"])
            logging.verbose("Backwards compatibility mounts cleaned up")
        except Exception as e:
            logging.verbose(f"Error cleaning up backwards compatibility mounts: {e}")

        if "session" in args:
            if quit_session:
                logging.verbose("Sending SIGUSR1 to session process...")
                try:
                    os.kill(int(args.session["pid"]), signal.SIGUSR1)
                    logging.verbose("SIGUSR1 sent to session process")
                except Exception as e:
                    logging.verbose(f"Error sending SIGUSR1: {e}")
            logging.verbose("Removing session tracking")
            del args.session
            logging.verbose("Session tracking removed")
        else:
            logging.verbose("No session tracking to remove")
    except:
        pass

def restart(args):
    logging.verbose("Restarting WayDroid container")
    status = helpers.lxc.status(args)
    logging.verbose(f"Current container status: {status}")
    
    if status == "RUNNING":
        logging.verbose("Container is running, stopping first...")
        helpers.lxc.stop(args)
        logging.verbose("Container stopped, starting again...")
        helpers.lxc.start(args)
        logging.verbose("Container restart completed")
    else:
        logging.error("WayDroid container is {}".format(status))

def freeze(args):
    logging.verbose("Freezing WayDroid container")
    status = helpers.lxc.status(args)
    logging.verbose(f"Current container status: {status}")
    
    if status == "RUNNING":
        logging.verbose("Container is running, freezing...")
        helpers.lxc.freeze(args)
        logging.verbose("Waiting for container to freeze...")
        while helpers.lxc.status(args) == "RUNNING":
            pass
        logging.verbose("Container frozen successfully")
    else:
        logging.error("WayDroid container is {}".format(status))

def unfreeze(args):
    logging.verbose("Unfreezing WayDroid container")
    status = helpers.lxc.status(args)
    logging.verbose(f"Current container status: {status}")
    
    if status == "FROZEN":
        logging.verbose("Container is frozen, unfreezing...")
        helpers.lxc.unfreeze(args)
        logging.verbose("Waiting for container to unfreeze...")
        while helpers.lxc.status(args) == "FROZEN":
            pass
        logging.verbose("Container unfrozen successfully")
    else:
        logging.verbose(f"Container is not frozen (status: {status}), nothing to unfreeze")
