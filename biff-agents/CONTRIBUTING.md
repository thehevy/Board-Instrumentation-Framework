# Contributing to BIFF Agents

Thank you for your interest in contributing to BIFF Agents! This project provides AI-powered configuration tools for the [Board Instrumentation Framework](https://github.com/intel/Board-Instrumentation-Framework).

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/thehevy/biff-agents.git
   cd biff-agents
   ```

2. **Install in development mode**:
   ```bash
   pip install -e .
   pip install pytest pytest-cov  # For testing
   ```

3. **Run tests**:
   ```bash
   pytest tests/ -v --cov=biff_agents_core
   ```

## Project Structure

```
biff-agents/
├── biff_agents_core/      # Shared library (XML parsing, validation, generation)
├── biff_cli/              # Command-line interface
└── tests/                 # Test suite
```

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Keep functions focused and well-documented
- Aim for 80%+ test coverage

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove)
- Reference issues when applicable

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the test suite
5. Commit your changes
6. Push to your fork
7. Open a Pull Request

### Testing
- Add tests for all new features
- Ensure existing tests pass
- Test against real BIFF configurations when possible

## Implementation Roadmap

See [IMPLEMENTATION_PLAN.md](https://github.com/intel/Board-Instrumentation-Framework/tree/master/.github) for the full roadmap.

**Current Phase**: Phase 0 (Foundation) - 85% complete

**Upcoming**:
- Phase 1: Quick Start Orchestrator
- Phase 2: Minion Collector Builder
- Phase 3: Marvin GUI Composer
- Phase 4: BIFF Debugging Agent
- Phase 5: Oscar Routing Configurator

## Getting Help

- Open an [issue](https://github.com/thehevy/biff-agents/issues) for bugs or feature requests
- Check the [BIFF User Guide](https://github.com/intel/Board-Instrumentation-Framework) for framework documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
