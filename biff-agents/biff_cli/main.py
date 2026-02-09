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
from biff_agents_core.utils.build_orchestrator import BuildOrchestrator, MarvinLauncher
from biff_agents_core.utils.cli_helpers import (
    print_header, print_success, print_error, print_info, print_warning,
    confirm_action
)
from biff_agents_core.utils.environment_validator import EnvironmentValidator
from biff_agents_core.utils.setup_wizard import SetupWizard
from biff_agents_core.utils.collector_discovery import CollectorDiscovery
from biff_agents_core.builders.collector_builder import CollectorWizard
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
        help='Minion Collector Builder - Discover and manage collectors'
    )
    collector_subparsers = collector_parser.add_subparsers(dest='collector_action', help='Collector actions')
    
    # collector list
    list_parser = collector_subparsers.add_parser('list', help='List available collectors')
    list_parser.add_argument(
        '-c', '--category',
        help='Filter by category (system, containers, monitoring, testing, etc.)'
    )
    list_parser.add_argument(
        '--biff-root',
        type=Path,
        help='Path to BIFF installation (default: auto-detect)'
    )
    
    # collector info
    info_parser = collector_subparsers.add_parser('info', help='Show detailed collector information')
    info_parser.add_argument(
        'name',
        help='Collector name (e.g., CPU, RandomVal, Docker_Stats)'
    )
    info_parser.add_argument(
        '--biff-root',
        type=Path,
        help='Path to BIFF installation (default: auto-detect)'
    )
    
    # collector search
    search_parser = collector_subparsers.add_parser('search', help='Search collectors by keyword')
    search_parser.add_argument(
        'query',
        nargs='?',
        help='Search query (searches names, descriptions, functions)'
    )
    search_parser.add_argument(
        '--category',
        help='Filter by category (e.g., system, containers, monitoring)'
    )
    search_parser.add_argument(
        '--dependency',
        help='Filter by required dependency (e.g., psutil, docker)'
    )
    search_parser.add_argument(
        '--function',
        help='Filter collectors with function name (partial match)'
    )
    search_parser.add_argument(
        '--min-functions',
        type=int,
        help='Filter collectors with at least N functions'
    )
    search_parser.add_argument(
        '--regex',
        help='Search using regular expression pattern'
    )
    search_parser.add_argument(
        '--search-in',
        choices=['name', 'description', 'functions', 'all'],
        default='all',
        help='Where to search with --regex (default: all)'
    )
    search_parser.add_argument(
        '--max-results',
        type=int,
        default=10,
        help='Maximum number of results for full-text search (default: 10)'
    )
    search_parser.add_argument(
        '--exact',
        action='store_true',
        help='Require exact function name match with --function'
    )
    search_parser.add_argument(
        '--biff-root',
        type=Path,
        help='Path to BIFF installation (default: auto-detect)'
    )
    
    # collector test
    test_parser = collector_subparsers.add_parser('test', help='Test a collector with sample parameters')
    test_parser.add_argument(
        'name',
        help='Collector name (e.g., RandomVal, Timer)'
    )
    test_parser.add_argument(
        'function',
        nargs='?',
        help='Function to test (default: first function)'
    )
    test_parser.add_argument(
        'params',
        nargs='*',
        help='Parameters to pass to function'
    )
    test_parser.add_argument(
        '--biff-root',
        type=Path,
        help='Path to BIFF installation (default: auto-detect)'
    )
    
    # collector template
    template_parser = collector_subparsers.add_parser('template', help='Generate XML configuration templates')
    template_parser.add_argument(
        'name',
        help='Collector name (e.g., RandomVal, CPU)'
    )
    template_parser.add_argument(
        'function',
        nargs='?',
        help='Function name (default: first function)'
    )
    template_parser.add_argument(
        '--id',
        dest='collector_id',
        help='Custom collector ID (default: name.function)'
    )
    template_parser.add_argument(
        '--frequency',
        type=int,
        default=1000,
        help='Collection frequency in milliseconds (default: 1000)'
    )
    template_parser.add_argument(
        '--all-params',
        action='store_true',
        help='Include all parameters with defaults'
    )
    template_parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate the generated template'
    )
    template_parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file path (default: stdout)'
    )
    template_parser.add_argument(
        '--biff-root',
        type=Path,
        help='Path to BIFF installation (default: auto-detect)'
    )
    
    # collector namespace
    namespace_parser = collector_subparsers.add_parser('namespace', help='Generate complete namespace configuration')
    namespace_parser.add_argument(
        'name',
        help='Namespace name'
    )
    namespace_parser.add_argument(
        '--collectors',
        nargs='+',
        help='Collectors in format "CollectorName:FunctionName" (e.g., CPU:GetCPU_Percentage)'
    )
    namespace_parser.add_argument(
        '--ip',
        default='localhost',
        help='Target connection IP (default: localhost)'
    )
    namespace_parser.add_argument(
        '--port',
        type=int,
        default=5100,
        help='Target connection port (default: 5100)'
    )
    namespace_parser.add_argument(
        '--frequency',
        type=int,
        default=1000,
        help='Default frequency in milliseconds (default: 1000)'
    )
    namespace_parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file path (default: stdout)'
    )
    namespace_parser.add_argument(
        '--biff-root',
        type=Path,
        help='Path to BIFF installation (default: auto-detect)'
    )
    
    # collector create
    create_parser = collector_subparsers.add_parser('create', help='Create new collector with interactive wizard')
    create_parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output directory for collector file (default: current directory)'
    )
    create_parser.add_argument(
        '--config',
        type=Path,
        help='MinionConfig.xml to update (optional)'
    )
    create_parser.add_argument(
        '--no-config-update',
        action='store_true',
        help='Do not update MinionConfig.xml'
    )
    
    # modifier create
    modifier_parser = collector_subparsers.add_parser('modifier', help='Create bulk regex modifier for pattern-based transformations')
    modifier_parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output directory for modifier XML (default: current directory)'
    )
    
    # aggregate create
    aggregate_parser = collector_subparsers.add_parser('aggregate', help='Create aggregate collector using Repeat operator')
    aggregate_parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output directory for aggregate XML (default: current directory)'
    )
    
    # externalfile create
    externalfile_parser = collector_subparsers.add_parser('externalfile', help='Create parameterized reusable config with ExternalFile pattern')
    externalfile_parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output directory for generated files (default: current directory)'
    )
    
    # networkstats create
    networkstats_parser = collector_subparsers.add_parser('networkstats', help='Create simplified network monitoring configuration')
    networkstats_parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output directory for network stats XML (default: current directory)'
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
    oscar_subparsers = oscar_parser.add_subparsers(dest='oscar_action', help='Oscar actions')
    
    # oscar generate
    oscar_gen_parser = oscar_subparsers.add_parser('generate', help='Generate Oscar config from Minion config')
    oscar_gen_parser.add_argument(
        '--from-minion',
        type=Path,
        required=True,
        help='Path to MinionConfig.xml'
    )
    oscar_gen_parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output Oscar config file (default: stdout)'
    )
    oscar_gen_parser.add_argument(
        '--oscar-id',
        default='Oscar',
        help='Oscar instance ID (default: Oscar)'
    )
    oscar_gen_parser.add_argument(
        '--marvin-count',
        type=int,
        default=1,
        help='Number of Marvin instances (default: 1)'
    )
    oscar_gen_parser.add_argument(
        '--marvin-ips',
        nargs='+',
        help='Marvin IP addresses (default: localhost)'
    )
    oscar_gen_parser.add_argument(
        '--per-namespace',
        action='store_true',
        help='Generate separate Oscar config per namespace'
    )
    
    # oscar validate
    oscar_val_parser = oscar_subparsers.add_parser('validate', help='Validate Minion to Oscar routing')
    oscar_val_parser.add_argument(
        '--minion',
        type=Path,
        required=True,
        help='Path to MinionConfig.xml'
    )
    oscar_val_parser.add_argument(
        '--oscar',
        type=Path,
        required=True,
        help='Path to OscarConfig.xml'
    )
    
    # oscar analyze
    oscar_analyze_parser = oscar_subparsers.add_parser('analyze', help='Analyze Minion namespaces')
    oscar_analyze_parser.add_argument(
        '--minion',
        type=Path,
        required=True,
        help='Path to MinionConfig.xml'
    )
    oscar_analyze_parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    
    # oscar deploy-guide
    oscar_deploy_parser = oscar_subparsers.add_parser('deploy-guide', help='Generate deployment guide')
    oscar_deploy_parser.add_argument(
        '--minion',
        type=Path,
        required=True,
        help='Path to MinionConfig.xml'
    )
    oscar_deploy_parser.add_argument(
        '--oscar',
        type=Path,
        help='Path to existing OscarConfig.xml (will generate if not provided)'
    )
    oscar_deploy_parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output markdown file (default: stdout)'
    )
    oscar_deploy_parser.add_argument(
        '--marvin-count',
        type=int,
        default=1,
        help='Number of Marvin instances (default: 1)'
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
        biff_root=biff_root,
        check_gradle=True  # Check Gradle for Marvin builds
    )
    
    # Print validation summary
    for info_msg in validator.info:
        print_info(info_msg)
    
    if validator.warnings:
        print()
        for warning in validator.warnings:
            print_warning(warning)
    
    # Check for missing Python packages and offer to install
    if results.get("python_packages") and results["python_packages"]["missing"]:
        print()
        missing = results["python_packages"]["missing"]
        print_warning(f"{len(missing)} optional Python package(s) not installed:")
        for pkg in missing:
            print(f"  • {pkg['name']}: {pkg['purpose']}")
        print()
        
        if confirm_action("Install missing packages now?", default=True):
            package_names = " ".join(pkg["name"] for pkg in missing)
            print_info(f"Installing: {package_names}")
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install"] + [pkg["name"] for pkg in missing],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print_success("✓ Packages installed successfully")
                else:
                    print_warning("⚠ Some packages may have failed to install")
                    print_info(f"You can install them manually: pip install {package_names}")
            except Exception as e:
                print_error(f"✗ Installation failed: {e}")
                print_info(f"Install manually: pip install {package_names}")
        else:
            print_info("Skipping package installation. Some collectors may not work.")
        print()
    
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
            
            # Step 4: Offer to build Marvin
            build_marvin = False
            if results.get("java") and results["java"]["sufficient"] and results.get("gradle") and results["gradle"]["installed"]:
                if config.get("use_existing") and config.get("biff_root"):
                    if confirm_action("Build Marvin now? (This will take 1-3 minutes)", default=True):
                        build_marvin = True
                        print()
                        print_header("Building Marvin")
                        print()
                        
                        orchestrator = BuildOrchestrator(config["biff_root"])
                        
                        # Check if build is actually needed
                        if orchestrator.is_build_needed():
                            print_info("Building Marvin and dependencies...")
                            result = orchestrator.execute(verbose=True)
                            
                            if result.success:
                                print()
                                print_success("✓ Marvin build completed successfully!")
                                jar_path = orchestrator.get_marvin_jar_path()
                                print_info(f"JAR location: {jar_path}")
                            else:
                                print()
                                print_error(f"✗ Marvin build failed: {result.message}")
                                if result.error:
                                    print_info("Error details:")
                                    print(result.error[:500])
                                build_marvin = False
                        else:
                            print_info("Marvin JAR already up-to-date - skipping build")
                            print_success("✓ Marvin ready")
            
            # Step 5: Offer to launch components
            if build_marvin or (config.get("use_existing") and config.get("biff_root")):
                print()
                if confirm_action("Start all components now?", default=True):
                    print()
                    print_header("Starting BIFF Components")
                    print()
                    
                    # Start Oscar
                    print_info("[1/3] Starting Oscar (data broker)...")
                    oscar_path = Path(config["biff_root"]) / "Oscar"
                    oscar_script = oscar_path / "start_oscar.bat" if platform.system() == "Windows" else oscar_path / "start_oscar.sh"
                    
                    try:
                        import subprocess
                        if oscar_script.exists():
                            subprocess.Popen([str(oscar_script), str(oscar_file)], cwd=str(oscar_path))
                            print_success("  ✓ Oscar started in background")
                        else:
                            # Fallback to direct Oscar.py launch
                            subprocess.Popen([sys.executable, "Oscar.py", "-c", str(oscar_file)], cwd=str(oscar_path))
                            print_success("  ✓ Oscar started")
                        
                        import time
                        time.sleep(2)
                    except Exception as e:
                        print_warning(f"  ⚠ Could not start Oscar: {e}")
                    
                    # Start Minion
                    print_info("[2/3] Starting Minion (data collector)...")
                    minion_path = Path(config["biff_root"]) / "Minion"
                    
                    try:
                        subprocess.Popen([sys.executable, "Minion.py", "-c", str(minion_file)], cwd=str(minion_path))
                        print_success("  ✓ Minion started")
                        time.sleep(2)
                    except Exception as e:
                        print_warning(f"  ⚠ Could not start Minion: {e}")
                    
                    # Start Marvin
                    if build_marvin and results["java"]["sufficient"]:
                        print_info("[3/3] Starting Marvin (GUI)...")
                        launcher = MarvinLauncher(config["biff_root"])
                        success, message = launcher.launch(str(marvin_files['application']), background=False)
                        
                        if success:
                            print_success("  ✓ Marvin started")
                        else:
                            print_warning(f"  ⚠ Could not start Marvin: {message}")
                    else:
                        print_info("[3/3] Skipping Marvin launch (build not completed or Java not available)")
                    
                    print()
                    print_success("✓ Quick start complete!")
                    return 0
            
            print()
            print_info("Quick Start - Use launcher script:")
            import platform
            if platform.system() == "Windows":
                print_info("  cd scripts && start_all.bat")
            else:
                print_info("  cd scripts && ./start_all.sh")
            print()
            print_info("Or start components manually:")
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
    
    # Auto-detect or use provided BIFF root
    biff_root = getattr(args, 'biff_root', None)
    if not biff_root:
        # Try to find BIFF installation
        current = Path.cwd()
        while current != current.parent:
            if (current / 'Minion' / 'Collectors').exists():
                biff_root = current
                break
            current = current.parent
        
        if not biff_root:
            print_error("Could not find BIFF installation")
            print_info("Please specify --biff-root or run from within BIFF directory")
            return 1
    
    # Initialize collector discovery
    try:
        discovery = CollectorDiscovery(biff_root)
    except Exception as e:
        print_error(f"Failed to initialize collector discovery: {e}")
        return 1
    
    # Route to subcommands
    action = getattr(args, 'collector_action', None)
    
    if not action:
        print_error("No action specified")
        print_info("Usage: biff collector {list|info|search}")
        return 1
    
    if action == 'list':
        return handle_collector_list(args, discovery)
    elif action == 'info':
        return handle_collector_info(args, discovery)
    elif action == 'search':
        return handle_collector_search(args, discovery)
    elif action == 'test':
        return handle_collector_test(args, discovery)
    elif action == 'template':
        return handle_collector_template(args, discovery)
    elif action == 'namespace':
        return handle_collector_namespace(args, discovery)
    elif action == 'create':
        return handle_collector_create(args)
    elif action == 'modifier':
        return handle_modifier_create(args)
    elif action == 'aggregate':
        return handle_aggregate_create(args)
    elif action == 'externalfile':
        return handle_externalfile_create(args)
    elif action == 'networkstats':
        return handle_networkstats_create(args)
    else:
        print_error(f"Unknown action: {action}")
        return 1


