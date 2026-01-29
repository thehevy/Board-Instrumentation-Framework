# Next Steps - Transition to Phase 1

**Date**: January 29, 2026  
**Current Status**: Phase 0 Complete (85%) → Phase 1 Ready

---

## Phase 0 Completion Checklist

### ✅ Core Complete (Week 1)
- [x] Directory structure (8 directories)
- [x] Core library implementation (12 files)
  - [x] XML parser with all extraction methods
  - [x] Alias resolver with circular reference detection
  - [x] Environment variable resolver
  - [x] Configuration validator (Minion/Oscar/Marvin)
  - [x] Base XML generator
  - [x] CLI helper utilities
- [x] CLI framework (6 commands structured)
  - [x] `biff validate` - FUNCTIONAL
  - [x] Framework for 5 agents ready
- [x] Testing infrastructure
  - [x] pytest configuration
  - [x] 17 unit tests passing
- [x] Package configuration
  - [x] setup.py with entry point
  - [x] requirements.txt
  - [x] Git initialized and committed
- [x] GitHub preparation
  - [x] LICENSE (MIT)
  - [x] CONTRIBUTING.md
  - [x] .gitignore
  - [x] GITHUB_SETUP.md

### 🔄 In Progress (Week 2, Days 2-5)
- [ ] **Testing Expansion** (Days 2-3)
  - [ ] Add EnvVarResolver tests (~10 tests)
  - [ ] Add ConfigValidator tests (~15 tests)
  - [ ] Add BaseGenerator tests (~10 tests)
  - [ ] Create fixture configs from Intel demos
  - [ ] Run full test suite with coverage
  - [ ] Target: 80%+ coverage

- [ ] **Enhancements** (Days 4-5)
  - [ ] Port availability checker (`network_utils.py`)
  - [ ] Dependency checker for Python packages
  - [ ] Enhanced error messages with line numbers
  - [ ] XML Import resolution (recursive alias files)
  - [ ] GitHub Actions CI/CD workflow

- [ ] **Documentation**
  - [ ] API documentation for core library
  - [ ] Usage examples for validator
  - [ ] Contributing guide polish

---

## Phase 1 Preparation

### Prerequisites ✅ All Met

- ✅ XML parser can extract namespaces, collectors, actors
- ✅ Validator can check configuration validity
- ✅ Generator can create XML elements
- ✅ CLI framework ready for new commands
- ✅ Testing framework established

### Week 3 Goals: Core Quick Start

#### Day 1-2: Environment Detection
**Files to Create**:
```
biff_agents_core/validators/environment_validator.py
biff_agents_core/utils/system_utils.py
```

**Features**:
- Java version detection (`java -version` → parse output)
- Python version detection (already have via `sys.version_info`)
- Gradle detection (check for `gradlew` in Marvin/)
- Port availability check (UDP 1100, 52001, 5100-5200 range)
- OS detection (Windows/Linux/macOS)

**Tests**:
```python
def test_java_version_detection():
    assert detect_java_version() >= (10, 0)

def test_port_availability():
    assert is_port_available(1100, protocol='udp')

def test_python_version():
    assert sys.version_info >= (3, 9)
```

#### Day 3-5: Single-Machine Setup Generator
**Files to Create**:
```
biff_agents_core/templates/quickstart_templates.py
biff_agents_core/generators/quickstart_generator.py
biff_cli/quickstart.py
tests/test_quickstart_generator.py
```

**Generate**:
1. **MinionConfig.xml**:
   - Single namespace "QuickStart"
   - Target: localhost:5100 (Oscar)
   - 3 collectors: CPU, Memory, RandomVal
   - Default frequency: 1000ms

2. **OscarConfig.xml**:
   - Incoming: port 1100 (Minion)
   - Outgoing: localhost:52001 (Marvin)

3. **QuickStartApp.xml** (Marvin):
   - Network: port 52001
   - 3 gauges (CPU, Memory, Random)
   - Grid: 3 columns
   - Auto-bind to QuickStart namespace

**CLI Implementation**:
```python
@quickstart.command()
def local():
    """Generate single-machine BIFF setup"""
    # 1. Validate prerequisites
    validate_environment()
    
    # 2. Create project directory
    create_project_structure()
    
    # 3. Generate configs
    generate_minion_config()
    generate_oscar_config()
    generate_marvin_config()
    
    # 4. Build Marvin
    build_marvin()
    
    # 5. Print launch instructions
    print_launch_instructions()
```

**Testing**:
```bash
# Test environment detection
pytest tests/test_environment_validator.py -v

# Test config generation
pytest tests/test_quickstart_generator.py -v

# Integration test
biff quickstart local --output test_project
cd test_project
# Verify all 3 configs exist and are valid
biff validate Minion/MinionConfig.xml
biff validate Oscar/OscarConfig.xml
biff validate Marvin/QuickStartApp.xml
```

---

## Week 4 Goals: Advanced Deployments

### Container Deployment (Days 1-3)
**Files to Create**:
```
biff_agents_core/templates/container_templates.py
biff_agents_core/generators/container_generator.py
tests/test_container_generator.py
```

