"""
CLI for Marvin GUI Composer

Command-line interface for creating Marvin dashboard configurations.
Integrates widget builders and dashboard composers.
"""

import argparse
import sys
from pathlib import Path

from .builders.text_widget_builder import TextWidgetBuilder
from .builders.led_widget_builder import LEDWidgetBuilder
from .builders.button_widget_builder import ButtonWidgetBuilder
from .builders.gauge_widget_builder import GaugeWidgetBuilder
from .builders.chart_widget_builder import ChartWidgetBuilder
from .builders.memory_widget_builder import MemoryWidgetBuilder
from .builders.network_widget_builder import NetworkWidgetBuilder
from .builders.system_widget_builder import SystemWidgetBuilder
from .composers.quickstart_composer import QuickstartDashboardComposer
from .composers.monitoring_composer import MonitoringDashboardComposer
from .composers.performance_composer import PerformanceDashboardComposer
from .utils.minion_discovery import MinionDataSourceDiscovery


def cmd_widget(args):
    """Handle 'widget' command"""
    
    # Map widget types to builder classes
    builders = {
        'text': TextWidgetBuilder,
        'led': LEDWidgetBuilder,
        'button': ButtonWidgetBuilder,
        'gauge': GaugeWidgetBuilder,
        'chart': ChartWidgetBuilder,
        'memory': MemoryWidgetBuilder,
        'network': NetworkWidgetBuilder,
        'system': SystemWidgetBuilder,
    }
    
    if args.type not in builders:
        print(f"❌ Error: Unknown widget type '{args.type}'")
        print(f"Available types: {', '.join(builders.keys())}")
        return 1
    
    # Create builder
    builder_class = builders[args.type]
    builder = builder_class(args.config)
    
    # Generate widget
    xml = builder.create_widget(args.output)
    
    if xml and not args.output:
        # Print to stdout if no output file
        print("\n" + "=" * 70)
        print(xml)
    
    return 0


def cmd_sources(args):
    """Handle 'sources' command"""
    
    if not args.config:
        print("❌ Error: --config required to discover data sources")
        return 1
    
    # Discover sources
    discovery = MinionDataSourceDiscovery(args.config)
    sources = discovery.discover()
    
    if args.search:
        # Search mode
        sources = discovery.search(args.search)
        print(f"\n🔍 Search '{args.search}': {len(sources)} results")
        for source in sources:
            print(f"  • {source.namespace}:{source.collector_id}")
            print(f"    {source.description}")
            if source.suggested_unit:
                print(f"    Suggested unit: {source.suggested_unit}")
            min_val, max_val = source.suggested_min_max
            if min_val is not None and max_val is not None:
                print(f"    Suggested range: {min_val} - {max_val}")
            print()
    else:
        # List all sources
        print(discovery.format_source_list())
    
    return 0


def cmd_dashboard(args):
    """Handle 'dashboard' command"""
    
    # Map template types to composer classes
    composers = {
        'quickstart': QuickstartDashboardComposer,
        'monitoring': MonitoringDashboardComposer,
        'performance': PerformanceDashboardComposer,
    }
    
    if args.template not in composers:
        print(f"❌ Error: Unknown template '{args.template}'")
        print(f"Available templates: {', '.join(composers.keys())}")
        return 1
    
    if not args.config:
        print("❌ Error: --config required to generate dashboard")
        return 1
    
    # Create composer
    composer_class = composers[args.template]
    composer = composer_class(args.config)
    
    # Determine output directory
    if args.output:
        output_dir = args.output
    else:
        output_dir = Path(f"{args.template}_dashboard")
    
    # Generate dashboard
    print(f"\n{'='*70}")
    print(f"  BIFF {args.template.title()} Dashboard Generator")
    print(f"{'='*70}\n")
    print(f"Data sources: {len(composer.data_sources)} found")
    print(f"Output directory: {output_dir}")
    print()
    
    result = composer.generate_dashboard(str(output_dir))
    
    print(f"\n{'='*70}")
    print(f"✅ Dashboard generated successfully!")
    print(f"{'='*70}")
    print(f"\nGenerated files in {output_dir}:")
    for tab in result.get('tabs', []):
        print(f"  • {tab}")
    print(f"  • App.Config.xml")
    print(f"\nTo run with Marvin:")
    print(f"  java -jar BIFF.Marvin.jar -i {output_dir}/App.Config.xml")
    print()
    
    return 0


