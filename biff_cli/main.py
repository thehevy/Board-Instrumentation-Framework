"""
BIFF Agents CLI

Command-line interface for BIFF AI agents.
"""

import sys
import os
import argparse
from pathlib import Path

# Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from biff_agents_core.validators.config_validator import ConfigValidator
from biff_agents_core.generators.minion_generator import MinionConfigGenerator
from biff_agents_core.generators.oscar_generator import OscarConfigGenerator
from biff_agents_core.generators.marvin_generator import MarvinApplicationGenerator
from biff_agents_core.utils.cli_helpers import (
    print_header, print_success, print_error, print_info, print_warning
)
from biff_agents_core.utils.environment_validator import EnvironmentValidator
from biff_agents_core.utils.setup_wizard import SetupWizard
from pathlib import Path


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
    print_header("BIFF Quick Start Orchestrator")
    print()
    print_info("Checking your environment for BIFF prerequisites...")
    print()
    
    # Step 1: Validate environment
    validator = EnvironmentValidator()
    
    # Check for BIFF installation
    biff_root = Path.cwd()
    results = validator.validate_all(
        check_network=False,  # Network check optional for now
        biff_root=biff_root
    )
    
    # Print validation summary
    for info_msg in validator.info:
        print_info(info_msg)
    
    if validator.warnings:
        print()
        for warning in validator.warnings:
            print_warning(warning)
    
    if validator.issues:
        print()
        for issue in validator.issues:
            print_error(issue)
        
        print()
        print_error("Environment validation failed!")
        print()
        print_info("Suggested fixes:")
        fixes = validator.suggest_fixes()
        for fix in fixes:
            print(f"  {fix}")
        
        return 1
    
    print()
    print_success("✓ Environment validation passed!")
    print()
    
    # Step 2: Run interactive setup wizard
    wizard = SetupWizard(results)
    
    try:
        config = wizard.run()
        
        if config is None:
            print_warning("Setup cancelled")
            return 0
        
        # Step 3: Generate configurations
        print()
        print_header("Generating BIFF Configurations")
        print()
        
        output_dir = config["output_dir"]
        
        try:
            # Generate Minion config
            print_info("Generating Minion configuration...")
            minion_gen = MinionConfigGenerator()
            minion_file = minion_gen.generate_file(config, output_dir)
            print_success(f"  ✓ Created: {minion_file}")
            
            # Generate Oscar config
            print_info("Generating Oscar configuration...")
            oscar_gen = OscarConfigGenerator()
            oscar_file = oscar_gen.generate_file(config, output_dir)
            print_success(f"  ✓ Created: {oscar_file}")
            
            # Generate Marvin config
            print_info("Generating Marvin application...")
            marvin_gen = MarvinApplicationGenerator()
            marvin_files = marvin_gen.generate_all(config, output_dir)
            print_success(f"  ✓ Created: {marvin_files['application']}")
            print_success(f"  ✓ Created: {marvin_files['tab']}")
            print_success(f"  ✓ Created: {marvin_files['grid']}")
            
            print()
            print_success("✓ Configuration files generated successfully!")
            print()
            print_info("Generated files:")
            print(f"  - {minion_file}")
            print(f"  - {oscar_file}")
            print(f"  - {marvin_files['application']}")
            print(f"  - {marvin_files['tab']}")
            print(f"  - {marvin_files['grid']}")
            print()
            print_info("Next steps:")
            print_info("  1. Start Oscar:")
            if config.get("use_existing") and config.get("biff_root"):
                print_info(f"     cd {Path(config['biff_root']) / 'Oscar'}")
                print_info(f"     python Oscar.py -c {oscar_file}")
            else:
                print_info(f"     cd Oscar && python Oscar.py -c {oscar_file}")
            print()
            print_info("  2. Start Minion:")
            if config.get("use_existing") and config.get("biff_root"):
                print_info(f"     cd {Path(config['biff_root']) / 'Minion'}")
                print_info(f"     python Minion.py -c {minion_file}")
            else:
                print_info(f"     cd Minion && python Minion.py -c {minion_file}")
            print()
            print_info("  3. Build and start Marvin (requires Java):")
            if config.get("use_existing") and config.get("biff_root"):
                print_info(f"     cd {Path(config['biff_root']) / 'Marvin'}")
                print_info(f"     gradlew build")
                print_info(f"     java -jar build/libs/BIFF.Marvin.jar -a {marvin_files['application']}")
            else:
                print_info(f"     cd Marvin")
                print_info(f"     gradlew build")
                print_info(f"     java -jar build/libs/BIFF.Marvin.jar -a {marvin_files['application']}")
            
            return 0
            
        except Exception as e:
            print()
            print_error(f"Config generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1
        
    except KeyboardInterrupt:
        print()
        print_warning("\nSetup interrupted by user")
        return 0
    except Exception as e:
        print()
        print_error(f"Setup failed: {str(e)}")
        return 1


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
