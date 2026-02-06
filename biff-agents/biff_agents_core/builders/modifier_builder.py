"""
Bulk Regex Modifier Generator for BIFF

Generates <Modifier> XML for pattern-based transformations
that apply to multiple metrics at once.
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path


class ModifierWizard:
    """Interactive wizard for creating bulk regex modifiers"""
    
    NORMALIZATION_PRESETS = {
        'bytes_to_mbps': {
            'name': 'Bytes/sec → Mbps',
            'factor': 0.00000782,
            'description': 'Network throughput: bytes per second to megabits per second'
        },
        'bytes_to_gbps': {
            'name': 'Bytes/sec → Gbps', 
            'factor': 0.00000000782,
            'description': 'High-speed network: bytes per second to gigabits per second'
        },
        'bytes_to_mb': {
            'name': 'Bytes → MB',
            'factor': 0.00000095367432,
            'description': 'Memory/storage: bytes to megabytes'
        },
        'bytes_to_gb': {
            'name': 'Bytes → GB',
            'factor': 0.00000000093132257,
            'description': 'Large storage: bytes to gigabytes'
        },
        'percent_decimal': {
            'name': 'Percentage (0-100) → Decimal (0-1)',
            'factor': 0.01,
            'description': 'Convert percentage to decimal fraction'
        },
        'milliseconds_to_seconds': {
            'name': 'Milliseconds → Seconds',
            'factor': 0.001,
            'description': 'Time conversion: milliseconds to seconds'
        },
        'nanoseconds_to_milliseconds': {
            'name': 'Nanoseconds → Milliseconds',
            'factor': 0.000001,
            'description': 'High-precision time: nanoseconds to milliseconds'
        },
        'custom': {
            'name': 'Custom factor',
            'factor': None,
            'description': 'Enter your own normalization factor'
        }
    }
    
    MODIFIER_OPERATIONS = {
        'normalize': 'Normalize (multiply by factor)',
        'scale': 'Scale (divide by factor)',
        'delta': 'Delta (report change since last value)',
        'average': 'Average (smooth over time)'
    }
    
    def __init__(self):
        self.responses = {}
    
    def _prompt(self, question: str, options: Optional[List[str]] = None, default: Optional[str] = None) -> str:
        """Prompt user for input"""
        if options:
            print(f"\n{question}")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            while True:
                choice = input(f"Choose (1-{len(options)}){f' [{default}]' if default else ''}: ").strip()
                # Strip BOM if present (both Unicode and UTF-8 byte sequence)
                if choice.startswith('\ufeff'):
                    choice = choice[1:]
                elif choice.startswith('ï»¿'):
                    choice = choice[3:]
                if not choice and default:
                    return default
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(options):
                        return options[idx]
                    else:
                        print(f"Please enter a number between 1 and {len(options)}")
                except ValueError:
                    print("Please enter a valid number")
        else:
            prompt_text = f"\n{question}"
            if default:
                prompt_text += f" [{default}]"
            prompt_text += ": "
            
            response = input(prompt_text).strip()
            # Strip BOM if present (Windows PowerShell/echo adds UTF-8 BOM)
            # Check for both Unicode BOM (\ufeff) and UTF-8 byte sequence (ï»¿)
            if response.startswith('\ufeff'):
                response = response[1:]
            elif response.startswith('ï»¿'):
                response = response[3:]  # Remove 3-byte UTF-8 BOM sequence
            return response if response else (default or "")
    
    def _validate_pattern(self, pattern: str) -> Tuple[bool, str]:
        """Validate modifier pattern format"""
        # Strip BOM if present (both Unicode and UTF-8 byte sequence)
        if pattern.startswith('\ufeff'):
            pattern = pattern[1:]
        elif pattern.startswith('ï»¿'):
            pattern = pattern[3:]
        
        if not pattern:
            return False, "Pattern cannot be empty"
        
        # Check for wildcard FIRST
        if '(_*)' not in pattern and '(*)' not in pattern:
            return False, "Pattern must contain wildcard: (_*) or (*)"
        
        # Check for valid characters (alphanumeric, dots, underscores, hyphens, wildcards, parentheses)
        import re
        # Allow: letters, numbers, dots, underscores, hyphens, parentheses, asterisks
        if not re.match(r'^[a-zA-Z0-9._\-\(\)\*]+$', pattern):
            return False, "Pattern can only contain letters, numbers, dots, underscores, hyphens, parentheses, and asterisks"
        
        return True, pattern  # Return cleaned pattern
    
    def run_wizard(self) -> Dict:
        """Run interactive wizard"""
        print("\n" + "="*70)
        print("  BIFF Bulk Regex Modifier Generator")
        print("="*70)
        print("\nGenerate <Modifier> XML for pattern-based transformations")
        print("that apply to multiple metrics at once.")
        
        # Step 1: Metric pattern
        print("\n🎯 Step 1: What metrics do you want to modify?")
        print("\n   Examples:")
        print("     • port.1.netdev.eth0.tx_queue(_*)  - Matches tx_queue_0, tx_queue_1, ...")
        print("     • cpu.core(_*).usage                - Matches core0.usage, core1.usage, ...")
        print("     • disk.(_*).io                      - Matches disk.sda.io, disk.sdb.io, ...")
        print("\n   Wildcards:")
        print("     • (_*) - Matches any characters (common)")
        print("     • (*)  - Also matches any characters")
        
        while True:
            pattern = self._prompt("Metric pattern (with wildcard)")
            valid, result = self._validate_pattern(pattern)
            if valid:
                self.responses['pattern'] = result  # Use cleaned pattern
                break
            else:
                print(f"❌ {result}")  # result contains error message
        
        # Step 2: Operation type
        print("\n🔧 Step 2: What transformation?")
        operation_options = [f"{k}: {v}" for k, v in self.MODIFIER_OPERATIONS.items()]
        operation_choice = self._prompt("Operation", operation_options)
        operation = operation_choice.split(':')[0]
        self.responses['operation'] = operation
        
        # Step 3: Configuration based on operation
        if operation == 'normalize':
            print("\n📐 Step 3: Normalization factor")
            print("\n   Common conversions:")
            preset_options = [f"{v['name']}" for v in self.NORMALIZATION_PRESETS.values()]
            preset_choice = self._prompt("Choose preset or custom", preset_options)
            
            # Find the preset key
            preset_key = None
            for key, value in self.NORMALIZATION_PRESETS.items():
                if value['name'] == preset_choice:
                    preset_key = key
                    break
            
            if preset_key == 'custom':
                factor = self._prompt("Enter normalization factor (e.g., 0.00000782)")
                self.responses['normalize_factor'] = float(factor)
                self.responses['normalize_description'] = 'Custom normalization'
            else:
                preset = self.NORMALIZATION_PRESETS[preset_key]
                self.responses['normalize_factor'] = preset['factor']
                self.responses['normalize_description'] = preset['description']
                print(f"   Using: {preset['description']}")
                print(f"   Factor: {preset['factor']}")
        
        elif operation == 'scale':
            print("\n📐 Step 3: Scale factor")
            factor = self._prompt("Enter scale factor (e.g., 1000 to convert KB to bytes)")
            self.responses['scale_factor'] = float(factor)
        
        # Step 4: Precision
        print("\n🎯 Step 4: Output precision")
        precision = self._prompt("Decimal places (0 for integers)", default="0")
        self.responses['precision'] = int(precision)
        
        # Step 5: Advanced options
        print("\n⚙️  Step 5: Advanced options")
        send_on_change = self._prompt(
            "Only send when value changes?",
            ['No (send always)', 'Yes (send on change only)']
        )
        self.responses['send_on_change'] = send_on_change.startswith('Yes')
        
        do_not_send = self._prompt(
            "Suppress sending (transform but don't transmit)?",
            ['No (send normally)', 'Yes (suppress transmission)']
        )
        self.responses['do_not_send'] = do_not_send.startswith('Yes')
        
        return self.responses
    
    def generate_modifier_xml(self, responses: Dict) -> str:
        """Generate <Modifier> XML from wizard responses"""
        pattern = responses['pattern']
        operation = responses['operation']
        precision = responses['precision']
        send_on_change = responses.get('send_on_change', False)
        do_not_send = responses.get('do_not_send', False)
        
        # Build attributes
        attributes = [f'ID="{pattern}"']
        if do_not_send:
            attributes.append('DoNotSend="True"')
        if send_on_change:
            attributes.append('SendOnlyOnChange="True"')
        
        # Build XML
        lines = []
        lines.append(f'<Modifier {" ".join(attributes)}>')
        
        # Add operation-specific elements
        if operation == 'normalize':
            factor = responses['normalize_factor']
            description = responses.get('normalize_description', '')
            lines.append(f'    <Normalize>{factor}</Normalize>  <!-- {description} -->')
        elif operation == 'scale':
            factor = responses['scale_factor']
            lines.append(f'    <Scale>{factor}</Scale>')
        elif operation == 'delta':
            lines.append('    <Delta>True</Delta>')
        elif operation == 'average':
            lines.append('    <Average>True</Average>')
        
        # Add precision
        lines.append(f'    <Precision>{precision}</Precision>')
        
        lines.append('</Modifier>')
        
        return '\n'.join(lines)
    
    def get_usage_notes(self, responses: Dict) -> str:
        """Generate usage notes for the modifier"""
        pattern = responses['pattern']
        operation = responses['operation']
        
        # Extract pattern components for examples
        base_pattern = pattern.replace('(_*)', 'X').replace('(*)', 'X')
        
        notes = f"""
