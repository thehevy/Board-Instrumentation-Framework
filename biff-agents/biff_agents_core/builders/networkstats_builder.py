"""
Network Statistics Template Builder
Generates simplified network monitoring configurations with pre-configured collectors.

Production Pattern:
    <DynamicCollector Prefix="port.1.netdev.eth0." Frequency="1000">
        <Plugin>
            <PythonFile>Collectors/LinuxNetwork.py</PythonFile>
            <EntryPoint>CollectDeviceStatistics</EntryPoint>
            <Param>device=eth0</Param>
            <Param>source=sysfs|Driver</Param>
        </Plugin>
    </DynamicCollector>
    <Modifier ID="port.1.netdev.eth0.tx_queue(_*)">
        <Normalize>0.00000782</Normalize>
        <Precision>0</Precision>
    </Modifier>

Use Cases:
- Quick network interface monitoring setup
- Common metrics: TX/RX bytes, packets, errors, drops
- Automatic unit conversion (bytes/sec → Mbps)
- Single or multiple interfaces

Production Usage: 5 instances in Intel Vision SUT demo
"""

import sys
import os
from typing import List, Tuple, Optional


class NetworkStatsWizard:
    """Interactive wizard for generating network statistics configurations."""
    
    # Metric levels
    METRIC_LEVELS = {
        '1': ('basic', 'TX/RX bytes only'),
        '2': ('standard', 'TX/RX bytes + packets + errors'),
        '3': ('full', 'All metrics including drops, queue stats'),
    }
    
    # Collection methods
    COLLECTION_METHODS = {
        '1': ('sysfs', 'Read from /sys/class/net (Linux)', 'sysfs'),
        '2': ('plugin', 'Use LinuxNetwork.py plugin (full stats)', 'sysfs|Driver'),
        '3': ('simple', 'Simple file collector (TX/RX only)', 'file'),
    }
    
    def __init__(self):
        self.interfaces = []  # List of interface names
        self.metric_level = "standard"
        self.collection_method = "sysfs"
        self.frequency = "1000"
        self.normalize_throughput = True
        self.port_numbers = []  # Corresponding port numbers for each interface
        
    def _prompt(self, message: str) -> str:
        """Prompt user and strip BOM characters."""
        print(message, end='', flush=True)
        response = input().strip()
        
        # Strip BOM
        if response.startswith('\ufeff'):
            response = response[1:]
        elif response.startswith('ï»¿'):
            response = response[3:]
            
        return response
    
    def run_interactive(self):
        """Run interactive wizard to collect parameters."""
        print("\n" + "="*70)
        print("  Network Statistics Template Generator")
        print("  Simplified setup for common network monitoring")
        print("="*70 + "\n")
        
        # Interface selection
        print("Network Interface Configuration:")
        print("-"*70)
        interfaces_input = self._prompt(
            "Interface names (comma-separated, e.g., eth0,eth1): "
        )
        self.interfaces = [iface.strip() for iface in interfaces_input.split(',') if iface.strip()]
        
        if not self.interfaces:
            print("❌ No interfaces specified, using 'eth0' as default")
            self.interfaces = ['eth0']
        
        # Port number assignment
        print(f"\n📊 {len(self.interfaces)} interface(s) detected")
        use_port_nums = self._prompt(
            "Assign port numbers? (y/n) [default: y]: "
        ).lower()
        
        if use_port_nums != 'n':
            for i, iface in enumerate(self.interfaces):
                port_str = self._prompt(f"  Port number for {iface} [default: {i+1}]: ")
                port_num = port_str if port_str else str(i+1)
                self.port_numbers.append(port_num)
        else:
            self.port_numbers = [str(i+1) for i in range(len(self.interfaces))]
        
        # Metric level selection
        print("\nMetric Level:")
        for key, (level, desc) in self.METRIC_LEVELS.items():
            print(f"  {key}. {level:10} - {desc}")
        
        level_choice = self._prompt("\nMetric level [1-3, default: 2]: ")
        if level_choice in self.METRIC_LEVELS:
            self.metric_level = self.METRIC_LEVELS[level_choice][0]
        else:
            self.metric_level = 'standard'
        
        # Collection method
        print("\nCollection Method:")
        for key, (method, desc, _) in self.COLLECTION_METHODS.items():
            print(f"  {key}. {method:10} - {desc}")
        
        method_choice = self._prompt("\nCollection method [1-3, default: 1]: ")
        if method_choice in self.COLLECTION_METHODS:
            _, _, self.collection_method = self.COLLECTION_METHODS[method_choice]
        else:
            self.collection_method = 'sysfs'
        
        # Frequency
        freq_choice = self._prompt(
            "\nCollection frequency (ms) [default: 1000]: "
        )
        if freq_choice:
            self.frequency = freq_choice
        
        # Normalization
        norm_choice = self._prompt(
            "\nNormalize throughput to Mbps? (y/n) [default: y]: "
        ).lower()
        self.normalize_throughput = norm_choice != 'n'
        
        print("\n" + "="*70 + "\n")
    
    def run_piped(self):
        """Run with piped input (non-interactive mode)."""
        try:
            interfaces_input = self._prompt("")
            self.interfaces = [iface.strip() for iface in interfaces_input.split(',') if iface.strip()]
            
            port_nums_input = self._prompt("")
            if port_nums_input:
                self.port_numbers = [p.strip() for p in port_nums_input.split(',')]
            else:
                self.port_numbers = [str(i+1) for i in range(len(self.interfaces))]
            
            level_choice = self._prompt("")
            if level_choice in self.METRIC_LEVELS:
                self.metric_level = self.METRIC_LEVELS[level_choice][0]
            
            method_choice = self._prompt("")
            if method_choice in self.COLLECTION_METHODS:
                _, _, self.collection_method = self.COLLECTION_METHODS[method_choice]
            
            self.frequency = self._prompt("")
            
            norm_input = self._prompt("")
            self.normalize_throughput = norm_input.lower() != 'n'
            
        except EOFError:
            print("❌ Insufficient input data", file=sys.stderr)
            sys.exit(1)
    
    def generate_collectors(self) -> str:
        """Generate collector XML for all interfaces."""
        xml_lines = []
        
        for iface, port_num in zip(self.interfaces, self.port_numbers):
            xml_lines.append(f"<!-- Network stats for {iface} (port {port_num}) -->")
            
            if self.collection_method == 'file':
                # Simple file-based collector
                xml_lines.extend(self._generate_file_collector(iface, port_num))
            elif self.collection_method in ['sysfs', 'sysfs|Driver']:
                # Plugin-based collector
                xml_lines.extend(self._generate_plugin_collector(iface, port_num))
            
            xml_lines.append("")  # Blank line between interfaces
        
        return '\n'.join(xml_lines)
    
    def _generate_file_collector(self, iface: str, port_num: str) -> List[str]:
        """Generate simple file-based collector (TX/RX only)."""
        lines = [
            f'<DynamicCollector Prefix="port.{port_num}.netdev.{iface}." Frequency="{self.frequency}">',
            f'    <File>/sys/class/net/{iface}/statistics/tx_bytes</File>',
            f'    <File>/sys/class/net/{iface}/statistics/rx_bytes</File>',
            '    <Precision>0</Precision>',
            '</DynamicCollector>'
        ]
        return lines
    
    def _generate_plugin_collector(self, iface: str, port_num: str) -> List[str]:
        """Generate plugin-based collector (full stats)."""
        lines = [
            f'<DynamicCollector Prefix="port.{port_num}.netdev.{iface}." Frequency="{self.frequency}">',
            '    <Plugin>',
            '        <PythonFile>Collectors/LinuxNetwork.py</PythonFile>',
            '        <EntryPoint>CollectDeviceStatistics</EntryPoint>',
            f'        <Param>device={iface}</Param>',
            f'        <Param>source={self.collection_method}</Param>',
            '    </Plugin>',
            '    <Precision>0</Precision>',
            '</DynamicCollector>'
        ]
        return lines
    
    def generate_modifiers(self) -> str:
        """Generate modifier XML for normalization."""
        if not self.normalize_throughput:
            return ""
        
        xml_lines = ["<!-- Normalization: bytes/sec → Mbps -->"]
        
        for iface, port_num in zip(self.interfaces, self.port_numbers):
            # TX throughput
            xml_lines.append(
                f'<Modifier ID="port.{port_num}.netdev.{iface}.tx_bytes">'
            )
            xml_lines.append('    <Normalize>0.00000782</Normalize>')
            xml_lines.append('    <Precision>2</Precision>')
            xml_lines.append('</Modifier>')
            
            # RX throughput
            xml_lines.append(
                f'<Modifier ID="port.{port_num}.netdev.{iface}.rx_bytes">'
            )
            xml_lines.append('    <Normalize>0.00000782</Normalize>')
            xml_lines.append('    <Precision>2</Precision>')
            xml_lines.append('</Modifier>')
            
            # Queue stats (if using plugin)
            if self.collection_method in ['sysfs|Driver']:
                xml_lines.append(
                    f'<Modifier ID="port.{port_num}.netdev.{iface}.tx_queue(_*)">'
                )
                xml_lines.append('    <Normalize>0.00000782</Normalize>')
                xml_lines.append('    <Precision>0</Precision>')
                xml_lines.append('</Modifier>')
                
                xml_lines.append(
                    f'<Modifier ID="port.{port_num}.netdev.{iface}.rx_queue(_*)">'
                )
                xml_lines.append('    <Normalize>0.00000782</Normalize>')
                xml_lines.append('    <Precision>0</Precision>')
                xml_lines.append('</Modifier>')
        
        return '\n'.join(xml_lines)
    
    def generate_namespace_wrapper(self) -> str:
        """Generate complete namespace configuration."""
        collectors = self.generate_collectors()
        modifiers = self.generate_modifiers()
        
        lines = [
            '<Namespace>',
            '    <Name>NetworkStats</Name>',
            f'    <DefaultFrequency>{self.frequency}</DefaultFrequency>',
            '    <TargetConnection IP="localhost" PORT="1100"/>',
            '',
            '    <!-- Collectors -->',
        ]
        
        # Indent collectors
        for line in collectors.split('\n'):
            if line:
                lines.append('    ' + line)
        
        if modifiers:
            lines.append('')
            lines.append('    <!-- Modifiers -->')
            for line in modifiers.split('\n'):
                if line:
                    lines.append('    ' + line)
        
        lines.append('</Namespace>')
        
        return '\n'.join(lines)
    
    def display_result(self, namespace_xml: str, filename: str):
        """Display generated XML and usage information."""
        print("✅ Generated Network Statistics Configuration:\n")
        print(namespace_xml)
        print(f"\n📄 Saved to: {filename}\n")
        
        # Usage notes
        print("="*70)
        print("USAGE NOTES")
        print("="*70)
        
        print(f"\n📊 Configuration Summary:")
        print("-"*70)
        print(f"  Interfaces: {', '.join(self.interfaces)} ({len(self.interfaces)} total)")
        print(f"  Port Numbers: {', '.join(self.port_numbers)}")
        print(f"  Metric Level: {self.metric_level}")
        print(f"  Collection Method: {self.collection_method}")
        print(f"  Frequency: {self.frequency}ms")
        print(f"  Normalization: {'Enabled (bytes/sec → Mbps)' if self.normalize_throughput else 'Disabled'}")
        
        print(f"\n📈 Metrics Collected (per interface):")
        print("-"*70)
        if self.metric_level == 'basic':
            print("  • tx_bytes - Transmitted bytes")
            print("  • rx_bytes - Received bytes")
        elif self.metric_level == 'standard':
            print("  • tx_bytes, rx_bytes - Throughput")
            print("  • tx_packets, rx_packets - Packet counts")
            print("  • tx_errors, rx_errors - Error counts")
        else:  # full
            print("  • tx_bytes, rx_bytes - Throughput")
            print("  • tx_packets, rx_packets - Packet counts")
            print("  • tx_errors, rx_errors - Error counts")
            print("  • tx_dropped, rx_dropped - Drop counts")
            print("  • tx_queue_*, rx_queue_* - Queue statistics")
        
        if self.normalize_throughput:
            print(f"\n🔧 Normalization Applied:")
            print("-"*70)
            print("  Original: bytes per second")
            print("  Normalized: megabits per second (Mbps)")
            print("  Formula: bytes/sec × 0.00000782 = Mbps")
            print("  Example: 1,000,000 bytes/sec = 7.82 Mbps")
        
        print("\n📦 Production Pattern (Intel Vision SUT Demo):")
        print("-"*70)
        print("  • Used for 5 network ports")
        print("  • Pattern: port.<N>.netdev.<iface>.*")
        print("  • DynamicCollector with LinuxNetwork.py plugin")
        print("  • Modifiers for queue stats normalization")
        
        print("\n💡 Integration Steps:")
        print("-"*70)
        print("  1. Copy generated XML to your MinionConfig.xml")
        print("  2. Ensure LinuxNetwork.py exists in Collectors/ (if using plugin)")
        print("  3. Verify interface names match your system (ip link show)")
        print("  4. Start Minion and verify metrics appear")
        print("  5. In Marvin, create widgets with MinionSrc:")
        print(f"     Namespace=\"NetworkStats\" ID=\"port.1.netdev.{self.interfaces[0]}.tx_bytes\"")
        
        if self.collection_method == 'file':
            print("\n⚠️  File Collection Notes:")
            print("-"*70)
            print("  • Requires read access to /sys/class/net/")
            print("  • Limited to basic metrics only")
            print("  • No driver-specific stats available")
        
        print("\n" + "="*70 + "\n")


def run_wizard(output_dir: str = "test_output") -> int:
    """
    Run the network statistics wizard.
    
    Args:
        output_dir: Directory to save generated XML
        
    Returns:
        0 on success, non-zero on failure
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize wizard
    wizard = NetworkStatsWizard()
    
    # Run in appropriate mode
    if sys.stdin.isatty():
        wizard.run_interactive()
    else:
        wizard.run_piped()
    
    # Generate XML
    namespace_xml = wizard.generate_namespace_wrapper()
    filename = "NetworkStats_Config.xml"
    filepath = os.path.join(output_dir, filename)
    
    # Write to file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(namespace_xml)
    except Exception as e:
        print(f"❌ Failed to write file: {e}", file=sys.stderr)
        return 1
    
    # Display result
    wizard.display_result(namespace_xml, filename)
    
    return 0


if __name__ == "__main__":
    sys.exit(run_wizard())
