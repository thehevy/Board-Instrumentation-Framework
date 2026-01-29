# BIFF Agents - AI-Powered Configuration Tools

[![GitHub](https://img.shields.io/badge/github-thehevy%2Fbiff--agents-blue)](https://github.com/thehevy/biff-agents)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-see%20parent-lightgrey)](https://github.com/intel/Board-Instrumentation-Framework)

Intelligent command-line agents for the Board Instrumentation Framework (BIFF).

> **Note**: This is an AI agent toolkit for [BIFF](https://github.com/intel/Board-Instrumentation-Framework). It requires the parent BIFF framework to be useful.

## Features

- **Quick Start Orchestrator**: Generate complete BIFF deployments
- **Minion Collector Builder**: Create and manage collector configurations
- **Marvin GUI Composer**: Design widget-based dashboards
- **Oscar Routing Configurator**: Set up data routing and connections
- **BIFF Debugging Agent**: Diagnose runtime issues

## Installation

```powershell
# From source
cd biff-agents
pip install -e .
```

## Quick Start

```powershell
# Validate a configuration
biff validate MinionConfig.xml

# Generate a quick start project
biff quickstart --preset monitoring

# Add collectors interactively
biff collector MinionConfig.xml --interactive

# Debug connection issues
biff debug --check network
```

## Commands

### validate
Validate BIFF configuration files for syntax and common errors.

```powershell
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
