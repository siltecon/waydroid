#!/usr/bin/env python3
# Copyright 2021 Erfan Abdi
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import logging
import sys
import os

# Add the tools directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from tools.actions.modular_container_manager import ModularContainerManager
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
        description='Modular Waydroid Container Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  waydroid-modular step1                    # Run only environment setup
  waydroid-modular step2                    # Run only container preparation
  waydroid-modular step3                    # Run only container start
  waydroid-modular step4                    # Run only hardware services
  waydroid-modular all                      # Run all steps
  waydroid-modular status                   # Show status of all steps
  waydroid-modular diagnose                 # Diagnose any failures
  waydroid-modular reset                    # Reset step results
        """
    )
    
    parser.add_argument(
        'command',
        choices=['step1', 'step2', 'step3', 'step4', 'all', 'status', 'diagnose', 'reset'],
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
        '--skip-hardware',
        action='store_true',
        help='Skip hardware services even when running all steps'
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
        
        # Create modular container manager
        manager = ModularContainerManager(config_args)
        
        # Execute command
        if args.command == 'step1':
            logging.info("Executing Step 1: Environment Setup")
            success = manager.step1_setup_environment()
            sys.exit(0 if success else 1)
            
        elif args.command == 'step2':
            logging.info("Executing Step 2: Container Preparation")
            success = manager.step2_prepare_container()
            sys.exit(0 if success else 1)
            
        elif args.command == 'step3':
            logging.info("Executing Step 3: Container Start")
            success = manager.step3_start_container()
            sys.exit(0 if success else 1)
            
        elif args.command == 'step4':
            logging.info("Executing Step 4: Hardware Services")
            success = manager.step4_hardware_services()
            sys.exit(0 if success else 1)
            
        elif args.command == 'all':
            logging.info("Executing All Steps")
            if args.skip_hardware:
                logging.info("Skipping hardware services as requested")
                # Run steps 1-3 only
                success = (manager.step1_setup_environment() and
                          manager.step2_prepare_container() and
                          manager.step3_start_container())
                if success:
                    manager.step_results['step4'] = 'SKIPPED: Hardware services disabled'
            else:
                success = manager.run_all_steps()
            sys.exit(0 if success else 1)
            
        elif args.command == 'status':
            status = manager.get_status()
            if status:
                print("Waydroid Container Status:")
                for step, result in status.items():
                    print(f"  {step}: {result}")
            else:
                print("No steps have been executed yet")
            sys.exit(0)
            
        elif args.command == 'diagnose':
            failed_steps = manager.diagnose()
            if failed_steps:
                print(f"Diagnosis complete. Failed steps: {', '.join(failed_steps)}")
                sys.exit(1)
            else:
                print("All steps completed successfully")
                sys.exit(0)
                
        elif args.command == 'reset':
            manager.reset()
            print("Step results have been reset")
            sys.exit(0)
            
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