def handle_collector_list(args, discovery):
    """Handle collector list subcommand"""
    category = getattr(args, 'category', None)
    
    if category:
        print_header(f"Collectors in category: {category}")
        collectors = discovery.get_by_category(category)
    else:
        print_header("Available Collectors")
        collectors = discovery.list_collectors()
    
    if not collectors:
        if category:
            print_warning(f"No collectors found in category '{category}'")
            print_info(f"Available categories: {', '.join(discovery.get_categories())}")
        else:
            print_warning("No collectors found")
        return 0
    
    # Group by category
    by_category = {}
    for collector in collectors:
        if collector.category not in by_category:
            by_category[collector.category] = []
        by_category[collector.category].append(collector)
    
    # Print by category
    for cat in sorted(by_category.keys()):
        print()
        print_info(f"━━━ {cat.upper()} ━━━")
        for collector in sorted(by_category[cat], key=lambda c: c.name):
            funcs = len(collector.functions)
            func_text = f"{funcs} function{'s' if funcs != 1 else ''}"
            desc = collector.description[:60] + "..." if len(collector.description) > 60 else collector.description
            print(f"  • {collector.name:25} ({func_text:12}) - {desc}")
    
    print()
    print_success(f"Found {len(collectors)} collector{'s' if len(collectors) != 1 else ''}")
    if not category:
        print_info(f"Categories: {', '.join(sorted(discovery.get_categories()))}")
        print_info("Use 'biff collector list -c <category>' to filter by category")
    
    return 0


