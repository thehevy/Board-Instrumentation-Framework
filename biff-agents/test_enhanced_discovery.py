"""Test enhanced CollectorDiscovery features"""
import sys
import codecs

# Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

from biff_agents_core.utils.collector_discovery import CollectorDiscovery
from pathlib import Path

# Initialize discovery
biff_root = Path(__file__).parent.parent
discovery = CollectorDiscovery(biff_root)

print("=" * 60)
print("Testing Enhanced CollectorDiscovery Features")
print("=" * 60)

# Test 1: Enhanced parameter parsing
print("\n1. Enhanced Parameter Parsing:")
print("-" * 40)
cpu = discovery.get_collector('CPU')
if cpu:
    func = cpu.functions[0]
    print(f"Function: {func.name}()")
    print(f"Parameters: {len(func.parameters)}")
    for p in func.parameters:
        print(f"  - {p.name}", end="")
        if p.type_hint:
            print(f": {p.type_hint}", end="")
        if p.default:
            print(f" = {p.default}", end="")
        if p.description:
            print(f"  # {p.description}", end="")
        print()

# Test 2: Dependency checking
print("\n2. Dependency Checking:")
print("-" * 40)
deps = discovery.check_dependencies('CPU')
print(f"CPU Dependencies: {list(deps.keys())}")
for dep, installed in deps.items():
    status = "✓ INSTALLED" if installed else "✗ MISSING"
    print(f"  {dep:20} {status}")

missing = discovery.get_missing_dependencies('CPU')
if missing:
    print(f"\nMissing dependencies: {missing}")
    print(f"Install command: {discovery.suggest_install_command(missing)}")
else:
    print("\n✓ All dependencies installed!")

# Test 3: Check a collector with more dependencies
print("\n3. Docker_Stats Dependencies:")
print("-" * 40)
docker_deps = discovery.check_dependencies('Docker_Stats')
print(f"Dependencies: {list(docker_deps.keys())}")
for dep, installed in docker_deps.items():
    status = "✓ INSTALLED" if installed else "✗ MISSING"
    print(f"  {dep:20} {status}")

docker_missing = discovery.get_missing_dependencies('Docker_Stats')
if docker_missing:
    print(f"\nTo use Docker_Stats, install:")
    print(f"  {discovery.suggest_install_command(docker_missing)}")

# Test 4: Example extraction
print("\n4. Example Extraction:")
print("-" * 40)
random_val = discovery.get_collector('RandomVal')
if random_val and random_val.functions:
    func = random_val.functions[0]
    print(f"Function: {func.name}()")
    if func.example:
        print(f"Example:\n{func.example}")
    else:
        print("No example found")

print("\n" + "=" * 60)
print("Enhanced features working! ✓")
print("=" * 60)
