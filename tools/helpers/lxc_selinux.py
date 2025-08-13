#!/usr/bin/env python3
# LXC Helper for Waydroid with SELinux Support
# This replaces the AppArmor-based LXC helper

import os
import shutil
import platform
import tools.helpers.run
import tools.config

# SELinux configuration constants
LXC_SELINUX_CONTEXT = "system_u:system_r:waydroid_t:s0"
LXC_SELINUX_NESTING = "1"

def get_selinux_status(args):
    """Check if SELinux is enabled and available"""
    enabled = False
    
    # Check if SELinux tools are available
    if shutil.which("sestatus"):
        # Check SELinux status
        result = tools.helpers.run.user(args, ["sestatus", "--quiet"], check=False)
        enabled = (result == 0)
    
    # Check if SELinux is actually enabled in the kernel
    if enabled:
        try:
            with open("/sys/fs/selinux/enforce", "r") as f:
                selinux_enabled = f.read().strip()
                enabled = (selinux_enabled in ["0", "1"])  # 0=permissive, 1=enforcing
        except:
            enabled = False
    
    return enabled

def get_selinux_mode(args):
    """Get current SELinux mode (enforcing, permissive, disabled)"""
    if not get_selinux_status(args):
        return "disabled"
    
    try:
        with open("/sys/fs/selinux/enforce", "r") as f:
            mode = f.read().strip()
            if mode == "1":
                return "enforcing"
            elif mode == "0":
                return "permissive"
            else:
                return "unknown"
    except:
        return "unknown"

def check_selinux_policy(args):
    """Check if Waydroid SELinux policy is loaded"""
    if not get_selinux_status(args):
        return False
    
    try:
        result = tools.helpers.run.user(args, ["semodule", "-l"], check=False)
        if result == 0:
            # Check if waydroid policy is loaded
            output = tools.helpers.run.user(args, ["semodule", "-l"], capture_output=True, text=True)
            return "waydroid" in output.stdout
    except:
        pass
    
    return False

def set_lxc_config_selinux(args):
    """Set LXC configuration with SELinux support"""
    lxc_path = tools.config.defaults["lxc"] + "/waydroid"
    lxc_ver = get_lxc_version(args)
    
    if lxc_ver == 0:
        raise OSError("LXC is not installed")
    
    config_paths = tools.config.tools_src + "/data/configs/config_"
    seccomp_profile = tools.config.tools_src + "/data/configs/waydroid.seccomp"
    
    # Create LXC directory
    command = ["mkdir", "-p", lxc_path]
    tools.helpers.run.user(args, command)
    
    # Build configuration from snippets
    config_snippets = [config_paths + "base"]
    
    # Add version-specific configs
    if lxc_ver <= 2:
        config_snippets.append(config_paths + "1")
    else:
        for ver in range(3, 5):
            snippet = config_paths + str(ver)
            if lxc_ver >= ver and os.path.exists(snippet):
                config_snippets.append(snippet)
    
    # Create base config
    command = ["sh", "-c", "cat {} > \"{}\"".format(' '.join('"{0}"'.format(w) for w in config_snippets), lxc_path + "/config")]
    tools.helpers.run.user(args, command)
    
    # Replace architecture placeholder
    command = ["sed", "-i", "s/LXCARCH/{}/".format(platform.machine()), lxc_path + "/config"]
    tools.helpers.run.user(args, command)
    
    # Copy seccomp profile
    command = ["cp", "-fpr", seccomp_profile, lxc_path + "/waydroid.seccomp"]
    tools.helpers.run.user(args, command)
    
    # Add SELinux configuration if available
    if get_selinux_status(args):
        add_selinux_config(args, lxc_path)
    
    # Generate and add device nodes
    nodes = generate_nodes_lxc_config(args)
    config_nodes_tmp_path = args.work + "/config_nodes"
    config_nodes = open(config_nodes_tmp_path, "w")
    
    for node in nodes:
        config_nodes.write(node + "\n")
    config_nodes.close()
    
    # Append device nodes to config
    command = ["cat", config_nodes_tmp_path, ">>", lxc_path + "/config"]
    tools.helpers.run.user(args, command)
    
    # Clean up temporary file
    os.remove(config_nodes_tmp_path)