def handle_collector_info(args, discovery):
    """Handle collector info subcommand"""
    name = args.name
    
    print_header(f"Collector: {name}")
    
    collector = discovery.get_collector(name)
    if not collector:
        print_error(f"Collector '{name}' not found")
        print_info("Use 'biff collector list' to see available collectors")
        return 1
    
    # Basic info
    print()
    print_info(f"Category:    {collector.category}")
    print_info(f"File:        {collector.file_path.name}")
    print_info(f"Functions:   {len(collector.functions)}")
    
    # Dependencies with installation status
    if collector.dependencies:
        dep_status = discovery.check_dependencies(name)
        deps_str = []
        for dep in sorted(collector.dependencies):
            status = dep_status.get(dep, False)
            symbol = "✓" if status else "✗"
            deps_str.append(f"{dep} {symbol}")
        print_info(f"Dependencies: {', '.join(deps_str)}")
        
        # Show install command if missing dependencies
        missing = discovery.get_missing_dependencies(name)
        if missing:
            print()
            print_warning(f"Missing dependencies: {', '.join(missing)}")
            print_info(f"Install: {discovery.suggest_install_command(missing)}")
    
    # Description
    if collector.description:
        print()
        print_info("Description:")
        print(f"  {collector.description}")
    
    # Functions
    if collector.functions:
        print()
        print_info(f"Available Functions ({len(collector.functions)}):")
        for func in collector.functions:
            print(f"\n  • {func.name}()")
            if func.description:
                desc_lines = func.description.split('\n')
                for line in desc_lines[:3]:  # Show first 3 lines
                    print(f"    {line.strip()}")
                if len(desc_lines) > 3:
                    print(f"    ...")
            
            if func.parameters:
                print(f"    Parameters:")
                for param in func.parameters:
                    param_str = f"      - {param.name}"
                    if param.type_hint:
                        param_str += f": {param.type_hint}"
                    if param.default:
                        param_str += f" = {param.default}"
                    print(param_str)
                    if param.description:
                        print(f"        {param.description}")
            
            # Show example if available
            if func.example:
                print(f"    Example:")
                for line in func.example.split('\n')[:5]:  # Show first 5 lines
                    print(f"      {line}")
                if len(func.example.split('\n')) > 5:
                    print(f"      ...")
    
    # Usage example
    print()
    print_info("Usage Example:")
    print(f"""  <Collector ID="my_{name.lower()}_collector">
    <Executable>Collectors/{collector.file_path.name}</Executable>""")
    if collector.functions:
        func = collector.functions[0]
        print(f"    <Param>{func.name}</Param>")
        if func.parameters:
            for param in func.parameters[:2]:  # Show first 2 params
                default = param.default or "value"
                print(f"    <Param>{default}</Param>")
    print(f"  </Collector>")
    
    print()
    return 0