def cmd_list_widgets(args):
    """Handle 'list-widgets' command"""
    print("\n" + "="*70)
    print("  Available Widget Types")
    print("="*70 + "\n")
    
    widgets = {
        'text': 'Simple text display for labels and values',
        'led': 'Status indicator with conditional colors',
        'button': 'Interactive control button (tasks, URLs, data)',
        'gauge': 'Circular/radial gauge with zones',
        'chart': 'Time-series line chart',
        'memory': 'Memory monitoring (bar/gauge/text) with smart zones',
        'network': 'Network throughput visualization',
        'system': 'Multi-source system information panel',
    }
    
    for widget_type, description in widgets.items():
        print(f"  {widget_type:12s} - {description}")
    
    print(f"\n{'='*70}")
    print(f"Total: {len(widgets)} widget types available")
    print(f"{'='*70}\n")
    print("Usage:")
    print("  biff-marvin widget <type> -c MinionConfig.xml -o output.xml")
    print("\nExample:")
    print("  biff-marvin widget gauge -c MinionConfig.xml -o cpu_gauge.xml")
    print()
    
    return 0


def cmd_list_composers(args):
    """Handle 'list-composers' command"""
    print("\n" + "="*70)
    print("  Available Dashboard Composers")
    print("="*70 + "\n")
    
    composers = {
        'quickstart': {
            'desc': 'Simple single-tab dashboard with gauges',
            'best_for': 'Quick setup, basic monitoring',
            'tabs': '1 (Overview)',
        },
        'monitoring': {
            'desc': 'Comprehensive 3-tab monitoring dashboard',
            'best_for': 'Server monitoring, infrastructure',
            'tabs': '3 (Overview, Details, Status)',
        },
        'performance': {
            'desc': 'Performance-focused 2-tab dashboard',
            'best_for': 'Application performance, network ops',
            'tabs': '2 (System, Network)',
        },
    }
    
    for template, info in composers.items():
        print(f"  {template}:")
        print(f"    Description: {info['desc']}")
        print(f"    Best for:    {info['best_for']}")
        print(f"    Tabs:        {info['tabs']}")
        print()
    
    print(f"{'='*70}")
    print(f"Total: {len(composers)} dashboard templates available")
    print(f"{'='*70}\n")
    print("Usage:")
    print("  biff-marvin compose <template> -c MinionConfig.xml -o dashboard_dir")
    print("\nExample:")
    print("  biff-marvin compose monitoring -c MinionConfig.xml -o my_dashboard")
    print()
    
    return 0