Bulk Regex Modifier Usage Notes:
----------------------------------
Pattern: {pattern}

This modifier will match and transform ALL metrics that fit the pattern.

Example matches:
"""
        # Generate example matches
        if 'queue' in pattern.lower():
            for i in range(3):
                example = pattern.replace('(_*)', str(i)).replace('(*)', str(i))
                notes += f"  • {example}\n"
            notes += "  • ... and all other queue numbers\n"
        elif 'core' in pattern.lower():
            for i in range(3):
                example = pattern.replace('(_*)', str(i)).replace('(*)', str(i))
                notes += f"  • {example}\n"
            notes += "  • ... and all other cores\n"
        else:
            example1 = pattern.replace('(_*)', '0').replace('(*)', '0')
            example2 = pattern.replace('(_*)', '1').replace('(*)', '1')
            exampleN = pattern.replace('(_*)', 'N').replace('(*)', 'N')
            notes += f"  • {example1}\n"
            notes += f"  • {example2}\n"
            notes += f"  • {exampleN}\n"
        
        notes += f"\nOperation: {operation}\n"
        
        if operation == 'normalize':
            factor = responses['normalize_factor']
            notes += f"  Each value will be multiplied by {factor}\n"
            notes += f"  {responses.get('normalize_description', '')}\n"
        
        notes += """
Integration Steps:
  1. Add this <Modifier> XML to your MinionConfig.xml
  2. Place AFTER the collector(s) that generate these metrics
  3. Inside the same <Namespace> as the collectors
  4. Restart Minion to apply transformations

Production Example (Intel Vision Demo):
  Pattern: port.1.netdev.ens1np0.tx_queue(_*)
  Matches: tx_queue_0 through tx_queue_63 (64 queues)
  Normalization: 0.00000782 (Bytes/sec → Mbps)
  Result: 64 metrics automatically normalized with ONE definition

Benefits:
  ✓ Single definition transforms N metrics
  ✓ No code changes when metrics added/removed
  ✓ Consistent transformations across similar metrics
  ✓ Clean separation of collection and transformation logic
"""
        
        return notes
    
    def save_modifier(self, xml: str, output_path: Path) -> None:
        """Save generated modifier XML to file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml)