def handle_collector_search(args, discovery):
    """Handle collector search subcommand"""
    
    # Determine search mode
    if args.regex:
        # Regex search
        print_header(f"Regex Search: {args.regex}")
        print_info(f"Searching in: {args.search_in}")
        print()
        
        try:
            results = discovery.regex_search(args.regex, search_in=args.search_in)
        except ValueError as e:
            print_error(str(e))
            return 1
            
    elif args.category or args.dependency or args.function or args.min_functions:
        # Advanced filter search
        filters = []
        if args.category:
            filters.append(f"category={args.category}")
        if args.dependency:
            filters.append(f"dependency={args.dependency}")
        if args.function:
            filters.append(f"function={args.function}")
        if args.min_functions:
            filters.append(f"min_functions={args.min_functions}")
        
        print_header(f"Advanced Search")
        print_info(f"Filters: {', '.join(filters)}")
        print()
        
        results = discovery.search_collectors(
            by_category=args.category,
            by_dependency=args.dependency,
            has_function=args.function,
            min_functions=args.min_functions
        )
        
    elif args.function:
        # Function name search
        print_header(f"Function Search: {args.function}")
        print_info(f"Match type: {'exact' if args.exact else 'partial'}")
        print()
        
        results = discovery.search_by_function(args.function, exact=args.exact)
        
    elif args.query:
        # Full-text search
        print_header(f"Searching for: {args.query}")
        print()
        
        scored_results = discovery.full_text_search(args.query, max_results=args.max_results)
        
        if not scored_results:
            print_warning(f"No collectors found matching '{args.query}'")
            print_info("Try searching for keywords like: cpu, docker, network, random, timer")
            return 0
        
        print_success(f"Found {len(scored_results)} matching collector{'s' if len(scored_results) != 1 else ''}")
        print()
        
        for collector, score in scored_results:
            funcs = len(collector.functions)
            func_text = f"{funcs} function{'s' if funcs != 1 else ''}"
            
            # Show relevance score
            score_bar = "█" * int(score / 2) + "░" * (10 - int(score / 2))
            print(f"  [{score_bar}] {score:5.1f}  {collector.name:20} [{collector.category:12}] ({func_text})")
            
            desc = collector.description[:70] + "..." if len(collector.description) > 70 else collector.description
            if desc:
                print(f"         {desc}")
            
            # Highlight matching functions
            matching_funcs = []
            for func in collector.functions:
                for keyword in args.query.lower().split():
                    if keyword in func.name.lower():
                        matching_funcs.append(func.name)
                        break
            
            if matching_funcs:
                print(f"         Functions: {', '.join(matching_funcs[:3])}")
                if len(matching_funcs) > 3:
                    print(f"                    ... and {len(matching_funcs) - 3} more")
            
            print()
        
        print_info(f"Use 'biff collector info <name>' for detailed information")
        return 0
    else:
        print_error("No search criteria specified")
        print_info("Use --help to see available search options")
        print_info("Examples:")
        print_info("  biff collector search 'cpu usage'")
        print_info("  biff collector search --category system")
        print_info("  biff collector search --function GetUsage")
        print_info("  biff collector search --regex '^Docker.*'")
        return 1
    
    # Handle results for non-full-text searches
    if not results:
        print_warning("No collectors found matching criteria")
        print_info("Try different filters or use 'biff collector list' to see all collectors")
        return 0
    
    print_success(f"Found {len(results)} matching collector{'s' if len(results) != 1 else ''}")
    print()
    
    for collector in results:
        funcs = len(collector.functions)
        func_text = f"{funcs} function{'s' if funcs != 1 else ''}"
        print(f"  • {collector.name:25} [{collector.category:12}] ({func_text:12})")
        desc = collector.description[:70] + "..." if len(collector.description) > 70 else collector.description
        if desc:
            print(f"    {desc}")
        
        # Show matching functions if function filter was used
        if args.function:
            matching_funcs = [f.name for f in collector.functions if args.function.lower() in f.name.lower()]
            if matching_funcs:
                print(f"    Matching functions: {', '.join(matching_funcs[:5])}")
        
        print()
    
    print_info(f"Use 'biff collector info <name>' for detailed information")
    
    return 0


