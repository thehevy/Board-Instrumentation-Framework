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
from biff_agents_core.utils.collector_discovery import CollectorDiscovery
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
    return 0 if result['success'] else 1


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
