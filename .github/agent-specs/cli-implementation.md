# BIFF Agent CLI - Detailed Implementation Specification

## Executive Summary

The BIFF Agent CLI provides a unified, intuitive command-line interface to all five AI agents. Designed for both interactive workflows and automation, the CLI supports progressive disclosure (simple commands for beginners, advanced flags for power users), smart defaults, and rich feedback including progress indicators, validation results, and contextual help.

**Design Philosophy**:
- **Natural Language First**: Commands read like sentences (`biff create collector`, not `biff-collector-create`)
- **Progressive Disclosure**: Simple commands work out-of-box, advanced features available via flags
- **Context-Aware**: CLI detects workspace state and suggests next actions
- **Automation-Friendly**: All interactive flows support non-interactive mode with flags
- **Rich Feedback**: Progress bars, color-coded output, structured results

---

## CLI Architecture

### Component Structure

```
biff (entry point)
├── biff.py              # Main CLI entry point, command router
├── cli/
│   ├── __init__.py
│   ├── base.py          # Base command class, common utilities
│   ├── commands/
│   │   ├── quickstart.py    # Quick Start commands
│   │   ├── collector.py     # Collector Builder commands
│   │   ├── gui.py           # GUI Composer commands
│   │   ├── oscar.py         # Oscar Configurator commands
│   │   └── debug.py         # Debugging Agent commands
│   ├── interactive.py   # Interactive prompt utilities
│   ├── output.py        # Formatted output, progress bars
│   └── validation.py    # Input validation, config checking
├── shared/              # Shared agent infrastructure
│   ├── biff_config.py   # Config parser/validator
│   ├── session_state.py # Session management
│   └── utilities.py     # Network, XML, process utilities
└── agents/              # Agent implementations
    ├── quick_start.py
    ├── collector_builder.py
    ├── gui_composer.py
    ├── oscar_configurator.py
    └── debugging_agent.py
```

---

## Command Structure

### Top-Level Commands

```bash
biff [COMMAND] [SUBCOMMAND] [OPTIONS]

Commands:
  init         Initialize BIFF workspace (alias: quickstart, setup)
  collector    Create and manage collectors (alias: collect)
  gui          Create and manage Marvin dashboards (alias: dashboard, viz)
  oscar        Configure Oscar routing (alias: route)
  debug        Diagnose and troubleshoot issues (alias: diagnose, check)
  status       Show workspace status and health
  validate     Validate all configurations
  version      Show version information
  help         Show detailed help
```

### Command Hierarchy