def handle_collector_test(args, discovery):
    """Handle collector test subcommand"""
    name = args.name
    function = getattr(args, 'function', None)
    params = getattr(args, 'params', [])
    
    print_header(f"Testing Collector: {name}")
    
    # Get collector info
    collector = discovery.get_collector(name)
    if not collector:
        print_error(f"Collector '{name}' not found")
        print_info("Use 'biff collector list' to see available collectors")
        return 1
    
    # Show what we're testing
    print()
    if function:
        print_info(f"Function: {function}")
    else:
        print_info(f"Function: {collector.functions[0].name if collector.functions else 'N/A'} (default)")
    
    if params:
        print_info(f"Parameters: {' '.join(params)}")
    else:
        print_info("Parameters: (none)")
    
    # Check dependencies first
    missing = discovery.get_missing_dependencies(name)
    if missing:
        print()
        print_error(f"Missing dependencies: {', '.join(missing)}")
        print_info(f"Install: {discovery.suggest_install_command(missing)}")
        return 1
    
    # Run test
    print()
    print_info("Running collector...")
    print()
    
    result = discovery.test_collector(name, function, params)
    
    if result['success']:
        print_success("✓ Collector executed successfully")
        print()
        if result['output']:
            print_info("Output:")
            for line in result['output'].strip().split('\n'):
                print(f"  {line}")
    else:
        print_error(f"✗ Collector failed (exit code: {result['exit_code']})")
        print()
        if result['error']:
            print_info("Error:")
            for line in result['error'].strip().split('\n')[:10]:  # Show first 10 lines
                print(f"  {line}")
            if len(result['error'].strip().split('\n')) > 10:
                print(f"  ... ({len(result['error'].strip().split('\n')) - 10} more lines)")
        if result['output']:
            print()
            print_info("Output:")
            for line in result['output'].strip().split('\n')[:10]:
                print(f"  {line}")
    
    print()
    return 0


def handle_collector_template(args, discovery):
    """Handle collector template generation subcommand"""
    name = args.name
    function = getattr(args, 'function', None)
    collector_id = getattr(args, 'collector_id', None)
    frequency = args.frequency
    all_params = args.all_params
    validate = args.validate
    output_file = getattr(args, 'output', None)
    
    print_header(f"Generating Template: {name}")
    
    # Generate XML template
    try:
        xml = discovery.generate_collector_xml(
            name,
            function_name=function,
            collector_id=collector_id,
            frequency=frequency,
            include_all_params=all_params
        )
    except ValueError as e:
        print_error(str(e))
        return 1
    
    print()
    print_success("Template generated successfully")
    print()
    
    # Validate if requested
    if validate:
        valid, errors = discovery.validate_collector_config(f'<root>{xml}</root>')
        if valid:
            print_success("✓ Template validation passed")
        else:
            print_error("✗ Template validation failed:")
            for error in errors:
                print(f"  - {error}")
        print()
    
    # Output to file or stdout
    if output_file:
        try:
            output_file.write_text(xml, encoding='utf-8')
            print_success(f"Template written to: {output_file}")
        except Exception as e:
            print_error(f"Failed to write template: {e}")
            return 1
    else:
        print_info("Generated XML:")
        print()
        for line in xml.split('\n'):
            print(f"  {line}")
    
    print()
    print_info("Usage tips:")
    print("  - Copy this XML into a <Namespace> section of your Minion config")
    print("  - Replace <!-- comments --> with actual parameter values")
    print("  - Adjust Frequency as needed for your use case")
    
    return 0


def handle_collector_namespace(args, discovery):
    """Handle namespace configuration generation subcommand"""
    name = args.name
    collectors_arg = getattr(args, 'collectors', [])
    target_ip = args.ip
    target_port = args.port
    frequency = args.frequency
    output_file = getattr(args, 'output', None)
    
    print_header(f"Generating Namespace: {name}")
    
    if not collectors_arg:
        print_error("No collectors specified")
        print_info("Use --collectors to specify collectors in format CollectorName:FunctionName")
        print_info("Example: --collectors CPU:GetCPU_Percentage Memory:GetMemory")
        return 1
    
    # Parse collectors
    collectors = []
    for spec in collectors_arg:
        if ':' not in spec:
            print_error(f"Invalid collector spec: {spec}")
            print_info("Format should be: CollectorName:FunctionName")
            return 1
        
        parts = spec.split(':', 1)
        collectors.append((parts[0], parts[1]))
    
    print()
    print_info(f"Target: {target_ip}:{target_port}")
    print_info(f"Default frequency: {frequency}ms")
    print_info(f"Collectors: {len(collectors)}")
    for coll_name, func_name in collectors:
        print(f"  - {coll_name}.{func_name}")
    print()
    
    # Generate namespace config
    try:
        xml = discovery.generate_namespace_config(
            name,
            collectors,
            target_ip=target_ip,
            target_port=target_port,
            default_frequency=frequency
        )
    except Exception as e:
        print_error(f"Failed to generate namespace: {e}")
        return 1
    
    print_success("Namespace configuration generated successfully")
    print()
    
    # Output to file or stdout
    if output_file:
        try:
            output_file.write_text(xml, encoding='utf-8')
            print_success(f"Configuration written to: {output_file}")
        except Exception as e:
            print_error(f"Failed to write configuration: {e}")
            return 1
    else:
        print_info("Generated XML:")
        print()
        for line in xml.split('\n'):
            print(f"  {line}")
    
    print()
    print_info("Next steps:")
    print("  1. Copy this XML into your Minion configuration file")
    print("  2. Replace parameter comments with actual values")
    print("  3. Test with: biff collector test <name> <function>")
    print("  4. Run Minion: python Minion.py -c YourConfig.xml")
    
    return 0