def add_selinux_config(args, lxc_path):
    """Add SELinux configuration to LXC config"""
    config_file = lxc_path + "/config"
    
    # Add SELinux context
    selinux_context = "lxc.selinux.context = {}\n".format(LXC_SELINUX_CONTEXT)
    selinux_nesting = "lxc.selinux.allow_nesting = {}\n".format(LXC_SELINUX_NESTING)
    
    # Append SELinux configuration
    with open(config_file, "a") as f:
        f.write("\n# SELinux Configuration\n")
        f.write(selinux_context)
        f.write(selinux_nesting)
    
    print("Added SELinux configuration to LXC config")

def remove_apparmor_config(args, lxc_path):
    """Remove AppArmor configuration from LXC config"""
    config_file = lxc_path + "/config"
    
    # Remove AppArmor-related lines
    command = ["sed", "-i", "/lxc.aa_profile/d", config_file]
    tools.helpers.run.user(args, command)
    
    command = ["sed", "-i", "/lxc.apparmor.profile/d", config_file]
    tools.helpers.run.user(args, command)
    
    print("Removed AppArmor configuration from LXC config")

def setup_selinux_policy(args):
    """Set up SELinux policy for Waydroid"""
    if not get_selinux_status(args):
        print("SELinux is not available")
        return False
    
    # Check if policy is already loaded
    if check_selinux_policy(args):
        print("Waydroid SELinux policy is already loaded")
        return True
    
    # Build and install policy
    policy_dir = tools.config.tools_src + "/data/configs/selinux_policies"
    
    if os.path.exists(policy_dir):
        print("Building SELinux policy...")
        
        # Change to policy directory
        original_dir = os.getcwd()
        os.chdir(policy_dir)
        
        try:
            # Build policy
            command = ["make", "clean"]
            tools.helpers.run.user(args, command)
            
            command = ["make"]
            result = tools.helpers.run.user(args, command)
            
            if result == 0:
                # Install policy
                command = ["sudo", "make", "install"]
                result = tools.helpers.run.user(args, command)
                
                if result == 0:
                    print("SELinux policy installed successfully")
                    os.chdir(original_dir)
                    return True
                else:
                    print("Failed to install SELinux policy")
            else:
                print("Failed to build SELinux policy")
        except Exception as e:
            print(f"Error setting up SELinux policy: {e}")
        finally:
            os.chdir(original_dir)
    else:
        print("SELinux policy directory not found")
    
    return False

def migrate_from_apparmor(args):
    """Migrate from AppArmor to SELinux"""
    print("Migrating from AppArmor to SELinux...")
    
    # Stop AppArmor service
    if shutil.which("systemctl"):
        command = ["sudo", "systemctl", "stop", "apparmor"]
        tools.helpers.run.user(args, command)
        
        command = ["sudo", "systemctl", "disable", "apparmor"]
        tools.helpers.run.user(args, command)
    
    # Unload AppArmor profiles
    if shutil.which("aa-teardown"):
        command = ["sudo", "aa-teardown"]
        tools.helpers.run.user(args, command)
    
    # Set up SELinux
    if setup_selinux_policy(args):
        print("Migration to SELinux completed successfully")
        return True
    else:
        print("Migration to SELinux failed")
        return False

# Import the original functions we need
from tools.helpers.lxc import get_lxc_version, generate_nodes_lxc_config

# Main function for backward compatibility
def set_lxc_config(args):
    """Main function - use SELinux if available, fallback to AppArmor"""
    if get_selinux_status(args):
        print("Using SELinux for LXC configuration")
        set_lxc_config_selinux(args)
        
        # Set up SELinux policy if not already loaded
        if not check_selinux_policy(args):
            setup_selinux_policy(args)
    else:
        print("SELinux not available, using AppArmor fallback")
        # Import and use original AppArmor-based function
        from tools.helpers.lxc import set_lxc_config as set_lxc_config_apparmor
        set_lxc_config_apparmor(args)

if __name__ == "__main__":
    print("LXC Helper with SELinux Support")
    print("This module provides SELinux support for Waydroid LXC containers")
