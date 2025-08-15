# Copyright 2021 Erfan Abdi
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import os
import glob
import signal
import threading
import time
import tools.config
from tools import helpers
from tools import services
from gi.repository import GLib

class ModularContainerManager:
    def __init__(self, args):
        self.args = args
        self.step_results = {}
        self.session = None
        
    def step1_setup_environment(self):
        """Step 1: Basic environment setup - drivers and permissions"""
        try:
            logging.info("Step 1: Setting up environment...")
            
            # Load binder and ashmem drivers
            cfg = tools.config.load(self.args)
            if cfg["waydroid"]["vendor_type"] == "MAINLINE":
                if helpers.drivers.probeBinderDriver(self.args) != 0:
                    logging.error("Failed to load Binder driver")
                    return False
                helpers.drivers.probeAshmemDriver(self.args)
            
            helpers.drivers.loadBinderNodes(self.args)
            
            # Set basic device permissions
            self._set_basic_permissions()
            
            self.step_results['step1'] = 'SUCCESS'
            logging.info("✅ Step 1 completed successfully")
            return True
            
        except Exception as e:
            self.step_results['step1'] = f'FAILED: {str(e)}'
            logging.error(f"❌ Step 1 failed: {str(e)}")
            return False
    
    def step2_prepare_container(self):
        """Step 2: Container preparation - config and mounting"""
        try:
            logging.info("Step 2: Preparing container...")
            
            # Create session if not exists
            if not hasattr(self.args, 'session'):
                self.session = self._create_session()
                self.args.session = self.session
            
            # Basic networking setup (simplified)
            self._setup_basic_networking()
            
            # Generate LXC configuration
            helpers.lxc.generate_session_lxc_config(self.args, self.args.session)
            
            # Mount rootfs
            cfg = tools.config.load(self.args)
            helpers.images.mount_rootfs(self.args, cfg["waydroid"]["images_path"], self.args.session)
            
            # Set protocol version
            helpers.protocol.set_aidl_version(self.args)
            
            self.step_results['step2'] = 'SUCCESS'
            logging.info("✅ Step 2 completed successfully")
            return True
            
        except Exception as e:
            self.step_results['step2'] = f'FAILED: {str(e)}'
            logging.error(f"❌ Step 2 failed: {str(e)}")
            return False
    
    def step3_start_container(self):
        """Step 3: Start LXC container"""
        try:
            logging.info("Step 3: Starting container...")
            
            # Start LXC container
            helpers.lxc.start(self.args)
            
            # Wait for container to be ready
            if self._wait_for_container_ready():
                self.step_results['step3'] = 'SUCCESS'
                logging.info("✅ Step 3 completed successfully")
                return True
            else:
                self.step_results['step3'] = 'FAILED: Container not ready'
                logging.error("❌ Step 3 failed: Container not ready")
                return False
                
        except Exception as e:
            self.step_results['step3'] = f'FAILED: {str(e)}'
            logging.error(f"❌ Step 3 failed: {str(e)}")
            return False
    
    def step4_hardware_services(self):
        """Step 4: Hardware services (optional)"""
        try:
            logging.info("Step 4: Starting hardware services...")
            
            # Start hardware manager
            services.hardware_manager.start(self.args)
            
            self.step_results['step4'] = 'SUCCESS'
            logging.info("✅ Step 4 completed successfully")
            return True
            
        except Exception as e:
            self.step_results['step4'] = f'FAILED: {str(e)}'
            logging.error(f"❌ Step 4 failed: {str(e)}")
            return False
    
    def run_all_steps(self):
        """Run all steps in sequence"""
        logging.info("Running all Waydroid startup steps...")
        
        if not self.step1_setup_environment():
            return False
        
        if not self.step2_prepare_container():
            return False
        
        if not self.step3_start_container():
            return False
        
        # Step 4 is optional - skip if it fails
        try:
            self.step4_hardware_services()
        except Exception as e:
            logging.warning(f"Step 4 (hardware services) failed, continuing without it: {str(e)}")
            self.step_results['step4'] = 'SKIPPED: Hardware services failed'
        
        logging.info("✅ All steps completed")
        return True
    
    def get_status(self):
        """Get status of all steps"""
        return self.step_results
    
    def diagnose(self):
        """Diagnose any failures"""
        failed_steps = [step for step, result in self.step_results.items() if 'FAILED' in result]
        if failed_steps:
            logging.error(f"Failed steps: {', '.join(failed_steps)}")
            for step in failed_steps:
                logging.error(f"  {step}: {self.step_results[step]}")
        else:
            logging.info("All steps completed successfully")
        return failed_steps
    
    def reset(self):
        """Reset all step results"""
        self.step_results = {}
        logging.info("Step results reset")
    
    def _set_basic_permissions(self):
        """Set basic device permissions"""
        def chmod(path, mode):
            if os.path.exists(path):
                command = ["chmod", mode, "-R", path]
                tools.helpers.run.user(self.args, command, check=False)
        
        # Essential binder nodes
        perm_list = [
            "/dev/" + self.args.BINDER_DRIVER,
            "/dev/" + self.args.VNDBINDER_DRIVER,
            "/dev/" + self.args.HWBINDER_DRIVER
        ]
        
        for path in perm_list:
            chmod(path, "666")
    
    def _setup_basic_networking(self):
        """Setup basic networking (simplified)"""
        try:
            command = [tools.config.tools_src + "/data/scripts/waydroid-net.sh", "start"]
            tools.helpers.run.user(self.args, command)
        except Exception as e:
            logging.warning(f"Basic networking setup failed: {str(e)}")
    
    def _create_session(self):
        """Create a basic session"""
        # This is a simplified session creation
        # In a real implementation, you'd want more robust session management
        session = {
            "user_id": "0",
            "pid": str(os.getpid()),
            "waydroid_data": "/var/lib/waydroid/data"
        }
        return session
    
    def _wait_for_container_ready(self, timeout=60):
        """Wait for container to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status = helpers.lxc.status(self.args)
                if status == "RUNNING":
                    return True
                time.sleep(1)
            except Exception:
                time.sleep(1)
        return False

# Convenience functions for backward compatibility
def start_modular(args):
    """Start Waydroid using modular approach"""
    manager = ModularContainerManager(args)
    return manager.run_all_steps()

def start_step_by_step(args, steps):
    """Start specific steps"""
    manager = ModularContainerManager(args)
    
    if 'step1' in steps:
        manager.step1_setup_environment()
    if 'step2' in steps:
        manager.step2_prepare_container()
    if 'step3' in steps:
        manager.step3_start_container()
    if 'step4' in steps:
        manager.step4_hardware_services()
    
    return manager.get_status()
