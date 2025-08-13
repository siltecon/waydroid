#!/bin/bash
# SELinux helper script for Waydroid
# Manages SELinux contexts and policies for Waydroid container

set -e

WAYDROID_DATA_DIR="/var/lib/waydroid"
WAYDROID_LXC_DIR="/var/lib/lxc/waydroid0"
WAYDROID_USER_DIR="$HOME/.local/share/waydroid"
SELINUX_POLICY_DIR="/usr/share/selinux/packages/waydroid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if SELinux is enabled
check_selinux() {
    if ! command -v getenforce &> /dev/null; then
        echo -e "${RED}SELinux tools not found. Please install policycoreutils.${NC}"
        exit 1
    fi

    local status=$(getenforce 2>/dev/null || echo "Disabled")
    if [ "$status" = "Disabled" ]; then
        echo -e "${YELLOW}SELinux is disabled. Enable SELinux to use these features.${NC}"
        exit 0
    fi
    echo -e "${GREEN}SELinux status: $status${NC}"
}

# Set file contexts for Waydroid directories
set_contexts() {
    echo "Setting SELinux file contexts for Waydroid..."
    
    # Set contexts for main data directory
    if [ -d "$WAYDROID_DATA_DIR" ]; then
        semanage fcontext -a -t waydroid_data_t "$WAYDROID_DATA_DIR(/.*)?" 2>/dev/null || true
        restorecon -Rv "$WAYDROID_DATA_DIR"
    fi
    
    # Set contexts for LXC container directory
    if [ -d "$WAYDROID_LXC_DIR" ]; then
        semanage fcontext -a -t waydroid_data_t "$WAYDROID_LXC_DIR(/.*)?" 2>/dev/null || true
        restorecon -Rv "$WAYDROID_LXC_DIR"
    fi
    
    # Set contexts for user session directory
    if [ -d "$WAYDROID_USER_DIR" ]; then
        semanage fcontext -a -t waydroid_data_t "$WAYDROID_USER_DIR(/.*)?" 2>/dev/null || true
        restorecon -Rv "$WAYDROID_USER_DIR"
    fi
    
    # Set contexts for binder devices
    for device in /dev/binder /dev/vndbinder /dev/hwbinder /dev/anbox-binder /dev/anbox-vndbinder /dev/anbox-hwbinder; do
        if [ -e "$device" ]; then
            chcon -t waydroid_data_t "$device" 2>/dev/null || true
        fi
    done
    
    echo -e "${GREEN}File contexts set successfully.${NC}"
}

# Load SELinux policy modules
load_policies() {
    echo "Loading Waydroid SELinux policy modules..."
    
    if [ ! -d "$SELINUX_POLICY_DIR" ]; then
        echo -e "${RED}SELinux policy directory not found at $SELINUX_POLICY_DIR${NC}"
        echo "Please run 'make install_selinux' first."
        exit 1
    fi
    
    cd "$SELINUX_POLICY_DIR"
    make install
    
    echo -e "${GREEN}SELinux policies loaded successfully.${NC}"
}

# Remove SELinux policy modules
remove_policies() {
    echo "Removing Waydroid SELinux policy modules..."
    
    semodule -r waydroid waydroid_app waydroid_adbd 2>/dev/null || true
    
    # Remove file contexts
    semanage fcontext -d "$WAYDROID_DATA_DIR(/.*)?" 2>/dev/null || true
    semanage fcontext -d "$WAYDROID_LXC_DIR(/.*)?" 2>/dev/null || true
    semanage fcontext -d "$WAYDROID_USER_DIR(/.*)?" 2>/dev/null || true
    
    echo -e "${GREEN}SELinux policies removed.${NC}"
}