def handle_modifier_create(args):
    """Handle modifier create command - generates bulk regex modifier XML"""
    from biff_agents_core.builders.modifier_builder import ModifierWizard
    from pathlib import Path
    
    print_header("BIFF Bulk Regex Modifier Generator")
    
    try:
        # Run interactive wizard
        wizard = ModifierWizard()
        responses = wizard.run_wizard()
        
        # Generate modifier XML
        print("\n" + "="*70)
        print("  Generating Modifier XML...")
        print("="*70)
        
        xml = wizard.generate_modifier_xml(responses)
        
        # Determine output path
        output_dir = args.output if args.output else Path.cwd()
        output_dir = Path(output_dir)
        
        # Create filename from pattern
        pattern = responses['pattern']
        # Sanitize pattern for filename
        filename = pattern.replace('(_*)', '_wildcard').replace('(*)', '_wildcard')
        filename = filename.replace('.', '_').replace('/', '_').replace('\\', '_')
        filename = 'Modifier_' + filename + '.xml'
        filename = ''.join(c for c in filename if c.isalnum() or c in ('_', '.', '-'))
        output_file = output_dir / filename
        
        # Save modifier
        wizard.save_modifier(xml, output_file)
        
        print()
        print_success(f"✓ Modifier XML created: {output_file}")
        
        # Show summary
        print()
        print_info("Modifier Summary:")
        print(f"  • Pattern: {responses['pattern']}")
        print(f"  • Operation: {responses['operation']}")
        if responses['operation'] == 'normalize':
            print(f"  • Factor: {responses['normalize_factor']}")
            print(f"  • Description: {responses.get('normalize_description', 'N/A')}")
        print(f"  • Precision: {responses['precision']}")
        print(f"  • Send on Change: {'Yes' if responses.get('send_on_change') else 'No'}")
        print(f"  • Suppress Send: {'Yes' if responses.get('do_not_send') else 'No'}")
        
        # Show generated XML
        print()
        print_info("Generated XML:")
        print()
        for line in xml.split('\n'):
            print(f"  {line}")
        
        # Show usage notes
        print()
        print_info(wizard.get_usage_notes(responses))
        
        print()
        print_info("Next Steps:")
        print("  1. Open your MinionConfig.xml")
        print("  2. Add this <Modifier> XML inside the <Namespace>")
        print("  3. Place AFTER the collectors that generate these metrics")
        print("  4. Restart Minion to apply transformations")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n❌ Modifier generation cancelled")
        return 1
    except Exception as e:
        print()
        print_error(f"✗ Failed to create modifier: {e}")
        import traceback
        traceback.print_exc()
        return 1


def handle_aggregate_create(args):
    """Handle aggregate collector create command"""
    from biff_agents_core.builders.aggregate_builder import run_wizard
    
    try:
        # Determine output directory
        output_dir = args.output if hasattr(args, 'output') and args.output else Path.cwd()
        
        # Run the wizard
        result = run_wizard(str(output_dir))
        return result
        
    except KeyboardInterrupt:
        print("\n\n❌ Aggregate generation cancelled")
        return 1
    except Exception as e:
        print()
        print_error(f"✗ Failed to create aggregate: {e}")
        import traceback
        traceback.print_exc()
        return 1


def handle_externalfile_create(args):
    """Handle external file template create command"""
    from biff_agents_core.builders.externalfile_builder import run_wizard
    
    try:
        # Determine output directory
        output_dir = args.output if hasattr(args, 'output') and args.output else Path.cwd()
        
        # Run the wizard
        result = run_wizard(str(output_dir))
        return result
        
    except KeyboardInterrupt:
        print("\n\n❌ ExternalFile generation cancelled")
        return 1
    except Exception as e:
        print()
        print_error(f"✗ Failed to create ExternalFile: {e}")
        import traceback
        traceback.print_exc()
        return 1


def handle_networkstats_create(args):
    """Handle network stats create command"""
    from biff_agents_core.builders.networkstats_builder import run_wizard
    
    try:
        # Determine output directory
        output_dir = args.output if hasattr(args, 'output') and args.output else Path.cwd()
        
        # Run the wizard
        result = run_wizard(str(output_dir))
        return result
        
    except KeyboardInterrupt:
        print("\n\n❌ Network stats generation cancelled")
        return 1
    except Exception as e:
        print()
        print_error(f"✗ Failed to create network stats: {e}")
        import traceback
        traceback.print_exc()
        return 1