```
biff
├── init [DEPLOYMENT_TYPE]
│   ├── --single-machine         # Single machine deployment (default)
│   ├── --distributed            # Distributed deployment
│   ├── --minion-ips IP1,IP2     # Minion IPs (distributed mode)
│   ├── --oscar-ip IP            # Oscar IP
│   ├── --marvin-ip IP           # Marvin IP
│   ├── --skip-build             # Don't build Marvin
│   ├── --skip-test              # Don't test connectivity
│   └── --output-dir DIR         # Output directory
│
├── collector
│   ├── create [NAME]            # Create new collector (interactive)
│   │   ├── --namespace NS       # Target namespace
│   │   ├── --id ID              # Collector ID
│   │   ├── --type TYPE          # Collector type (shell, file, psutil, api, custom)
│   │   ├── --command CMD        # Command to execute (shell type)
│   │   ├── --file PATH          # File to parse (file type)
│   │   ├── --frequency MS       # Collection frequency
│   │   ├── --test               # Test after creation
│   │   └── --no-add             # Don't add to MinionConfig.xml
│   │
│   ├── list                     # List existing collectors
│   │   ├── --namespace NS       # Filter by namespace
│   │   └── --format json|table  # Output format
│   │
│   ├── test [COLLECTOR_ID]      # Test specific collector
│   │   ├── --namespace NS       # Namespace (if ambiguous)
│   │   └── --verbose            # Show detailed output
│   │
│   ├── edit [COLLECTOR_ID]      # Edit existing collector
│   └── remove [COLLECTOR_ID]    # Remove collector
│
├── gui
│   ├── create [NAME]            # Create new dashboard (interactive)
│   │   ├── --template TYPE      # Template (monitoring, system, app, executive, blank)
│   │   ├── --collectors ID1,ID2 # Collectors to include
│   │   ├── --layout STYLE       # Layout style (balanced, priority, compact)
│   │   ├── --theme THEME        # Theme (default, dark, light)
│   │   ├── --window-size WxH    # Window size (1920x1080)
│   │   └── --output-dir DIR     # Output directory
│   │
│   ├── add-widget [DASHBOARD]   # Add widget to existing dashboard
│   │   ├── --collector ID       # Collector to bind
│   │   ├── --type WIDGET_TYPE   # Widget type (gauge, chart, text, led)
│   │   ├── --position R,C       # Grid position (row, column)
│   │   └── --tab TAB_NAME       # Tab name
│   │
│   ├── list                     # List existing dashboards
│   ├── validate [DASHBOARD]     # Validate dashboard config
│   └── preview [DASHBOARD]      # Show dashboard structure
│
├── oscar
│   ├── configure [TOPOLOGY]     # Configure Oscar (interactive)
│   │   ├── --topology TYPE      # Topology type (single, distributed, hierarchical, etc.)
│   │   ├── --minion-ips IP1,IP2 # Minion IPs
│   │   ├── --oscar-ip IP        # Oscar IP
│   │   ├── --marvin-ips IP1,IP2 # Marvin IPs
│   │   ├── --record FILE        # Enable recording to file
│   │   ├── --filter FILE        # Enable filtering (shunting)
│   │   └── --output FILE        # Output config file
│   │
│   ├── chain                    # Configure Oscar chaining (interactive)
│   │   ├── --levels N           # Number of levels
│   │   └── --site-count N       # Sites per level
│   │
│   ├── record                   # Configure recording
│   │   ├── --output FILE        # Recording output file
│   │   ├── --auto-timestamp     # Add timestamp to filename
│   │   └── --max-size MB        # Max file size
│   │
│   ├── playback FILE            # Generate playback command
│   │   ├── --speed FLOAT        # Playback speed (1.0 = realtime)
│   │   ├── --loop               # Enable looping
│   │   └── --exit-after         # Exit after playback
│   │
│   └── validate                 # Validate Oscar config
│
├── debug
│   ├── [no args]                # Interactive troubleshooting wizard
│   │
│   ├── check [COMPONENT]        # Check specific component (minion, oscar, marvin, all)
│   │   ├── --verbose            # Detailed output
│   │   └── --fix                # Auto-fix if possible
│   │
│   ├── network                  # Test network connectivity
│   │   ├── --minion-to-oscar    # Test Minion → Oscar
│   │   ├── --oscar-to-marvin    # Test Oscar → Marvin
│   │   └── --all                # Test all connections
│   │
│   ├── logs [COMPONENT]         # Analyze logs
│   │   ├── --errors-only        # Show only errors
│   │   ├── --tail N             # Show last N lines
│   │   └── --follow             # Follow log in realtime
│   │
│   ├── collector [COLLECTOR_ID] # Test specific collector
│   │   └── --namespace NS       # Namespace (if ambiguous)
│   │
│   └── report                   # Generate diagnostic report
│       ├── --output FILE        # Save report to file
│       └── --include-logs       # Include log excerpts
│
├── status                       # Show workspace status
│   ├── --verbose                # Detailed status
│   ├── --json                   # JSON output
│   └── --component COMP         # Show specific component
│
├── validate                     # Validate all configs
│   ├── --component COMP         # Validate specific component
│   ├── --fix                    # Auto-fix issues
│   └── --report FILE            # Save report to file
│
└── version                      # Show version info
    └── --check-updates          # Check for updates
```

---

## Implementation Details

### Main Entry Point

