# BIFF Agents - AI-Powered Configuration Tools

[![GitHub](https://img.shields.io/badge/github-thehevy%2Fbiff--agents-blue)](https://github.com/thehevy/biff-agents)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-see%20parent-lightgrey)](https://github.com/intel/Board-Instrumentation-Framework)

Intelligent command-line agents for the Board Instrumentation Framework (BIFF).

> **Note**: This is an AI agent toolkit for [BIFF](https://github.com/intel/Board-Instrumentation-Framework). It requires the parent BIFF framework to be useful.

## ⚡ Quick Start

**Get a complete BIFF setup running in < 5 minutes!**

```bash
cd biff-agents

# Step 1: Generate configs (interactive wizard)
python -m biff_cli quickstart

# Step 2: Launch everything
cd scripts
start_all.bat  # Windows
./start_all.sh # Linux/Mac
```

→ **[Full Quick Start Guide](QUICKSTART.md)** - Detailed walkthrough with screenshots and troubleshooting

## Features

- **Quick Start Orchestrator**: Generate complete BIFF deployments ✅ **Phase 1 Complete**
- **Minion Collector Builder**: Create and manage collector configurations (Coming soon)
- **Marvin GUI Composer**: Design widget-based dashboards (Coming soon)
- **Oscar Routing Configurator**: Set up data routing and connections (Coming soon)
- **BIFF Debugging Agent**: Diagnose runtime issues (Coming soon)

## What You Get

The Quick Start Orchestrator creates:

- **MinionConfig.xml** - Data collector configuration with 4-6 built-in collectors
- **OscarConfig.xml** - Data routing broker setup
- **Application.xml** - Marvin GUI entry point
- **Tab.QuickStart.xml** - Dashboard tab definition
- **Grid.QuickStart.xml** - Widget grid with gauges and text displays

**Result**: Live dashboard showing CPU, memory, random values, timers, and more!

## Installation

```bash
# From source
cd biff-agents
pip install -e .
```

## CLI Commands

### quickstart
Interactive wizard to create a complete BIFF deployment.

```bash
python -m biff_cli quickstart
```

Generates 5 XML files ready to run. Includes launcher scripts for one-command startup.

### validate
Validate BIFF configuration files for syntax and common errors.

```bash
biff validate <config_file> [-t minion|oscar|marvin|auto]
```

### quickstart
Generate a complete BIFF setup with preconfigured components.

```powershell
biff quickstart [-d OUTPUT_DIR] [-p basic|monitoring|dashboard|custom]
```

### collector
Build and manage Minion collector configurations.

```powershell
biff collector <config_file> [--interactive]
```

### gui
Compose Marvin widget-based dashboards.

```powershell
biff gui <config_file> [--template TEMPLATE]
```

### oscar
Configure Oscar data routing and connections.

```powershell
biff oscar <config_file>
```

### debug
Diagnose BIFF runtime issues.

```powershell
biff debug [--component minion|oscar|marvin|all] [--check network|config|data|all]
```

## Development Status

**Phase 0: Foundation** (Current)
- ✓ Core XML parser
- ✓ Alias/environment variable resolution
- ✓ Configuration validator
- ✓ CLI framework
- ⏳ Testing framework

**Phase 1: Quick Start Orchestrator** (Weeks 3-4)

**Phase 2: Minion Collector Builder** (Weeks 5-7)

**Phase 3: Marvin GUI Composer** (Weeks 8-10)

**Phase 4: BIFF Debugging Agent** (Weeks 11-13)

**Phase 5: Oscar Routing Configurator** (Weeks 14-15)

**Phase 6: Integration & Polish** (Weeks 16-18)

## Architecture

```
biff-agents/
├── biff_agents_core/      # Shared library
│   ├── config/            # XML parsing, alias resolution
│   ├── validators/        # Configuration validation
│   ├── generators/        # XML generation
│   ├── templates/         # Config templates
│   └── utils/             # CLI helpers
├── biff_cli/              # Command-line interface
└── tests/                 # Test suite
```

## Dependencies

- Python 3.9+
- xml.etree.ElementTree (stdlib)
- argparse (stdlib)
- pathlib (stdlib)

## Testing

```powershell
pytest tests/ -v --cov=biff_agents_core
```

## Documentation

See the [BIFF User Guide](../BIFF%20Instrumentation%20Framework%20User%20Guide.pdf) for framework documentation.

## Contributing

This project follows the BIFF contribution guidelines. See [Contributors.txt](../Minion/contributors.txt) for the team.

## License

See [license.txt](../license.txt) for licensing information.