# Check policy status
check_status() {
    echo "Checking Waydroid SELinux policy status..."
    
    if semodule -l | grep -q "^waydroid"; then
        echo -e "${GREEN}Waydroid SELinux policies are installed:${NC}"
        semodule -l | grep "^waydroid"
    else
        echo -e "${YELLOW}Waydroid SELinux policies are not installed.${NC}"
    fi
    
    echo ""
    echo "File contexts for Waydroid directories:"
    semanage fcontext -l | grep waydroid || echo "No Waydroid file contexts found."
}

# Set permissive mode for Waydroid domain (for debugging)
set_permissive() {
    echo "Setting Waydroid SELinux domain to permissive mode..."
    
    semanage permissive -a waydroid_t 2>/dev/null || true
    semanage permissive -a waydroid_app_t 2>/dev/null || true
    semanage permissive -a waydroid_adbd_t 2>/dev/null || true
    
    echo -e "${YELLOW}Waydroid domains set to permissive mode.${NC}"
    echo "This is for debugging only. Run 'waydroid-selinux.sh enforce' to re-enable enforcement."
}

# Set enforcing mode for Waydroid domain
set_enforcing() {
    echo "Setting Waydroid SELinux domain to enforcing mode..."
    
    semanage permissive -d waydroid_t 2>/dev/null || true
    semanage permissive -d waydroid_app_t 2>/dev/null || true
    semanage permissive -d waydroid_adbd_t 2>/dev/null || true
    
    echo -e "${GREEN}Waydroid domains set to enforcing mode.${NC}"
}

# View SELinux denials related to Waydroid
view_denials() {
    echo "Recent SELinux denials for Waydroid:"
    
    if command -v ausearch &> /dev/null; then
        ausearch -m avc -c waydroid --start recent 2>/dev/null || \
        ausearch -m avc --start recent 2>/dev/null | grep -i waydroid || \
        echo "No recent Waydroid-related denials found."
    else
        echo -e "${YELLOW}ausearch not found. Install audit tools to view denials.${NC}"
        echo "You can also check: journalctl -xe | grep -i waydroid"
    fi
}

# Generate SELinux policy from denials
generate_policy() {
    echo "Generating SELinux policy from recent denials..."
    
    if ! command -v audit2allow &> /dev/null; then
        echo -e "${RED}audit2allow not found. Please install policycoreutils-devel.${NC}"
        exit 1
    fi
    
    local policy_file="/tmp/waydroid_custom.te"
    
    ausearch -m avc -c waydroid --start recent 2>/dev/null | \
        audit2allow -M waydroid_custom > "$policy_file" 2>/dev/null
    
    if [ -s "$policy_file" ]; then
        echo -e "${GREEN}Custom policy generated at: $policy_file${NC}"
        echo "Review the policy and install with: semodule -i waydroid_custom.pp"
    else
        echo "No denials found to generate policy from."
    fi
}

# Print usage
usage() {
    echo "Waydroid SELinux Helper Script"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  setup       - Set up SELinux contexts and load policies"
    echo "  load        - Load SELinux policy modules"
    echo "  remove      - Remove SELinux policy modules"
    echo "  status      - Check SELinux policy status"
    echo "  contexts    - Set file contexts for Waydroid directories"
    echo "  permissive  - Set Waydroid domain to permissive mode (debugging)"
    echo "  enforce     - Set Waydroid domain to enforcing mode"
    echo "  denials     - View recent SELinux denials for Waydroid"
    echo "  generate    - Generate custom policy from denials"
    echo "  help        - Show this help message"
}

# Main script logic
case "${1:-}" in
    setup)
        check_selinux
        load_policies
        set_contexts
        ;;
    load)
        check_selinux
        load_policies
        ;;
    remove)
        check_selinux
        remove_policies
        ;;
    status)
        check_selinux
        check_status
        ;;
    contexts)
        check_selinux
        set_contexts
        ;;
    permissive)
        check_selinux
        set_permissive
        ;;
    enforce)
        check_selinux
        set_enforcing
        ;;
    denials)
        check_selinux
        view_denials
        ;;
    generate)
        check_selinux
        generate_policy
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        usage
        exit 1
        ;;
esac