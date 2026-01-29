"""Manual test to see generated Marvin XML output"""
from pathlib import Path
import tempfile
import shutil
from biff_agents_core.generators.marvin_generator import MarvinApplicationGenerator

# Create generator
gen = MarvinApplicationGenerator()

# Test config
config = {
    "minion_namespace": "QuickStart",
    "collectors": ["RandomVal", "Timer", "CPU", "Memory", "Network", "Storage"],
    "marvin_port": 52001,
    "use_existing": False
}

# Generate to temp dir
temp_dir = Path(tempfile.mkdtemp())
files = gen.generate_all(config, temp_dir)

print("Generated files:")
for name, path in files.items():
    print(f"\n{'='*80}")
    print(f"{name.upper()}: {path}")
    print('='*80)
    print(path.read_text())

# Clean up
shutil.rmtree(temp_dir)
