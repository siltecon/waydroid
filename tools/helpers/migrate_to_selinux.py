#!/usr/bin/env python3
# Migration Script: AppArmor to SELinux for Waydroid
# This script helps migrate from AppArmor to SELinux

import os
import sys
import shutil
import subprocess
import argparse

def check_root():
    """Check if running as root"""
    if os.geteuid() != 0:
        print("Error: This script must be run as root (use sudo)")
        sys.exit(1)

def check_selinux_available():
    """Check if SELinux is available on the system"""
    if not os.path.exists("/sys/fs/selinux"):
        print("Error: SELinux is not available on this system")
        return False
    
    if not shutil.which("sestatus"):
        print("Error: SELinux tools not found. Please install selinux-policy-utils")
        return False
    
    return True

def check_apparmor_status():
    """Check current AppArmor status"""
    if shutil.which("aa-status"):
        try:
            result = subprocess.run(["aa-status", "--quiet"], capture_output=True)
            return result.returncode == 0
        except:
            pass
    
    if shutil.which("systemctl"):
        try:
            result = subprocess.run(["systemctl", "is-active", "apparmor"], capture_output=True)
            return result.returncode == 0
        except:
            pass
    
    return False

def stop_apparmor():
    """Stop and disable AppArmor"""
    print("Stopping AppArmor...")
    
    # Stop AppArmor service
    if shutil.which("systemctl"):
        try:
            subprocess.run(["systemctl", "stop", "apparmor"], check=True)
            subprocess.run(["systemctl", "disable", "apparmor"], check=True)
            print("AppArmor service stopped and disabled")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to stop AppArmor service: {e}")
    
    # Unload AppArmor profiles
    if shutil.which("aa-teardown"):
        try:
            subprocess.run(["aa-teardown"], check=True)
            print("AppArmor profiles unloaded")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to unload AppArmor profiles: {e}")