def handle_collector_create(args):
    """Handle collector create command"""
    print_header("Minion Collector Builder - Create New Collector")
    
    try:
        # Run interactive wizard
        wizard = CollectorWizard()
        responses = wizard.run_wizard()
        
        # Check if this is a DynamicCollector (XML-only) or plugin_framework
        is_dynamic_collector = responses.get('source_type') == 'dynamic_file'
        is_plugin_framework = responses.get('source_type') == 'plugin_framework'
        
        # Generate collector code/config
        print("\n" + "="*70)
        if is_dynamic_collector:
            print("  Generating DynamicCollector XML...")
        else:
            print("  Generating Collector Code...")
        print("="*70)
        
        code = wizard.generate_collector(responses)
        
        # Determine output path
        output_dir = args.output if args.output else Path.cwd()
        output_dir = Path(output_dir)
        
        # For DynamicCollector, save as XML snippet
        if is_dynamic_collector:
            filename = 'DynamicCollector_' + responses['metric_prefix'].replace('.', '_') + '.xml'
            output_file = output_dir / filename
            wizard.save_collector(code, output_file)
            
            print()
            print_success(f"✓ DynamicCollector XML created: {output_file}")
            
            # Show summary
            print()
            print_info("DynamicCollector Summary:")
            print(f"  • Metric Prefix: {responses['metric_prefix']}")
            print(f"  • File Path: {responses['file_path']}")
            print(f"  • Frequency: {responses['frequency_display']}")
            print(f"  • Precision: {responses['precision']}")
            print(f"  • Send on Change: {'Yes' if responses.get('send_on_change') else 'No'}")
            print()
            print_info("Usage:")
            print("  1. Add the XML to your MinionConfig.xml inside <Namespace>")
            print("  2. Create file with format: metric.name=value")
            print("  3. Minion will auto-discover and send all metrics")
            
            # Show usage notes
            template = wizard.TEMPLATES['dynamic_file']
            print()
            print_info(template.get_usage_notes())
            
        elif is_plugin_framework:
            # Plugin Framework collectors are Python files
            metric_name = responses['metric_name']
            filename = metric_name.replace(' ', '_').replace('-', '_') + '.py'
            filename = ''.join(c for c in filename if c.isalnum() or c in ('_', '.'))
            output_file = output_dir / filename
            
            # Save collector
            wizard.save_collector(code, output_file)
            
            print()
            print_success(f"✓ Plugin Framework collector created: {output_file}")
            
            # Show summary
            print()
            print_info("Plugin Framework Collector Summary:")
            print(f"  • Metric Name: {responses['metric_name']}")
            print(f"  • Entry Point: {responses.get('function_name', 'collect')}")
            print(f"  • Discovery Mode: {responses.get('discovery_mode', 'dynamic')}")
            if responses.get('discovery_mode') == 'static':
                static_ids = responses.get('static_ids', [])
                print(f"  • Collector IDs: {', '.join(static_ids[:3])}{'...' if len(static_ids) > 3 else ''} ({len(static_ids)} total)")
            print(f"  • Frequency: {responses['frequency_display']}")
            print(f"  • Output File: {output_file}")
            
            # Show XML configuration
            print()
            print_info("XML Configuration for MinionConfig.xml:")
            print()
            print(f'''<Plugin>
    <PythonFile>Collectors/{filename}</PythonFile>
    <EntryPoint>{responses.get('function_name', 'collect')}</EntryPoint>
    <!-- Optional parameters -->
    <Param>param_name=value</Param>
</Plugin>''')
            
            # Show usage notes
            template = wizard.TEMPLATES['plugin_framework']
            print()
            print_info(template.get_usage_notes())
            
        else:
            # Create filename from metric name for Python collectors
            metric_name = responses['metric_name']
            filename = metric_name.replace(' ', '_').replace('-', '_') + '.py'
            filename = ''.join(c for c in filename if c.isalnum() or c in ('_', '.'))
            output_file = output_dir / filename
            
            # Save collector
            wizard.save_collector(code, output_file)
            
            print()
            print_success(f"✓ Collector created: {output_file}")
            
            # Show summary
            print()
            print_info("Collector Summary:")
            print(f"  • Metric Name: {responses['metric_name']}")
            if 'metric_id' in responses:
                print(f"  • Metric ID: {responses['metric_id']}")
            print(f"  • Source Type: {responses['source_type']}")
            print(f"  • Frequency: {responses['frequency_display']}")
            print(f"  • Template: {responses['template_key']}")
            print(f"  • Output File: {output_file}")
        
        # Update MinionConfig.xml if requested (only for collectors with metric_id)
        # Skip for dynamic_file (XML-only) and plugin_framework (uses <Plugin> instead of <Collector>)
        if not is_dynamic_collector and not is_plugin_framework and 'metric_id' in responses and not args.no_config_update:
            config_file = args.config if args.config else None
            if not config_file:
                # Try to find MinionConfig.xml in current directory or parent
                search_paths = [
                    Path.cwd() / 'MinionConfig.xml',
                    Path.cwd().parent / 'MinionConfig.xml',
                    Path.cwd() / 'Minion' / 'MinionConfig.xml'
                ]
                for path in search_paths:
                    if path.exists():
                        config_file = path
                        break
            
            if config_file:
                print()
                if confirm_action(f"Update {config_file} with new collector?"):
                    try:
                        # Parse existing config
                        import xml.etree.ElementTree as ET
                        tree = ET.parse(config_file)
                        root = tree.getroot()
                        
                        # Find or create Namespace
                        namespace = root.find('.//Namespace')
                        if namespace is None:
                            namespace = ET.SubElement(root, 'Namespace')
                            name_elem = ET.SubElement(namespace, 'Name')
                            name_elem.text = 'Default'
                            freq_elem = ET.SubElement(namespace, 'DefaultFrequency')
                            freq_elem.text = '1000'
                            conn_elem = ET.SubElement(namespace, 'TargetConnection')
                            conn_elem.set('IP', 'localhost')
                            conn_elem.set('PORT', '5100')
                        
                        # Add Collector element
                        collector_elem = ET.SubElement(namespace, 'Collector')
                        collector_elem.set('ID', responses['metric_id'])
                        collector_elem.set('Frequency', str(responses['frequency']))
                        
                        executable_elem = ET.SubElement(collector_elem, 'Executable')
                        executable_elem.text = str(output_file)
                        
                        # Write back with proper formatting
                        from xml.dom import minidom
                        xml_str = ET.tostring(root, encoding='unicode')
                        dom = minidom.parseString(xml_str)
                        pretty_xml = dom.toprettyxml(indent='  ')
                        
                        # Remove extra blank lines
                        lines = [line for line in pretty_xml.split('\n') if line.strip()]
                        pretty_xml = '\n'.join(lines)
                        
                        with open(config_file, 'w', encoding='utf-8') as f:
                            f.write(pretty_xml)
                        
                        print_success(f"✓ Updated {config_file}")
                        
                    except Exception as e:
                        print_warning(f"Failed to update config: {e}")
                        print_info("You can manually add the collector to your MinionConfig.xml")
            else:
                print()
                print_info("No MinionConfig.xml found. You can manually add this collector:")
                print()
                if 'metric_id' in responses:
                    print(f'''  <Collector ID="{responses['metric_id']}" Frequency="{responses['frequency']}">
    <Executable>{output_file}</Executable>
  </Collector>''')
                else:
                    print("  (Plugin framework collectors use <Plugin> instead of <Collector>)")
        
        # Next steps
        print()
        print_info("Next Steps:")
        print("  1. Review the generated collector code")
        print("  2. Customize parsing logic if needed (look for TODO comments)")
        print(f"  3. Test the collector: python {output_file}")
        print("  4. Start Minion to see your metric in action")
        
        if responses.get('command'):
            print()
            print_warning("Note: Make sure the command is available in your system PATH:")
            print(f"  {responses['command'].split()[0]}")
        
        if responses.get('file_path'):
            print()
            print_warning("Note: Make sure the file path is accessible:")
            print(f"  {responses['file_path']}")
        
        return 0
        
    except KeyboardInterrupt:
        print()
        print_warning("\nCollector creation cancelled by user")
        return 0
    except Exception as e:
        print()
        print_error(f"Failed to create collector: {e}")
        import traceback
        traceback.print_exc()
        return 1


def handle_gui(args):
    """Handle gui command"""
    print_header("Marvin GUI Composer")
    print_info("This feature is under development")
    print_info(f"Config file: {args.config_file}")
    return 0


