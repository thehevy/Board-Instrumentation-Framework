"""
Aggregate Collector Builder
Generates XML for collectors that aggregate multiple metrics using Repeat operator.

Production Pattern:
    <Collector ID="post.Tb.TX.Test.Total">
        <Operator>Addition</Operator>
        <Repeat Count="$(NUM_PORTS)" StartValue="1">
            <Input DefaultValue="0">post.$(CurrentValueAlias).test_total_tx</Input>
        </Repeat>
        <Precision>0</Precision>
    </Collector>

Use Cases:
- Sum total TX/RX across all network ports
- Average CPU usage across all cores
- Max memory usage across all containers
- Min latency across all endpoints

Production Usage: 6 instances in Intel Vision SUT demo
"""

import sys
from typing import Optional


class AggregateCollectorWizard:
    """Interactive wizard for generating aggregate collector XML."""
    
    # Supported operators with descriptions
    OPERATORS = {
        '1': ('Addition', 'Sum values from all sources'),
        '2': ('Average', 'Calculate mean value across sources'),
        '3': ('Max', 'Take maximum value from all sources'),
        '4': ('Min', 'Take minimum value from all sources')
    }
    
    def __init__(self):
        self.collector_id = ""
        self.operator = ""
        self.input_pattern = ""
        self.repeat_count = ""
        self.start_value = "1"
        self.default_value = "0"
        self.precision = "0"
        
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
    
    def _validate_pattern(self, pattern: str) -> bool:
        """Validate input pattern contains $(CurrentValueAlias)."""
        # Strip BOM before validation
        if pattern.startswith('\ufeff'):
            pattern = pattern[1:]
        elif pattern.startswith('ï»¿'):
            pattern = pattern[3:]
            
        if '$(CurrentValueAlias)' not in pattern:
            print("❌ Pattern must contain '$(CurrentValueAlias)' placeholder")
            print("   Example: post.$(CurrentValueAlias).test_total_tx")
            return False
        return True
    
    def run_interactive(self):
        """Run interactive wizard to collect parameters."""
        print("\n" + "="*70)
        print("  Aggregate Collector Template Generator")
        print("  Combines multiple metrics using Repeat operator")
        print("="*70 + "\n")
        
        # Collector ID
        self.collector_id = self._prompt(
            "Collector ID (e.g., post.Tb.TX.Test.Total): "
        )
        
        # Operator selection
        print("\nSelect operator:")
        for key, (op, desc) in self.OPERATORS.items():
            print(f"  {key}. {op:10} - {desc}")
        
        op_choice = self._prompt("\nOperator [1-4]: ")
        if op_choice in self.OPERATORS:
            self.operator = self.OPERATORS[op_choice][0]
        else:
            print(f"Invalid choice '{op_choice}', using Addition")
            self.operator = 'Addition'
        
        # Input pattern with validation
        print("\n" + "-"*70)
        print("Input Pattern Requirements:")
        print("  • Must contain $(CurrentValueAlias) placeholder")
        print("  • Will be expanded for each repeat iteration")
        print("  • Example: post.$(CurrentValueAlias).test_total_tx")
        print("-"*70)
        
        while True:
            self.input_pattern = self._prompt(
                "\nInput pattern: "
            )
            if self._validate_pattern(self.input_pattern):
                break
        
        # Repeat count
        self.repeat_count = self._prompt(
            "\nRepeat count (number or alias like $(NUM_PORTS)): "
        )
        
        # Start value (default 1)
        start_val = self._prompt(
            "\nStart value [default: 1]: "
        )
        if start_val:
            self.start_value = start_val
        
        # Default value for missing sources
        default_val = self._prompt(
            "\nDefault value if source missing [default: 0]: "
        )
        if default_val:
            self.default_value = default_val
        
        # Precision
        precision = self._prompt(
            "\nPrecision (decimal places) [default: 0]: "
        )
        if precision:
            self.precision = precision
        
        print("\n" + "="*70 + "\n")
    
    def run_piped(self):
        """Run with piped input (non-interactive mode)."""
        try:
            # Read all inputs
            self.collector_id = self._prompt("")
            op_choice = self._prompt("")
            self.input_pattern = self._prompt("")
            self.repeat_count = self._prompt("")
            self.start_value = self._prompt("")
            self.default_value = self._prompt("")
            self.precision = self._prompt("")
            
            # Validate operator choice
            if op_choice in self.OPERATORS:
                self.operator = self.OPERATORS[op_choice][0]
            else:
                raise ValueError(f"Invalid operator choice: {op_choice}")
            
            # Validate pattern
            if not self._validate_pattern(self.input_pattern):
                raise ValueError("Pattern validation failed")
                
        except EOFError:
            print("❌ Insufficient input data", file=sys.stderr)
            sys.exit(1)
    
    def generate_xml(self) -> str:
        """Generate aggregate collector XML."""
        xml_lines = [
            f'<Collector ID="{self.collector_id}">',
            f'    <Operator>{self.operator}</Operator>',
            f'    <Repeat Count="{self.repeat_count}" StartValue="{self.start_value}">',
            f'        <Input DefaultValue="{self.default_value}">{self.input_pattern}</Input>',
            '    </Repeat>',
            f'    <Precision>{self.precision}</Precision>',
            '</Collector>'
        ]
        return '\n'.join(xml_lines)
    
    def generate_filename(self) -> str:
        """Generate sanitized filename from collector ID."""
        # Replace dots with underscores, keep alphanumeric and underscores
        safe_name = ''.join(
            c if c.isalnum() or c == '_' else '_' 
            for c in self.collector_id
        )
        # Remove consecutive underscores
        while '__' in safe_name:
            safe_name = safe_name.replace('__', '_')
        # Trim underscores from ends
        safe_name = safe_name.strip('_')
        return f"Aggregate_{safe_name}.xml"
    
    def display_result(self, xml_content: str, filename: str):
        """Display generated XML and usage information."""
        print("✅ Generated Aggregate Collector XML:\n")
        print(xml_content)
        print(f"\n📄 Saved to: {filename}\n")
        
        # Usage notes
        print("="*70)
        print("USAGE NOTES")
        print("="*70)
        
        # Expansion example
        if self.repeat_count.isdigit():
            count = int(self.repeat_count)
            start = int(self.start_value)
            print(f"\n📊 Expansion Preview (Count={count}, Start={start}):")
            print("-"*70)
            
            for i in range(start, start + min(count, 3)):
                expanded = self.input_pattern.replace('$(CurrentValueAlias)', str(i))
                print(f"  Iteration {i}: {expanded}")
            
            if count > 3:
                print(f"  ... ({count - 3} more iterations)")
        else:
            print(f"\n📊 Expansion with alias {self.repeat_count}:")
            print("-"*70)
            print(f"  Pattern: {self.input_pattern}")
            print(f"  Will expand from {self.start_value} to {self.start_value} + {self.repeat_count} - 1")
        
        # Operator explanation
        print(f"\n🔧 Operator: {self.operator}")
        print("-"*70)
        if self.operator == 'Addition':
            print("  Sums all source values together")
            print("  Example: port1_tx=100, port2_tx=200 → Total=300")
        elif self.operator == 'Average':
            print("  Calculates mean of all source values")
            print("  Example: core1=50%, core2=70% → Average=60%")
        elif self.operator == 'Max':
            print("  Returns maximum value from all sources")
            print("  Example: endpoint1=100ms, endpoint2=50ms → Max=100ms")
        elif self.operator == 'Min':
            print("  Returns minimum value from all sources")
            print("  Example: endpoint1=100ms, endpoint2=50ms → Min=50ms")
        
        # Default value handling
        if self.default_value != "0":
            print(f"\n⚠️  Default Value: {self.default_value}")
            print("-"*70)
            print(f"  Used when source metric is missing or unavailable")
        
        # Production examples
        print("\n📦 Production Usage (Intel Vision SUT Demo):")
        print("-"*70)
        print("  • Total TX across all ports (6 instances)")
        print("  • Pattern: post.$(CurrentValueAlias).test_total_tx")
        print("  • Repeat: Count=$(NUM_PORTS), StartValue=1")
        print("  • Common with netdev collectors for multi-port aggregation")
        
        print("\n💡 Integration Tips:")
        print("-"*70)
        print("  1. Wrap in <Group> with appropriate Frequency")
        print("  2. Use aliases for Count to enable runtime configuration")
        print("  3. Ensure source collectors exist and send data")
        print("  4. DefaultValue prevents missing data from breaking aggregation")
        print("  5. Precision controls decimal places in output")
        
        print("\n" + "="*70 + "\n")


def run_wizard(output_dir: str = "test_output") -> int:
    """
    Run the aggregate collector wizard.
    
    Args:
        output_dir: Directory to save generated XML
        
    Returns:
        0 on success, non-zero on failure
    """
    import os
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize wizard
    wizard = AggregateCollectorWizard()
    
    # Run in appropriate mode
    if sys.stdin.isatty():
        wizard.run_interactive()
    else:
        wizard.run_piped()
    
    # Generate XML
    xml_content = wizard.generate_xml()
    filename = wizard.generate_filename()
    filepath = os.path.join(output_dir, filename)
    
    # Write to file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
    except Exception as e:
        print(f"❌ Failed to write file: {e}", file=sys.stderr)
        return 1
    
    # Display result
    wizard.display_result(xml_content, filename)
    
    return 0


if __name__ == "__main__":
    sys.exit(run_wizard())
