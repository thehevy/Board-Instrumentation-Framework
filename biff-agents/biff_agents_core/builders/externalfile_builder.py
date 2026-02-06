"""
ExternalFile Template Builder
Generates parameterized reusable configuration files using ExternalFile pattern.

Production Pattern:
    Main Config (MinionConfig.xml):
        <ExternalFile PORT_NUM="1" Eth="$(Eth1)">netdev_stats.xml</ExternalFile>
        <ExternalFile PORT_NUM="2" Eth="$(Eth2)">netdev_stats.xml</ExternalFile>
    
    Template File (netdev_stats.xml):
        <ExternalMinionFile>
            <DynamicCollector Prefix="port.$(PORT_NUM)." ...>
                <Plugin>
                    <Param>device=$(Eth)</Param>
                </Plugin>
            </DynamicCollector>
        </ExternalMinionFile>

Use Cases:
- Multi-instance collectors (network ports, CPU cores, containers)
- Parameterized reusable configs
- Reducing config duplication
- Runtime instance count configuration

Production Usage: 10 instances in Intel Vision SUT demo
"""

import sys
import os
from typing import List, Tuple, Optional


class ExternalFileWizard:
    """Interactive wizard for generating ExternalFile pattern configs."""
    
    def __init__(self):
        # Main config parameters
        self.base_filename = ""
        self.instance_count = 1
        self.parameters = []  # List of (param_name, param_values_list)
        
        # Template file parameters
        self.template_type = ""  # 'dynamic_collector', 'collector', 'group'
        self.prefix_pattern = ""
        self.collector_details = {}
        
    def _prompt(self, message: str) -> str:
        """Prompt user and strip BOM characters (Windows PowerShell compatibility)."""
        print(message, end='', flush=True)
        response = input().strip()
        
        # Strip Unicode BOM (\ufeff) or UTF-8 BOM (ï»¿)
        if response.startswith('\ufeff'):
            response = response[1:]
        elif response.startswith('ï»¿'):
            response = response[3:]
            
        return response
    
    def run_interactive(self):
        """Run interactive wizard to collect parameters."""
        print("\n" + "="*70)
        print("  ExternalFile Template Generator")
        print("  Create parameterized reusable configurations")
        print("="*70 + "\n")
        
        # Template filename
        self.base_filename = self._prompt(
            "Template filename (e.g., netdev_stats.xml, test_results.xml): "
        )
        if not self.base_filename.endswith('.xml'):
            self.base_filename += '.xml'
        
        # Instance count
        count_str = self._prompt(
            "\nNumber of instances (how many times to include this file): "
        )
        try:
            self.instance_count = int(count_str)
        except ValueError:
            print(f"Invalid number '{count_str}', using 1")
            self.instance_count = 1
        
        # Parameters
        print("\n" + "-"*70)
        print("Parameter Configuration:")
        print("  Parameters are passed to the template file")
        print("  Common examples: PORT_NUM, Eth, CORE_ID, CONTAINER_ID")
        print("-"*70)
        
        param_count_str = self._prompt(
            "\nHow many parameters to pass to template [1-5]: "
        )
        try:
            param_count = int(param_count_str)
            param_count = max(1, min(5, param_count))
        except ValueError:
            param_count = 1
        
        for i in range(param_count):
            print(f"\nParameter {i+1}:")
            param_name = self._prompt("  Name (e.g., PORT_NUM, Eth): ")
            
            # Get values for each instance
            values = []
            if param_name.upper() in ['PORT_NUM', 'CORE_ID', 'INSTANCE_ID']:
                # Auto-generate sequential values
                start_str = self._prompt(f"  Start value [default: 1]: ")
                try:
                    start_val = int(start_str) if start_str else 1
                except ValueError:
                    start_val = 1
                
                values = [str(start_val + j) for j in range(self.instance_count)]
                print(f"  Auto-generated: {', '.join(values)}")
            else:
                # User provides values
                print(f"  Provide {self.instance_count} values (comma-separated or aliases):")
                values_str = self._prompt("  Values: ")
                values = [v.strip() for v in values_str.split(',')]
                
                # Pad with defaults if needed
                while len(values) < self.instance_count:
                    values.append(f"VALUE{len(values)+1}")
            
            self.parameters.append((param_name, values))
        
        # Template type
        print("\n" + "-"*70)
        print("Template Type:")
        print("  1. DynamicCollector (file-based metrics)")
        print("  2. Standard Collector (plugin/executable)")
        print("  3. Group (multiple collectors)")
        print("-"*70)
        
        type_choice = self._prompt("\nTemplate type [1-3]: ")
        type_map = {
            '1': 'dynamic_collector',
            '2': 'collector',
            '3': 'group'
        }
        self.template_type = type_map.get(type_choice, 'dynamic_collector')
        
        # Prefix pattern
        self.prefix_pattern = self._prompt(
            "\nMetric prefix pattern (use $(PARAM_NAME) for parameters): "
        )
        
        print("\n" + "="*70 + "\n")
    
    def run_piped(self):
        """Run with piped input (non-interactive mode)."""
        try:
            self.base_filename = self._prompt("")
            if not self.base_filename.endswith('.xml'):
                self.base_filename += '.xml'
            
            count_str = self._prompt("")
            self.instance_count = int(count_str)
            
            param_count_str = self._prompt("")
            param_count = int(param_count_str)
            
            # Read parameters
            for _ in range(param_count):
                param_name = self._prompt("")
                values_str = self._prompt("")
                values = [v.strip() for v in values_str.split(',')]
                self.parameters.append((param_name, values))
            
            type_choice = self._prompt("")
            type_map = {'1': 'dynamic_collector', '2': 'collector', '3': 'group'}
            self.template_type = type_map.get(type_choice, 'dynamic_collector')
            
            self.prefix_pattern = self._prompt("")
            
        except (EOFError, ValueError) as e:
            print(f"❌ Input error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def generate_main_config(self) -> str:
        """Generate ExternalFile references for main config."""
        lines = []
        lines.append("<!-- ExternalFile instances -->")
        
        for i in range(self.instance_count):
            # Build attribute string
            attrs = []
            for param_name, param_values in self.parameters:
                if i < len(param_values):
                    value = param_values[i]
                    attrs.append(f'{param_name}="{value}"')
            
            attr_str = ' '.join(attrs)
            lines.append(f'<ExternalFile {attr_str}>{self.base_filename}</ExternalFile>')
        
        return '\n'.join(lines)
    
    def generate_template_file(self) -> str:
        """Generate the external template file content."""
        lines = ['<?xml version="1.0"?>']
        lines.append('<!-- Generated ExternalFile Template -->')
        lines.append('<ExternalMinionFile>')
        
        if self.template_type == 'dynamic_collector':
            lines.append(f'    <DynamicCollector Prefix="{self.prefix_pattern}" Frequency="1000">')
            lines.append('        <File>path/to/data/file.txt</File>')
            lines.append('        <Precision>0</Precision>')
            lines.append('    </DynamicCollector>')
        elif self.template_type == 'collector':
            lines.append(f'    <Collector ID="{self.prefix_pattern}metric">')
            lines.append('        <Plugin>')
            lines.append('            <PythonFile>Collectors/YourCollector.py</PythonFile>')
            lines.append('            <EntryPoint>CollectData</EntryPoint>')
            # Add parameters as <Param> elements
            for param_name, _ in self.parameters:
                lines.append(f'            <Param>{param_name.lower()}=$({param_name})</Param>')
            lines.append('        </Plugin>')
            lines.append('        <Frequency>1000</Frequency>')
            lines.append('    </Collector>')
        else:  # group
            lines.append('    <Group Frequency="1000">')
            lines.append(f'        <Collector ID="{self.prefix_pattern}metric1">')
            lines.append('            <!-- Collector 1 configuration -->')
            lines.append('        </Collector>')
            lines.append(f'        <Collector ID="{self.prefix_pattern}metric2">')
            lines.append('            <!-- Collector 2 configuration -->')
            lines.append('        </Collector>')
            lines.append('    </Group>')
        
        lines.append('</ExternalMinionFile>')
        return '\n'.join(lines)
    
    def display_result(self, main_config: str, template_content: str, 
                      main_filename: str, template_filename: str):
        """Display generated configurations and usage information."""
        print("✅ Generated ExternalFile Configuration:\n")
        
        print("=" * 70)
        print(f"MAIN CONFIG SNIPPET ({main_filename})")
        print("=" * 70)
        print(main_config)
        
        print("\n" + "=" * 70)
        print(f"TEMPLATE FILE ({template_filename})")
        print("=" * 70)
        print(template_content)
        
        print("\n" + "=" * 70)
        print("USAGE NOTES")
        print("=" * 70)
        
        # Parameter expansion example
        print(f"\n📊 Parameter Expansion ({self.instance_count} instances):")
        print("-" * 70)
        for i in range(min(self.instance_count, 3)):
            param_str = ", ".join([
                f"{name}={vals[i] if i < len(vals) else 'N/A'}"
                for name, vals in self.parameters
            ])
            print(f"  Instance {i+1}: {param_str}")
        if self.instance_count > 3:
            print(f"  ... ({self.instance_count - 3} more instances)")
        
        # Prefix expansion
        print(f"\n🔧 Prefix Pattern: {self.prefix_pattern}")
        print("-" * 70)
        if self.instance_count > 0 and self.parameters:
            example_prefix = self.prefix_pattern
            for param_name, param_values in self.parameters:
                if param_values:
                    example_prefix = example_prefix.replace(f'$({param_name})', param_values[0])
            print(f"  Example (instance 1): {example_prefix}")
        
        # Production examples
        print("\n📦 Production Usage (Intel Vision SUT Demo):")
        print("-" * 70)
        print("  • 5 instances of netdev_stats.xml (network ports)")
        print("  • 5 instances of test_results.xml (test data)")
        print("  • Parameters: PORT_NUM (1-5), Eth ($(Eth1)-$(Eth5))")
        print("  • Reduces duplication from 50+ collectors to 2 templates")
        
        print("\n💡 Integration Tips:")
        print("-" * 70)
        print("  1. Add ExternalFile lines to your MinionConfig.xml <Namespace>")
        print(f"  2. Create {self.base_filename} in same directory as config")
        print("  3. Define aliases in <AliasList> if using $(ALIAS) syntax")
        print("  4. Parameters are passed to template and substituted at runtime")
        print("  5. Template file can contain any valid Minion elements")
        print("  6. Use $(PARAM_NAME) in template to reference passed parameters")
        
        print("\n⚠️  Important:")
        print("-" * 70)
        print("  • Template file must have <ExternalMinionFile> root element")
        print("  • Parameters are case-sensitive")
        print("  • Template is included at ExternalFile location")
        print("  • All parameters must be provided in each ExternalFile reference")
        
        print("\n" + "=" * 70 + "\n")


def run_wizard(output_dir: str = "test_output") -> int:
    """
    Run the ExternalFile wizard.
    
    Args:
        output_dir: Directory to save generated files
        
    Returns:
        0 on success, non-zero on failure
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize wizard
    wizard = ExternalFileWizard()
    
    # Run in appropriate mode
    if sys.stdin.isatty():
        wizard.run_interactive()
    else:
        wizard.run_piped()
    
    # Generate configs
    main_config = wizard.generate_main_config()
    template_content = wizard.generate_template_file()
    
    # Filenames
    main_filename = f"ExternalFile_MainConfig_Snippet.xml"
    template_filename = wizard.base_filename
    
    main_filepath = os.path.join(output_dir, main_filename)
    template_filepath = os.path.join(output_dir, template_filename)
    
    # Write files
    try:
        with open(main_filepath, 'w', encoding='utf-8') as f:
            f.write(main_config)
        
        with open(template_filepath, 'w', encoding='utf-8') as f:
            f.write(template_content)
            
    except Exception as e:
        print(f"❌ Failed to write files: {e}", file=sys.stderr)
        return 1
    
    # Display result
    wizard.display_result(main_config, template_content, main_filename, template_filename)
    
    return 0


if __name__ == "__main__":
    sys.exit(run_wizard())