```python
#!/usr/bin/env python3
# biff.py

import sys
import argparse
from cli.commands import quickstart, collector, gui, oscar, debug
from cli.base import CLIBase
from cli.output import Output, Colors

VERSION = "1.0.0"

class BIFFCLIError(Exception):
    """Base exception for CLI errors"""
    pass

def create_parser():
    """Create main argument parser"""
    
    parser = argparse.ArgumentParser(
        prog='biff',
        description='BIFF AI Agent CLI - Interactive instrumentation framework toolkit',
        epilog='Run "biff COMMAND --help" for detailed command help'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'BIFF CLI {VERSION}'
    )
    
    parser.add_argument(
        '--workspace',
        default='.',
        help='Workspace root directory (default: current directory)'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init/Quick Start
    quickstart.register_parser(subparsers)
    
    # Collector commands
    collector.register_parser(subparsers)
    
    # GUI commands
    gui.register_parser(subparsers)
    
    # Oscar commands
    oscar.register_parser(subparsers)
    
    # Debug commands
    debug.register_parser(subparsers)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show workspace status')
    status_parser.add_argument('--json', action='store_true', help='JSON output')
    status_parser.add_argument('--component', choices=['minion', 'oscar', 'marvin', 'all'], 
                               default='all', help='Component to check')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configurations')
    validate_parser.add_argument('--component', help='Specific component to validate')
    validate_parser.add_argument('--fix', action='store_true', help='Auto-fix issues')
    validate_parser.add_argument('--report', help='Save report to file')
    
    return parser

def main():
    """Main CLI entry point"""
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Configure output
    Output.configure(
        color=not args.no_color,
        quiet=args.quiet,
        verbose=args.verbose
    )
    
    # No command provided, show help
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        # Route to appropriate command handler
        if args.command in ['init', 'quickstart', 'setup']:
            return quickstart.run(args)
        elif args.command in ['collector', 'collect']:
            return collector.run(args)
        elif args.command in ['gui', 'dashboard', 'viz']:
            return gui.run(args)
        elif args.command in ['oscar', 'route']:
            return oscar.run(args)
        elif args.command in ['debug', 'diagnose', 'check']:
            return debug.run(args)
        elif args.command == 'status':
            return run_status(args)
        elif args.command == 'validate':
            return run_validate(args)
        else:
            Output.error(f"Unknown command: {args.command}")
            return 1
            
    except BIFFCLIError as e:
        Output.error(str(e))
        return 1
    except KeyboardInterrupt:
        Output.warning("\nOperation cancelled by user")
        return 130
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            Output.error(f"Unexpected error: {e}")
            Output.info("Run with --verbose for details")
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

---

## Usage Examples

### Example 1: Complete Setup Flow

```bash
# Initial setup
$ biff init --distributed

[Interactive wizard walks through setup]

✓ Generated MinionConfig.xml
✓ Generated OscarConfig.xml  
✓ Generated Application.xml

Next: Create custom collectors? [Y/n]: y

# Seamless handoff to collector builder
[Continuing from Quick Start...]

# Add custom collector
$ biff collector create
[Interactive wizard]
✓ Created Collectors/DiskUsage.py
✓ Updated MinionConfig.xml

# Create dashboard
$ biff gui create --template system
[Interactive wizard]
✓ Created Application.xml
✓ Created Grid_System.xml

# Validate everything
$ biff validate
✓ Minion config valid
✓ Oscar config valid
✓ Marvin config valid
✓ All widget bindings valid
```

### Example 2: Non-Interactive (CI/CD)

```bash
# Automated setup
$ biff init \
    --single-machine \
    --skip-build \
    --yes

# Create collector without prompts
$ biff collector create \
    --namespace SystemMetrics \
    --id disk.usage \
    --type shell \
    --command "df -h / | awk 'NR==2 {print $5}' | sed 's/%//'" \
    --frequency 5000 \
    --test

# Validate in CI pipeline
$ biff validate --report validation-report.json
$ if [ $? -ne 0 ]; then
    echo "Validation failed"
    exit 1
  fi
```

### Example 3: Troubleshooting Workflow

```bash
# Dashboard not showing data
$ biff debug

[Interactive troubleshooting wizard]

Checking components...
✓ Minion running
✓ Oscar running  
✓ Marvin running

Checking network...
✓ Minion → Oscar connectivity
✗ Oscar → Marvin connectivity

Issue: Marvin listening on port 52001, Oscar sending to 52002

Fix? [Y/n]: y

✓ Updated OscarConfig.xml
✓ Restart Oscar to apply changes
```

---

## Success Metrics

### CLI Usability Metrics
- **Time to First Success**: <5 minutes from install to running dashboard
- **Error Recovery Rate**: >90% of errors provide actionable suggestions
- **Interactive vs Non-Interactive**: Support both seamlessly
- **Help Accessibility**: <2 keystrokes to relevant help

### Technical Metrics
- **Startup Time**: <100ms for command invocation
- **Progress Feedback**: All operations >2s show progress indicator
- **Output Clarity**: 95%+ users understand output without documentation

---

## Implementation Phases

### Phase 1: Core CLI (Week 1)
- Main entry point and argument parsing
- Output formatting utilities
- Base command class
- Quick Start and Collector commands

### Phase 2: Advanced Features (Week 2)
- Interactive prompts and wizards
- GUI and Oscar commands
- Debug command with diagnostics
- Session state and handoffs

### Phase 3: Polish & Integration (Week 3)
- Platform-specific installers
- Shell completion
- Comprehensive error handling
- Integration testing

---

This CLI specification provides a production-ready command-line interface that makes BIFF's AI agents accessible, consistent, and powerful for both interactive and automated workflows.
