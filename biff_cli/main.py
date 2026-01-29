"""
BIFF Agents CLI

Command-line interface for BIFF AI agents.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from biff_agents_core.validators.config_validator import ConfigValidator
from biff_agents_core.utils.cli_helpers import (
    print_header, print_success, print_error, print_info
)


def create_parser():
    """Create argument parser for CLI"""
    parser = argparse.ArgumentParser(
        prog='biff',
        description='BIFF Framework AI Agents - Intelligent configuration tools'
    )
    parser.add_argument('--version', action='version', version='biff 0.1.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate BIFF configuration files'
    )
    validate_parser.add_argument(
        'config_file',
        type=Path,
        help='Path to configuration file (Minion/Oscar/Marvin)'
    )
    validate_parser.add_argument(
        '-t', '--type',
        choices=['minion', 'oscar', 'marvin', 'auto'],
        default='auto',
        help='Configuration type (default: auto-detect)'
    )
    
    # Quickstart command
    quickstart_parser = subparsers.add_parser(
        'quickstart',
        help='Quick Start Orchestrator - Generate complete BIFF setup'
    )
    quickstart_parser.add_argument(
        '-d', '--directory',
        type=Path,
        default=Path.cwd(),
        help='Output directory (default: current directory)'
    )
    quickstart_parser.add_argument(
        '-p', '--preset',
        choices=['basic', 'monitoring', 'dashboard', 'custom'],
        default='basic',
        help='Preset configuration (default: basic)'
    )
    
    # Collector command
    collector_parser = subparsers.add_parser(
        'collector',
        help='Minion Collector Builder - Generate collector configurations'
    )
    collector_parser.add_argument(
        'config_file',
        type=Path,
        help='Path to MinionConfig.xml'
    )
    collector_parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive mode with guided prompts'
    )
    
    # GUI command
    gui_parser = subparsers.add_parser(
        'gui',
        help='Marvin GUI Composer - Generate widget configurations'
    )
    gui_parser.add_argument(
        'config_file',
        type=Path,
        help='Path to Marvin configuration XML'
    )
    gui_parser.add_argument(
        '--template',
        help='Widget template to use'
    )
    
    # Oscar command
    oscar_parser = subparsers.add_parser(
        'oscar',
        help='Oscar Routing Configurator - Set up data routing'
    )
    oscar_parser.add_argument(
        'config_file',
        type=Path,
        help='Path to OscarConfig.xml'
    )
    
    # Debug command
    debug_parser = subparsers.add_parser(
        'debug',
        help='BIFF Debugging Agent - Diagnose runtime issues'
    )
    debug_parser.add_argument(
        '--component',
        choices=['minion', 'oscar', 'marvin', 'all'],
        default='all',
        help='Component to debug (default: all)'
    )
    debug_parser.add_argument(
        '--check',
        choices=['network', 'config', 'data', 'all'],
        default='all',
        help='Check type (default: all)'
    )
    
    return parser


def handle_validate(args):
    """Handle validate command"""
    print_header(f"Validating {args.config_file}")
    
    if not args.config_file.exists():
        print_error(f"File not found: {args.config_file}")
        return 1
    
    validator = ConfigValidator()
    
    # Auto-detect type if needed
    if args.type == 'auto':
        from biff_agents_core.config.xml_parser import BIFFXMLParser
        parser = BIFFXMLParser()
        try:
            root = parser.parse_config(args.config_file)
            config_type = parser.get_component_type(root).lower()
        except Exception as e:
            print_error(f"Could not auto-detect type: {e}")
            return 1
    else:
        config_type = args.type
    
    # Validate based on type
    try:
        if config_type == 'minion':
            result = validator.validate_minion_config(args.config_file)
        elif config_type == 'oscar':
            result = validator.validate_oscar_config(args.config_file)
        elif config_type == 'marvin':
            result = validator.validate_marvin_config(args.config_file)
        else:
            print_error(f"Unknown configuration type: {config_type}")
            return 1
        
        print(result)
        
        return 0 if result.valid else 1
        
    except Exception as e:
        print_error(f"Validation failed: {e}")
        return 1


def handle_quickstart(args):
    """Handle quickstart command"""
    print_header("Quick Start Orchestrator")
    print_info("This feature is under development")
    print_info(f"Output directory: {args.directory}")
    print_info(f"Preset: {args.preset}")
    return 0


def handle_collector(args):
    """Handle collector command"""
    print_header("Minion Collector Builder")
    print_info("This feature is under development")
    print_info(f"Config file: {args.config_file}")
    return 0


def handle_gui(args):
    """Handle gui command"""
    print_header("Marvin GUI Composer")
    print_info("This feature is under development")
    print_info(f"Config file: {args.config_file}")
    return 0


def handle_oscar(args):
    """Handle oscar command"""
    print_header("Oscar Routing Configurator")
    print_info("This feature is under development")
    print_info(f"Config file: {args.config_file}")
    return 0


def handle_debug(args):
    """Handle debug command"""
    print_header("BIFF Debugging Agent")
    print_info("This feature is under development")
    print_info(f"Component: {args.component}")
    print_info(f"Check: {args.check}")
    return 0


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Route to command handlers
    handlers = {
        'validate': handle_validate,
        'quickstart': handle_quickstart,
        'collector': handle_collector,
        'gui': handle_gui,
        'oscar': handle_oscar,
        'debug': handle_debug,
    }
    
    handler = handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        print_error(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
