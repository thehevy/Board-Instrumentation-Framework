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
    
    saved_paths = composer.save_dashboard(output_dir)
    
    print(f"\n{'='*70}")
    print(f"✅ Dashboard generated successfully!")
    print(f"{'='*70}")
    print(f"\nGenerated {len(saved_paths)} files:")
    for path in saved_paths:
        print(f"  • {path.name}")
    print(f"\nTo run with Marvin:")
    print(f"  java -jar BIFF.Marvin.jar -i {output_dir / 'App.Config.xml'}")
    print()
    
    return 0


def main():
    """Main CLI entry point"""
    
    parser = argparse.ArgumentParser(
        prog='biff-marvin',
        description='BIFF Agents - Marvin GUI Composer (Phase 3)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available data sources
  biff-marvin sources -c MinionConfig.xml
  
  # Search for specific data sources
  biff-marvin sources -c MinionConfig.xml --search cpu
  
  # Create a text widget interactively
  biff-marvin widget text -c MinionConfig.xml -o my_text.xml
  
  # Create an LED indicator
  biff-marvin widget led -c MinionConfig.xml -o status_led.xml
  
  # Create a complete dashboard (Week 9)
  biff-marvin dashboard quickstart -c MinionConfig.xml
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
        choices=['text', 'led', 'gauge', 'chart'],
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
        help='Output directory for dashboard files (default: <template>_dashboard)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle no command
    if not args.command:
        parser.print_help()
        return 0
    
    # Dispatch to command handler
    if args.command == 'widget':
        return cmd_widget(args)
    elif args.command == 'sources':
        return cmd_sources(args)
    elif args.command == 'dashboard':
        return cmd_dashboard(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