def handle_oscar(args):
    """Handle oscar command"""
    if not args.oscar_action:
        print_error("No Oscar action specified. Use: generate, validate, analyze, or deploy-guide")
        return 1
    
    from biff_agents_core.utils.minion_oscar_integration import (
        MinionOscarIntegration, MinionNamespaceAnalyzer
    )
    import json
    
    if args.oscar_action == 'generate':
        print_header("Oscar Config Generator")
        
        if not args.from_minion.exists():
            print_error(f"Minion config not found: {args.from_minion}")
            return 1
        
        integration = MinionOscarIntegration()
        
        try:
            if args.per_namespace:
                # Generate separate Oscar per namespace
                print_info(f"Generating per-namespace Oscar configs from {args.from_minion}")
                oscar_configs = integration.generate_oscar_from_minion(
                    args.from_minion,
                    marvin_ips=args.marvin_ips or ['localhost']
                )
                
                for ns_name, oscar_xml in oscar_configs.items():
                    if args.output:
                        output_file = args.output.parent / f"{args.output.stem}_{ns_name}.xml"
                        output_file.write_text(oscar_xml)
                        print_success(f"✓ Generated {output_file}")
                    else:
                        print(f"\n=== Oscar Config for Namespace: {ns_name} ===")
                        print(oscar_xml)
            else:
                # Generate unified Oscar
                print_info(f"Generating unified Oscar config from {args.from_minion}")
                oscar_xml, port_map = integration.generate_unified_oscar(
                    args.from_minion,
                    oscar_id=args.oscar_id,
                    marvin_count=args.marvin_count
                )
                
                if args.output:
                    args.output.write_text(oscar_xml)
                    print_success(f"✓ Generated {args.output}")
                    print()
                    print_info("Marvin Port Assignments:")
                    for marvin, config in port_map.items():
                        print(f"  {marvin}: {config['ip']}:{config['port']}")
                else:
                    print(oscar_xml)
                    print()
                    print_info("Marvin Port Assignments:")
                    for marvin, config in port_map.items():
                        print(f"  {marvin}: {config['ip']}:{config['port']}")
            
            return 0
            
        except ValueError as e:
            print_error(f"Configuration error: {e}")
            return 1
        except Exception as e:
            print_error(f"Failed to generate Oscar config: {e}")
            return 1
    
    elif args.oscar_action == 'validate':
        print_header("Oscar Routing Validator")
        
        if not args.minion.exists():
            print_error(f"Minion config not found: {args.minion}")
            return 1
        
        if not args.oscar.exists():
            print_error(f"Oscar config not found: {args.oscar}")
            return 1
        
        integration = MinionOscarIntegration()
        
        try:
            print_info(f"Validating {args.minion} → {args.oscar}")
            errors = integration.validate_minion_oscar_routing(args.minion, args.oscar)
            
            if not errors:
                print()
                print_success("✓ Routing validation passed!")
                print_info("  Minion target ports match Oscar incoming ports")
                print_info("  Oscar has valid target connections")
                return 0
            else:
                print()
                print_error(f"Found {len(errors)} routing error(s):")
                for i, error in enumerate(errors, 1):
                    print(f"  {i}. {error}")
                return 1
                
        except Exception as e:
            print_error(f"Validation failed: {e}")
            return 1
    
    elif args.oscar_action == 'analyze':
        print_header("Minion Namespace Analyzer")
        
        if not args.minion.exists():
            print_error(f"Minion config not found: {args.minion}")
            return 1
        
        analyzer = MinionNamespaceAnalyzer()
        
        try:
            analysis = analyzer.analyze_namespaces(args.minion)
            
            if args.json:
                print(json.dumps(analysis, indent=2))
            else:
                print()
                print_info(f"Configuration: {args.minion}")
                print()
                print(f"Namespaces: {analysis['namespace_count']}")
                print(f"Total Collectors: {analysis['total_collectors']}")
                print(f"Total Actors: {analysis.get('total_actors', 0)}")
                print(f"Avg Collectors/Namespace: {analysis.get('avg_collectors_per_namespace', 0):.1f}")
                print(f"Avg Actors/Namespace: {analysis.get('avg_actors_per_namespace', 0):.1f}")
                print()
                print_info("Target Connections:")
                for target in analysis['targets']:
                    print(f"  • {target}")
                
                if analysis['high_frequency_collectors']:
                    print()
                    print_warning(f"High-Frequency Collectors (<500ms):")
                    for hf in analysis['high_frequency_collectors']:
                        print(f"  • {hf['namespace']}.{hf['collector']}: {hf['frequency']}ms")
            
            return 0
            
        except Exception as e:
            print_error(f"Analysis failed: {e}")
            return 1
    
    elif args.oscar_action == 'deploy-guide':
        print_header("Deployment Guide Generator")
        
        if not args.minion.exists():
            print_error(f"Minion config not found: {args.minion}")
            return 1
        
        integration = MinionOscarIntegration()
        
        try:
            # Generate or use existing Oscar config
            if args.oscar and args.oscar.exists():
                print_info(f"Using existing Oscar config: {args.oscar}")
                oscar_xml = args.oscar.read_text()
                # Parse to get port map
                from biff_agents_core.utils.oscar_routing import OscarConfigParser
                parser = OscarConfigParser()
                oscar_config = parser.parse(args.oscar)
                port_map = {}
                for i, conn in enumerate(oscar_config.target_connections, 1):
                    port_map[f'Marvin{i}'] = {'ip': conn.ip, 'port': conn.port}
            else:
                print_info(f"Generating Oscar config from {args.minion}")
                oscar_xml, port_map = integration.generate_unified_oscar(
                    args.minion,
                    marvin_count=args.marvin_count
                )
            
            guide = integration.generate_deployment_guide(
                args.minion,
                oscar_xml,
                port_map
            )
            
            if args.output:
                args.output.write_text(guide)
                print_success(f"✓ Generated deployment guide: {args.output}")
            else:
                print()
                print(guide)
            
            return 0
            
        except Exception as e:
            print_error(f"Failed to generate deployment guide: {e}")
            return 1
    
    else:
        print_error(f"Unknown Oscar action: {args.oscar_action}")
        return 1


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
