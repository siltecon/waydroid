# Copyright 2021 Erfan Abdi
# SPDX-License-Identifier: GPL-3.0-or-later
from shutil import which
import logging
import os
import glob
import signal
import tools.config
from tools import helpers
from gi.repository import GLib

def set_permissions(args, perm_list=None, mode="777"):
    def chmod(path, mode):
        if os.path.exists(path):
            command = ["chmod", mode, "-R", path]
            tools.helpers.run.user(args, command, check=False)

    # Nodes list
    if not perm_list:
        perm_list = [
            "/dev/ashmem",
            "/dev/sw_sync",
            "/sys/kernel/debug/sync/sw_sync",
            "/dev/Vcodec",
            "/dev/MTK_SMI",
            "/dev/mdp_sync",
            "/dev/mtk_cmdq",
            "/dev/graphics",
            "/dev/pvr_sync",
            "/dev/ion",
        ]

        # DRM render nodes
        perm_list.extend(glob.glob("/dev/dri/renderD*"))
        # Framebuffers
        perm_list.extend(glob.glob("/dev/fb*"))
        # Videos
        perm_list.extend(glob.glob("/dev/video*"))
        # DMA-BUF Heaps
        perm_list.extend(glob.glob("/dev/dma_heap/*"))

    for path in perm_list:
        chmod(path, mode)

def start_simplified(args):
    """Simplified container start without hardware manager"""
    try:
        name = dbus.service.BusName("id.waydro.Container", dbus.SystemBus(), do_not_queue=True)
    except dbus.exceptions.NameExistsException:
        logging.error("Container service is already running")
        return

    status = helpers.lxc.status(args)
    if status == "STOPPED":
        # Load binder and ashmem drivers
        cfg = tools.config.load(args)
        if cfg["waydroid"]["vendor_type"] == "MAINLINE":
            if helpers.drivers.probeBinderDriver(args) != 0:
                logging.error("Failed to load Binder driver")
            helpers.drivers.probeAshmemDriver(args)
        helpers.drivers.loadBinderNodes(args)
        
        # Set basic permissions for binder devices
        set_permissions(args, [
            "/dev/" + args.BINDER_DRIVER,
            "/dev/" + args.VNDBINDER_DRIVER,
            "/dev/" + args.HWBINDER_DRIVER
        ], "666")

        mainloop = GLib.MainLoop()

        def sigint_handler(data):
            stop_simplified(args)
            mainloop.quit()

        GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGINT, sigint_handler, None)
        GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGTERM, sigint_handler, None)
        service_simplified(args, mainloop)
    else:
        logging.error("WayDroid container is {}".format(status))

def do_start_simplified(args, session):
    """Simplified container start - no hardware manager, no complex networking"""
    if "session" in args:
        raise RuntimeError("Already tracking a session")

    # Basic networking setup (simplified)
    try:
        command = [tools.config.tools_src + "/data/scripts/waydroid-net.sh", "start"]
        tools.helpers.run.user(args, command)
    except Exception as e:
        logging.warning(f"Basic networking setup failed: {str(e)}")

    # Set basic permissions
    set_permissions(args)

    # Create session-specific LXC config file
    helpers.lxc.generate_session_lxc_config(args, session)
    
    # Backwards compatibility
    with open(tools.config.defaults["lxc"] + "/waydroid/config") as f:
        if "config_session" not in f.read():
            helpers.mount.bind(args, session["waydroid_data"],
                               tools.config.defaults["data"])

    # Mount rootfs
    cfg = tools.config.load(args)
    helpers.images.mount_rootfs(args, cfg["waydroid"]["images_path"], session)

    helpers.protocol.set_aidl_version(args)

    # Start LXC container (no hardware manager)
    helpers.lxc.start(args)

    args.session = session

def stop_simplified(args, quit_session=True):
    """Simplified container stop"""
    try:
        status = helpers.lxc.status(args)
        if status != "STOPPED":
            helpers.lxc.stop(args)
            while helpers.lxc.status(args) != "STOPPED":
                pass

        # Basic networking cleanup
        try:
            command = [tools.config.tools_src + "/data/scripts/waydroid-net.sh", "stop"]
            tools.helpers.run.user(args, command, check=False)
        except Exception as e:
            logging.warning(f"Network cleanup failed: {str(e)}")

        # Umount rootfs
        helpers.images.umount_rootfs(args)

        # Backwards compatibility
        try:
            helpers.mount.umount_all(args, tools.config.defaults["data"])
        except:
            pass

        if "session" in args:
            if quit_session:
                try:
                    os.kill(int(args.session["pid"]), signal.SIGUSR1)
                except:
                    pass
            del args.session
    except Exception as e:
        logging.error(f"Error during stop: {str(e)}")

def service_simplified(args, looper):
    """Simplified service without hardware manager"""
    # This is a minimal service that just keeps the container running
    # No hardware management, no complex DBus interfaces
    
    def sigint_handler(data):
        logging.info("Received interrupt signal, stopping container")
        stop_simplified(args)
        looper.quit()

    GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGINT, sigint_handler, None)
    GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGTERM, sigint_handler, None)
    
    logging.info("Simplified Waydroid container service started")
    logging.info("Container is running without hardware manager")
    logging.info("Use Ctrl+C to stop the container")
    
    looper.run()

def restart_simplified(args):
    """Simplified container restart"""
    status = helpers.lxc.status(args)
    if status == "RUNNING":
        helpers.lxc.stop(args)
        helpers.lxc.start(args)
    else:
        logging.error("WayDroid container is {}".format(status))

def freeze_simplified(args):
    """Simplified container freeze"""
    status = helpers.lxc.status(args)
    if status == "RUNNING":
        helpers.lxc.freeze(args)
        while helpers.lxc.status(args) == "RUNNING":
            pass
    else:
        logging.error("WayDroid container is {}".format(status))

def unfreeze_simplified(args):
    """Simplified container unfreeze"""
    status = helpers.lxc.status(args)
    if status == "FROZEN":
        helpers.lxc.unfreeze(args)
        while helpers.lxc.status(args) == "FROZEN":
            pass