def cmd_interactive(args):
    """Handle 'interactive' command - guided dashboard creation"""
    print("\n" + "="*70)
    print("  BIFF Agents - Interactive Dashboard Builder")
    print("="*70 + "\n")
    
    # Step 1: Config file
    if args.config:
        config_path = args.config
    else:
        config_input = input("Path to MinionConfig.xml (or press Enter for quickstart_configs/MinionConfig.xml): ").strip()
        config_path = Path(config_input) if config_input else Path("quickstart_configs/MinionConfig.xml")
    
    if not config_path.exists():
        print(f"\n❌ Config file not found: {config_path}")
        return 1
    
    print(f"✅ Using config: {config_path}\n")
    
    # Step 2: Dashboard template
    print("Available dashboard templates:")
    print("  1. Quickstart  - Simple single-tab with gauges")
    print("  2. Monitoring  - 3-tab comprehensive monitoring")
    print("  3. Performance - 2-tab performance focused")
    
    template_choice = input("\nSelect template (1-3, default=1): ").strip() or "1"
    template_map = {'1': 'quickstart', '2': 'monitoring', '3': 'performance'}
    template = template_map.get(template_choice, 'quickstart')
    
    print(f"✅ Template: {template}\n")
    
    # Step 3: Output directory
    if args.output:
        output_dir = args.output
    else:
        output_input = input(f"Output directory (default={template}_dashboard): ").strip()
        output_dir = Path(output_input) if output_input else Path(f"{template}_dashboard")
    
    print(f"✅ Output: {output_dir}\n")
    
    # Step 4: Confirm and generate
    print("="*70)
    print("Ready to generate dashboard:")
    print(f"  Config:   {config_path}")
    print(f"  Template: {template}")
    print(f"  Output:   {output_dir}")
    print("="*70)
    
    confirm = input("\nProceed? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("❌ Cancelled")
        return 0
    
    # Generate
    composers = {
        'quickstart': QuickstartDashboardComposer,
        'monitoring': MonitoringDashboardComposer,
        'performance': PerformanceDashboardComposer,
    }
    
    composer = composers[template](str(config_path))
    result = composer.generate_dashboard(str(output_dir))
    
    print(f"\n{'='*70}")
    print(f"✅ Dashboard generated successfully!")
    print(f"{'='*70}")
    print(f"\nLocation: {output_dir}")
    print(f"Files: {len(result.get('tabs', [])) + 1}")
    print(f"\nTo run with Marvin:")
    print(f"  java -jar BIFF.Marvin.jar -i {output_dir}/App.Config.xml")
    print()
    
    return 0


def cmd_batch(args):
    """Handle 'batch' command - generate multiple dashboards"""
    print("\n" + "="*70)
    print("  BIFF Agents - Batch Dashboard Generator")
    print("="*70 + "\n")
    
    if not args.configs:
        print("❌ Error: --configs required (comma-separated list)")
        return 1
    
    # Parse config list
    config_paths = [Path(c.strip()) for c in args.configs.split(',')]
    
    # Validate all configs exist
    for config_path in config_paths:
        if not config_path.exists():
            print(f"❌ Config not found: {config_path}")
            return 1
    
    print(f"Found {len(config_paths)} config files:")
    for path in config_paths:
        print(f"  • {path}")
    print()
    
    # Determine template
    template = args.template or 'monitoring'
    composers_map = {
        'quickstart': QuickstartDashboardComposer,
        'monitoring': MonitoringDashboardComposer,
        'performance': PerformanceDashboardComposer,
    }
    
    if template not in composers_map:
        print(f"❌ Invalid template: {template}")
        return 1
    
    # Generate dashboards
    results = []
    for i, config_path in enumerate(config_paths, 1):
        print(f"[{i}/{len(config_paths)}] Processing {config_path.name}...")
        
        try:
            # Create output directory based on config name
            config_name = config_path.stem
            output_dir = Path(args.output or 'batch_output') / config_name
            
            # Generate
            composer = composers_map[template](str(config_path))
            result = composer.generate_dashboard(str(output_dir))
            
            print(f"  ✅ Generated: {output_dir}")
            results.append((config_path, output_dir, True))
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results.append((config_path, None, False))
    
    # Summary
    print(f"\n{'='*70}")
    print("Batch Generation Summary")
    print(f"{'='*70}\n")
    
    success_count = sum(1 for _, _, success in results if success)
    for config_path, output_dir, success in results:
        status = "✅" if success else "❌"
        location = f" → {output_dir}" if output_dir else ""
        print(f"  {status} {config_path.name}{location}")
    
    print(f"\n{'='*70}")
    print(f"Completed: {success_count}/{len(config_paths)} dashboards")
    print(f"{'='*70}\n")
    
    return 0 if success_count == len(config_paths) else 1


def main():
    """Main CLI entry point"""
    
    parser = argparse.ArgumentParser(
        prog='biff-marvin',
        description='BIFF Agents - Marvin GUI Composer (Phase 3)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available widgets and composers
  biff-marvin list-widgets
  biff-marvin list-composers
  
  # List available data sources
  biff-marvin sources -c MinionConfig.xml
  
  # Search for specific data sources
  biff-marvin sources -c MinionConfig.xml --search cpu
  
  # Create individual widgets
  biff-marvin widget gauge -c MinionConfig.xml -o cpu_gauge.xml
  biff-marvin widget button -c MinionConfig.xml -o control_button.xml
  biff-marvin widget memory -c MinionConfig.xml -o memory_monitor.xml
  
  # Create complete dashboards
  biff-marvin dashboard quickstart -c MinionConfig.xml
  biff-marvin dashboard monitoring -c MinionConfig.xml -o my_dashboard
  
  # Interactive mode (guided wizard)
  biff-marvin interactive
  biff-marvin wizard -c MinionConfig.xml
  
  # Batch generation for multiple configs
  biff-marvin batch --configs cfg1.xml,cfg2.xml,cfg3.xml --template monitoring
"""
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='BIFF Agents - Marvin GUI Composer v3.0.0'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Widget command
    widget_parser = subparsers.add_parser(
        'widget',
        help='Create individual widget configurations'
    )
    widget_parser.add_argument(
        'type',
        choices=['text', 'led', 'button', 'gauge', 'chart', 'memory', 'network', 'system'],
        help='Widget type to create'
    )
    widget_parser.add_argument(
        '-c', '--config',
        type=Path,
        help='Path to MinionConfig.xml for data source discovery'
    )
    widget_parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file path for widget XML'
    )
    widget_parser.set_defaults(func=cmd_widget)
    
    # Sources command
    sources_parser = subparsers.add_parser(
        'sources',
        help='Discover and list available data sources'
    )
    sources_parser.add_argument(
        '-c', '--config',
        type=Path,
        required=True,
        help='Path to MinionConfig.xml'
    )
    sources_parser.add_argument(
        '--search',
        help='Search for data sources matching keyword'
    )
    sources_parser.set_defaults(func=cmd_sources)
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser(
        'dashboard',
        help='Create complete dashboard from templates'
    )
    dashboard_parser.add_argument(
        'template',
        choices=['quickstart', 'monitoring', 'performance'],
        help='Dashboard template to use'
    )
    dashboard_parser.add_argument(
        '-c', '--config',
        type=Path,
        required=True,
        help='Path to MinionConfig.xml'
    )
    dashboard_parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output directory (default: <template>_dashboard)'
    )
    dashboard_parser.set_defaults(func=cmd_dashboard)
    
    # List widgets command
    list_widgets_parser = subparsers.add_parser(
        'list-widgets',
        help='Show all available widget types with descriptions'
    )
    list_widgets_parser.set_defaults(func=cmd_list_widgets)
    
    # List composers command
    list_composers_parser = subparsers.add_parser(
        'list-composers',
        help='Show all available dashboard templates'
    )
    list_composers_parser.set_defaults(func=cmd_list_composers)
    
    # Interactive command
    interactive_parser = subparsers.add_parser(
        'interactive',
        aliases=['wizard'],
        help='Interactive dashboard builder with guided prompts'
    )
    interactive_parser.add_argument(
        '-c', '--config',
        type=Path,
        help='Path to MinionConfig.xml (optional, will prompt if not provided)'
    )
    interactive_parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output directory (optional, will prompt if not provided)'
    )
    interactive_parser.set_defaults(func=cmd_interactive)
    
    # Batch command
    batch_parser = subparsers.add_parser(
        'batch',
        help='Generate multiple dashboards from config list'
    )
    batch_parser.add_argument(
        '--configs',
        required=True,
        help='Comma-separated list of MinionConfig.xml files'
    )
    batch_parser.add_argument(
        '--template',
        choices=['quickstart', 'monitoring', 'performance'],
        default='monitoring',
        help='Template to use for all dashboards (default: monitoring)'
    )
    batch_parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Base output directory (default: batch_output)'
    )
    batch_parser.set_defaults(func=cmd_batch)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle no command
    if not args.command:
        parser.print_help()
        return 0
    
    # Dispatch to command handler via set_defaults(func=...)
    if hasattr(args, 'func'):
        return args.func(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
