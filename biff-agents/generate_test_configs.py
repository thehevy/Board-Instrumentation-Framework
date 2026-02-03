"""Test script to generate sample configs for launcher testing"""
from pathlib import Path
from biff_agents_core.generators.minion_generator import MinionConfigGenerator
from biff_agents_core.generators.oscar_generator import OscarConfigGenerator
from biff_agents_core.generators.marvin_generator import MarvinApplicationGenerator

# Create output directory
output_dir = Path(__file__).parent / "quickstart_configs"
output_dir.mkdir(exist_ok=True)

# Test config
config = {
    "minion_namespace": "QuickStart",
    "collectors": ["RandomVal", "Timer", "CPU", "Memory"],
    "oscar_port": 1100,
    "minion_port": 5100,
    "marvin_port": 52001,
    "use_existing": True,
    "biff_root": Path(__file__).parent.parent.absolute()
}

print(f"Generating test configs in: {output_dir}")
print()

# Generate Minion config
minion_gen = MinionConfigGenerator()
minion_file = minion_gen.generate_file(config, output_dir)
print(f"✓ Created: {minion_file}")

# Generate Oscar config
oscar_gen = OscarConfigGenerator()
oscar_file = oscar_gen.generate_file(config, output_dir)
print(f"✓ Created: {oscar_file}")

# Generate Marvin configs
marvin_gen = MarvinApplicationGenerator()
marvin_files = marvin_gen.generate_all(config, output_dir)
print(f"✓ Created: {marvin_files['application']}")
print(f"✓ Created: {marvin_files['tab']}")
print(f"✓ Created: {marvin_files['grid']}")

print()
print("Test configs generated successfully!")
print()
print("To test the launcher:")
print("  cd scripts")
print("  start_all.bat")