def enable_selinux():
    """Enable SELinux"""
    print("Enabling SELinux...")
    
    # Check current SELinux status
    try:
        result = subprocess.run(["sestatus"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Current SELinux status:")
            print(result.stdout)
    except:
        pass
    
    # Set SELinux to permissive mode initially
    try:
        subprocess.run(["setenforce", "0"], check=True)
        print("SELinux set to permissive mode")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to set SELinux mode: {e}")
    
    # Update SELinux configuration
    selinux_config = "/etc/selinux/config"
    if os.path.exists(selinux_config):
        try:
            # Backup original config
            backup_config = selinux_config + ".backup"
            shutil.copy2(selinux_config, backup_config)
            print(f"Backed up SELinux config to {backup_config}")
            
            # Update config to enable SELinux
            with open(selinux_config, 'r') as f:
                content = f.read()
            
            # Replace SELINUX=disabled with SELINUX=permissive
            content = content.replace("SELINUX=disabled", "SELINUX=permissive")
            content = content.replace("SELINUX=enforcing", "SELINUX=permissive")
            
            with open(selinux_config, 'w') as f:
                f.write(content)
            
            print("SELinux configuration updated")
        except Exception as e:
            print(f"Warning: Failed to update SELinux config: {e}")

def build_selinux_policy():
    """Build and install SELinux policy"""
    print("Building SELinux policy...")
    
    # Find the policy directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    policy_dir = os.path.join(script_dir, "..", "..", "data", "configs", "selinux_policies")
    
    if not os.path.exists(policy_dir):
        print(f"Error: SELinux policy directory not found: {policy_dir}")
        return False
    
    # Change to policy directory
    original_dir = os.getcwd()
    os.chdir(policy_dir)
    
    try:
        # Check if make is available
        if not shutil.which("make"):
            print("Error: 'make' command not found. Please install build-essential")
            return False
        
        # Check if SELinux development tools are available
        if not shutil.which("checkpolicy"):
            print("Error: 'checkpolicy' not found. Please install selinux-policy-dev")
            return False
        
        if not shutil.which("semodule_package"):
            print("Error: 'semodule_package' not found. Please install selinux-policy-dev")
            return False
        
        # Clean and build
        print("Cleaning previous build...")
        subprocess.run(["make", "clean"], check=True)
        
        print("Building policy...")
        subprocess.run(["make"], check=True)
        
        print("Installing policy...")
        subprocess.run(["make", "install"], check=True)
        
        print("SELinux policy built and installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error building SELinux policy: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        os.chdir(original_dir)

def update_waydroid_config():
    """Update Waydroid configuration to use SELinux"""
    print("Updating Waydroid configuration...")
    
    waydroid_config = "/etc/waydroid/waydroid.cfg"
    
    if os.path.exists(waydroid_config):
        try:
            # Backup original config
            backup_config = waydroid_config + ".backup"
            shutil.copy2(waydroid_config, backup_config)
            print(f"Backed up Waydroid config to {backup_config}")
            
            # Read current config
            with open(waydroid_config, 'r') as f:
                content = f.read()
            
            # Add SELinux configuration if not present
            if "security = selinux" not in content:
                content += "\n# SELinux Configuration\n"
                content += "security = selinux\n"
                content += "selinux_policy = /etc/selinux/targeted/policy/waydroid.pp\n"
                
                with open(waydroid_config, 'w') as f:
                    f.write(content)
                
                print("Waydroid configuration updated for SELinux")
            else:
                print("Waydroid already configured for SELinux")
        except Exception as e:
            print(f"Warning: Failed to update Waydroid config: {e}")
    else:
        print("Warning: Waydroid configuration file not found")

def update_lxc_config():
    """Update LXC configuration to use SELinux"""
    print("Updating LXC configuration...")
    
    lxc_config = "/var/lib/waydroid/lxc/waydroid/config"
    
    if os.path.exists(lxc_config):
        try:
            # Backup original config
            backup_config = lxc_config + ".backup"
            shutil.copy2(lxc_config, backup_config)
            print(f"Backed up LXC config to {backup_config}")
            
            # Remove AppArmor configuration
            subprocess.run(["sed", "-i", "/lxc.aa_profile/d", lxc_config])
            subprocess.run(["sed", "-i", "/lxc.apparmor.profile/d", lxc_config])
            
            # Add SELinux configuration
            with open(lxc_config, 'a') as f:
                f.write("\n# SELinux Configuration\n")
                f.write("lxc.selinux.context = system_u:system_r:waydroid_t:s0\n")
                f.write("lxc.selinux.allow_nesting = 1\n")
            
            print("LXC configuration updated for SELinux")
        except Exception as e:
            print(f"Warning: Failed to update LXC config: {e}")
    else:
        print("Warning: LXC configuration file not found")

def verify_selinux_setup():
    """Verify SELinux setup"""
    print("\nVerifying SELinux setup...")
    
    # Check SELinux status
    try:
        result = subprocess.run(["sestatus"], capture_output=True, text=True)
        if result.returncode == 0:
            print("SELinux Status:")
            print(result.stdout)
    except:
        print("Warning: Could not check SELinux status")
    
    # Check if Waydroid policy is loaded
    try:
        result = subprocess.run(["semodule", "-l"], capture_output=True, text=True)
        if result.returncode == 0 and "waydroid" in result.stdout:
            print("✓ Waydroid SELinux policy is loaded")
        else:
            print("✗ Waydroid SELinux policy is not loaded")
    except:
        print("Warning: Could not check SELinux policies")
    
    # Check file contexts
    waydroid_dirs = ["/var/lib/waydroid", "/data/waydroid"]
    for directory in waydroid_dirs:
        if os.path.exists(directory):
            try:
                result = subprocess.run(["ls", "-Z", directory], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✓ File contexts for {directory}:")
                    print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
            except:
                print(f"Warning: Could not check file contexts for {directory}")

def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(description="Migrate Waydroid from AppArmor to SELinux")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--force", action="store_true", help="Force migration even if checks fail")
    
    args = parser.parse_args()
    
    print("Waydroid AppArmor to SELinux Migration Tool")
    print("=" * 50)
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print()
    
    # Check prerequisites
    if not args.force:
        check_root()
        
        if not check_selinux_available():
            print("Error: Cannot proceed without SELinux support")
            sys.exit(1)
    
    # Migration steps
    try:
        if check_apparmor_status():
            print("AppArmor is currently active")
            if not args.dry_run:
                stop_apparmor()
            else:
                print("Would stop AppArmor")
        else:
            print("AppArmor is not active")
        
        if not args.dry_run:
            enable_selinux()
        else:
            print("Would enable SELinux")
        
        if not args.dry_run:
            if build_selinux_policy():
                update_waydroid_config()
                update_lxc_config()
            else:
                print("Error: Failed to build SELinux policy")
                sys.exit(1)
        else:
            print("Would build SELinux policy")
            print("Would update Waydroid configuration")
            print("Would update LXC configuration")
        
        if not args.dry_run:
            verify_selinux_setup()
        else:
            print("Would verify SELinux setup")
        
        print("\nMigration completed successfully!")
        print("\nNext steps:")
        print("1. Reboot your system to ensure SELinux is fully enabled")
        print("2. Test Waydroid functionality")
        print("3. If everything works, you can set SELinux to enforcing mode:")
        print("   sudo setenforce 1")
        print("   sudo sed -i 's/^SELINUX=.*/SELINUX=enforcing/' /etc/selinux/config")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