**Generate**:
1. **Dockerfile** (Minion):
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY Minion/ ./Minion/
   COPY MinionConfig.xml .
   ENV MinionNamespace=default
   CMD ["python3", "Minion/Minion.py", "-c", "MinionConfig.xml"]
   ```

2. **docker-compose.yml**:
   ```yaml
   services:
     oscar:
       build: ./Oscar
       ports:
         - "1100:1100/udp"
     minion:
       build: ./Minion
       environment:
         - MinionNamespace=${NAMESPACE}
   ```

3. **launchMinion.sh** (with CPU affinity):
   ```bash
   #!/bin/bash
   lastCore=$(($(nproc) - 1))
   taskset -c $lastCore python3 Minion/Minion.py -c MinionConfig.xml
   ```

4. **DaemonSet.yaml** (Kubernetes):
   ```yaml
   apiVersion: apps/v1
   kind: DaemonSet
   metadata:
     name: biff-minion
   ```

### Multi-Deployment (Days 4-5)
**Project Structure**:
```
multi-deployment-project/
├── Oscar/
│   └── OscarConfig.xml
├── Minion/
│   ├── deployment-A/
│   │   └── MinionConfig.xml
│   └── deployment-B/
│       └── MinionConfig.xml
├── Marvin/
│   ├── ComparisonApp.xml
│   └── Tab.DeploymentA.xml
│   └── Tab.DeploymentB.xml
```

**CLI**:
```bash
biff quickstart multi-deployment \
  --deployments prod,staging \
  --metrics cpu,memory,network
```

---

## Success Criteria for Phase 1

### Week 3 Completion
- [ ] `biff quickstart local` generates working setup
- [ ] User can launch all 3 components and see data
- [ ] Setup time < 10 minutes (vs 1-2 hours manual)
- [ ] Works on Windows and Linux

### Week 4 Completion
- [ ] `biff quickstart container` generates Docker/K8s configs
- [ ] `biff quickstart multi-deployment` creates comparison project
- [ ] Docker image builds and runs successfully
- [ ] Multi-deployment shows side-by-side comparison

### Demo Requirements
1. **New User Demo** (Week 3):
   ```bash
   biff quickstart local
   # Follow prompts
   # Launch components
   # Show live dashboard in < 10 minutes
   ```

2. **Container Demo** (Week 4):
   ```bash
   biff quickstart container
   docker-compose up
   # Show containerized BIFF running
   ```

3. **Multi-Deployment Demo** (Week 4):
   ```bash
   biff quickstart multi-deployment --deployments prod,test
   # Show comparison dashboard with 2 environments
   ```

---

## Immediate Actions (Today/Tomorrow)

### Priority 1: Complete Phase 0 Testing
```bash
# 1. Create test for EnvVarResolver
cd biff-agents
cat > tests/test_env_var_resolver.py << 'EOF'
import pytest
from biff_agents_core.config.env_var_resolver import EnvVarResolver

def test_resolve_env_var():
    resolver = EnvVarResolver()
    result = resolver.resolve("Path: $(HOME)", env={'HOME': '/home/user'})
    assert result == "Path: /home/user"
EOF

# 2. Run tests
pytest tests/ -v --cov=biff_agents_core

# 3. Check coverage
# Target: 80%+
```

### Priority 2: Push to GitHub
```bash
# 1. Fork on GitHub: https://github.com/intel/Board-Instrumentation-Framework
# 2. Update remote and push
git remote rename origin upstream
git remote add origin https://github.com/thehevy/Board-Instrumentation-Framework.git
git checkout -b feature/biff-agents
git push -u origin feature/biff-agents
```

### Priority 3: Start Phase 1 Prep
```bash
# 1. Create branch for Phase 1
git checkout -b phase1/quickstart

# 2. Create placeholder files
mkdir -p biff_agents_core/validators
touch biff_agents_core/validators/environment_validator.py
touch biff_agents_core/utils/system_utils.py
touch biff_agents_core/templates/quickstart_templates.py

# 3. Start implementing environment detection
```

---

## Questions to Resolve

### Technical Decisions
1. **Build Automation**: Should we build Marvin automatically or provide instructions?
   - Recommendation: Auto-build with progress indicator
   
2. **Error Handling**: How verbose should error messages be?
   - Recommendation: Verbose by default, `--quiet` flag for CI/CD
   
3. **Default Values**: What defaults for Quick Start?
   - Recommendation: 3 collectors, 1000ms frequency, localhost routing

### Process Decisions
1. **Testing Approach**: Unit tests vs integration tests priority?
   - Recommendation: Unit tests during development, integration tests before release
   
2. **Documentation**: When to write user docs?
   - Recommendation: After each phase completes

---

## Resources Needed

### Development
- [ ] Access to Windows/Linux test VMs
- [ ] Docker Desktop installed
- [ ] Kubernetes cluster (minikube/kind) for testing

### Testing
- [ ] Intel Vision demo configs for fixtures
- [ ] Production BIFF setup for integration testing

---

## Risk Mitigation

### Risk: Java/Gradle build issues
**Mitigation**: Test on clean systems, provide detailed error messages

### Risk: UDP port conflicts
**Mitigation**: Port availability checker before setup

### Risk: Cross-platform path issues
**Mitigation**: Use `pathlib` exclusively, test on both platforms

---

## Timeline

**Week 2 (Current)**: Complete Phase 0 testing, push to GitHub
**Week 3**: Implement Quick Start core (environment detection, single-machine)
**Week 4**: Implement Quick Start advanced (container, multi-deployment)
**Week 5**: Begin Phase 2 (Collector Builder)

**Milestone**: End of Week 4 - Quick Start fully functional

---

## Contact & Coordination

For questions about:
- **Architecture**: Review shared library design
- **Testing**: Coordinate test coverage goals
- **Timeline**: Adjust if needed based on progress

---

**Ready to Begin Phase 1!** 🚀

The foundation is solid. All prerequisites are met. Let's build the Quick Start Orchestrator!
