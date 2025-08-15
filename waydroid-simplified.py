#!/usr/bin/env python3
# Copyright 2021 Erfan Abdi
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import logging
import sys
import os

# Add the tools directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from tools.actions.simplified_container_manager import (
    start_simplified, 
    do_start_simplified, 
    stop_simplified,
    restart_simplified,
    freeze_simplified,
    unfreeze_simplified
)
import tools.config

def setup_logging(verbose=False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )

def main():
    parser = argparse.ArgumentParser(
        description='Simplified Waydroid Container Manager (No Hardware Manager)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  waydroid-simplified start              # Start container without hardware manager
  waydroid-simplified stop               # Stop container
  waydroid-simplified restart            # Restart container
  waydroid-simplified freeze             # Freeze container
  waydroid-simplified unfreeze           # Unfreeze container
  waydroid-simplified status             # Show container status
        """
    )
    
    parser.add_argument(
        'command',
        choices=['start', 'stop', 'restart', 'freeze', 'unfreeze', 'status'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--config', '-c',
        default='/etc/waydroid/waydroid.conf',
        help='Path to Waydroid configuration file'
    )
    
    parser.add_argument(
        '--session',
        action='store_true',
        help='Start with session management'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    try:
        # Load Waydroid configuration
        if not os.path.exists(args.config):
            logging.error(f"Configuration file not found: {args.config}")
            sys.exit(1)
        
        # Initialize configuration
        config_args = tools.config.load_config(args.config)
        
        # Execute command
        if args.command == 'start':
            logging.info("Starting simplified Waydroid container (no hardware manager)...")
            if args.session:
                # Create a basic session
                session = {
                    "user_id": "0",
                    "pid": str(os.getpid()),
                    "waydroid_data": "/var/lib/waydroid/data"
                }
                do_start_simplified(config_args, session)
                logging.info("✅ Container started with session management")
            else:
                start_simplified(config_args)
                logging.info("✅ Container started successfully")
                
        elif args.command == 'stop':
            logging.info("Stopping Waydroid container...")
            stop_simplified(config_args)
            logging.info("✅ Container stopped successfully")
            
        elif args.command == 'restart':
            logging.info("Restarting Waydroid container...")
            restart_simplified(config_args)
            logging.info("✅ Container restarted successfully")
            
        elif args.command == 'freeze':
            logging.info("Freezing Waydroid container...")
            freeze_simplified(config_args)
            logging.info("✅ Container frozen successfully")
            
        elif args.command == 'unfreeze':
            logging.info("Unfreezing Waydroid container...")
            unfreeze_simplified(config_args)
            logging.info("✅ Container unfrozen successfully")
            
        elif args.command == 'status':
            try:
                from tools import helpers
                status = helpers.lxc.status(config_args)
                print(f"Container status: {status}")
                if status == "RUNNING":
                    print("✅ Container is running (simplified mode - no hardware manager)")
                elif status == "STOPPED":
                    print("⏹️ Container is stopped")
                elif status == "FROZEN":
                    print("❄️ Container is frozen")
                else:
                    print(f"❓ Container status: {status}")
            except Exception as e:
                logging.error(f"Failed to get container status: {str(e)}")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logging.info("Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
