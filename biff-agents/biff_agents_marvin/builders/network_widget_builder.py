"""
Network Widget Builder for BIFF Marvin GUI Composer

Creates network monitoring widgets (charts, gauges, text) with throughput
visualization and multi-interface support.

Phase 3 Week 8 Day 4
"""

from .widget_builder import WidgetBuilder
from typing import Optional, Tuple
from pathlib import Path
import sys


class NetworkWidgetBuilder(WidgetBuilder):
    """Builder for network monitoring widgets"""
    
    def __init__(self, config_file: str):
        super().__init__(str(config_file))  # Ensure string
        self.widget_type = 'network'
    
    def build_widget(self) -> str:
        """Build network widget with interactive wizard"""
        print("\n" + "="*70)
        print("Network Widget Builder")
        print("="*70)
        
        # Step 1: Select data source
        print("\nStep 1: Select Network Data Source")
        print("-" * 70)
        
        # Filter for network-related sources
        network_sources = self.discovery.search('network')
        if not network_sources:
            # Also search for interface, throughput, bandwidth
            for term in ['interface', 'throughput', 'bandwidth', 'eth', 'wlan']:
                network_sources.extend(self.discovery.search(term))
        
        if not network_sources:
            # Fallback to all sources
            network_sources = self.discovery.data_sources
        
        if not network_sources:
            print("❌ No data sources found. Create Minion config first.")
            return ""
        
        # Remove duplicates
        seen = set()
        unique_sources = []
        for source in network_sources:
            key = f"{source.namespace}:{source.collector_id}"
            if key not in seen:
                seen.add(key)
                unique_sources.append(source)
        network_sources = unique_sources
        
        print(f"\nAvailable network sources ({len(network_sources)}):")
        for i, source in enumerate(network_sources, 1):
            units = source.suggested_unit or "?"
            print(f"  {i}. {source.namespace}:{source.collector_id} ({units})")
        
        # Get selection
        while True:
            try:
                choice = input("\nSelect source (number): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(network_sources):
                    selected_source = network_sources[idx]
                    break
                print(f"❌ Please enter 1-{len(network_sources)}")
            except (ValueError, EOFError):
                print("❌ Invalid input")
                return ""
        
        print(f"✅ Selected: {selected_source.namespace}:{selected_source.collector_id}")
        
        # Step 2: Widget display style
        print("\n" + "-" * 70)
        print("Step 2: Display Style")
        print("-" * 70)
        print("\nAvailable styles:")
        print("  1. Line Chart (time-series throughput)")
        print("  2. Gauge (current throughput)")
        print("  3. Text (numeric display)")
        
        while True:
            try:
                style_choice = input("\nSelect style (1-3, default=1): ").strip() or "1"
                style_idx = int(style_choice)
                if 1 <= style_idx <= 3:
                    break
                print("❌ Please enter 1-3")
            except (ValueError, EOFError):
                print("❌ Invalid input")
                return ""
        
        style_map = {1: 'chart', 2: 'gauge', 3: 'text'}
        display_style = style_map[style_idx]
        print(f"✅ Style: {display_style}")
        
        # Step 3: Units
        print("\n" + "-" * 70)
        print("Step 3: Units")
        print("-" * 70)
        
        suggested_units = selected_source.suggested_unit
        if suggested_units:
            print(f"\n💡 Suggested units: {suggested_units}")
            use_suggested_units = input("Use suggested units? (Y/n): ").strip().lower()
            if use_suggested_units != 'n':
                units = suggested_units
            else:
                units = input("Enter units: ").strip()
        else:
            units = input("Enter units (e.g., Mbps, KB/s, packets/s): ").strip() or "Mbps"
        
        print(f"✅ Units: {units}")
        
        # Step 4: Chart-specific options
        history_size = 100
        auto_scale = True
        if display_style == 'chart':
            print("\n" + "-" * 70)
            print("Step 4: Chart Options")
            print("-" * 70)
            
            history_input = input("\nHistory size (default=100): ").strip()
            history_size = int(history_input) if history_input else 100
            
            auto_scale_input = input("Auto-scale Y-axis? (Y/n): ").strip().lower()
            auto_scale = auto_scale_input != 'n'
            
            print(f"✅ History: {history_size}, Auto-scale: {auto_scale}")
        
        # Step 5: Range (for gauge and non-auto-scale chart)
        min_val = 0
        max_val = 1000
        if display_style == 'gauge' or (display_style == 'chart' and not auto_scale):
            print("\n" + "-" * 70)
            print("Step 5: Value Range")
            print("-" * 70)
            
            suggested_min_max = selected_source.suggested_min_max
            if suggested_min_max and suggested_min_max[0] is not None:
                print(f"\n💡 Suggested range: {suggested_min_max[0]} - {suggested_min_max[1]}")
                use_suggested = input("Use suggested range? (Y/n): ").strip().lower()
                if use_suggested != 'n':
                    min_val, max_val = suggested_min_max
                else:
                    min_val = float(input("Minimum value: "))
                    max_val = float(input("Maximum value: "))
            else:
                print("\n⚠️  No suggested range available")
                min_val = float(input("Minimum value (default=0): ") or "0")
                max_val = float(input("Maximum value (default=1000): ") or "1000")
            
            print(f"✅ Range: {min_val} - {max_val}")
        
        # Step 6: Grid position
        print("\n" + "-" * 70)
        print(f"Step {'6' if display_style == 'text' else '5' if display_style == 'chart' and auto_scale else '6'}: Grid Position")
        print("-" * 70)
        
        row = int(input("\nRow (default=0): ").strip() or "0")
        col = int(input("Column (default=0): ").strip() or "0")
        
        # Size based on style
        if display_style == 'chart':
            width = int(input("Width (default=4): ").strip() or "4")
            height = int(input("Height (default=2): ").strip() or "2")
        elif display_style == 'gauge':
            width = int(input("Width (default=2): ").strip() or "2")
            height = int(input("Height (default=2): ").strip() or "2")
        else:  # text
            width = int(input("Width (default=2): ").strip() or "2")
            height = int(input("Height (default=1): ").strip() or "1")
        
        print(f"✅ Position: Row={row}, Col={col}, Size={width}x{height}")
        
        # Generate XML based on style
        if display_style == 'chart':
            widget_xml = self._generate_chart_xml(
                selected_source, units, history_size, auto_scale,
                min_val, max_val, row, col, width, height
            )
        elif display_style == 'gauge':
            widget_xml = self._generate_gauge_xml(
                selected_source, min_val, max_val, units,
                row, col, width, height
            )
        else:  # text
            widget_xml = self._generate_text_xml(
                selected_source, units, row, col, width, height
            )
        
        print("\n" + "="*70)
        print("✅ Network widget generated successfully!")
        print("="*70)
        
        return widget_xml
    
    def _generate_chart_xml(self, source, units: str, history_size: int,
                           auto_scale: bool, min_val: float, max_val: float,
                           row: int, col: int, width: int, height: int) -> str:
        """Generate chart-style network widget XML"""
        auto_scale_str = "true" if auto_scale else "false"
        range_xml = ""
        if not auto_scale:
            range_xml = f"""  <MinValue>{min_val}</MinValue>
  <MaxValue>{max_val}</MaxValue>
"""
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Network Chart Widget: {source.collector_id} -->
<Widget Type="LineChart" row="{row}" column="{col}" rowSpan="{height}" columnSpan="{width}">
  <Title>Network Throughput</Title>
  <HistorySize>{history_size}</HistorySize>
  <AutoScale>{auto_scale_str}</AutoScale>
{range_xml}  <ShowLegend>true</ShowLegend>
  <Series>
    <Name>{source.collector_id}</Name>
    <Units>{units}</Units>
    <MinionSrc Namespace="{source.namespace}" ID="{source.collector_id}"/>
  </Series>
</Widget>"""
    
    def _generate_gauge_xml(self, source, min_val: float, max_val: float,
                           units: str, row: int, col: int, width: int, height: int) -> str:
        """Generate gauge-style network widget XML"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Network Gauge Widget: {source.collector_id} -->
<Widget Type="Gauge" row="{row}" column="{col}" rowSpan="{height}" columnSpan="{width}">
  <Title>Network</Title>
  <MinValue>{min_val}</MinValue>
  <MaxValue>{max_val}</MaxValue>
  <Units>{units}</Units>
  <MinionSrc Namespace="{source.namespace}" ID="{source.collector_id}"/>
</Widget>"""
    
    def _generate_text_xml(self, source, units: str,
                          row: int, col: int, width: int, height: int) -> str:
        """Generate text-style network widget XML"""
        units_attr = f' Units="{units}"' if units else ''
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Network Text Widget: {source.collector_id} -->
<Widget Type="Text" row="{row}" column="{col}" rowSpan="{height}" columnSpan="{width}">
  <Title>Network</Title>
  <MinionSrc Namespace="{source.namespace}" ID="{source.collector_id}"/>{units_attr}
</Widget>"""


if __name__ == '__main__':
    """Test network widget builder standalone"""
    if len(sys.argv) < 2:
        print("Usage: python network_widget_builder.py <config_file> [-o output_file]")
        sys.exit(1)
    
    config_file = sys.argv[1]
    output_file = None
    
    if '-o' in sys.argv:
        output_file = sys.argv[sys.argv.index('-o') + 1]
    
    builder = NetworkWidgetBuilder(config_file)
    xml = builder.build_widget()
    
    if xml:
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(xml)
            print(f"\n✅ Saved to: {output_file}")
        else:
            print("\n" + "="*70)
            print("Generated XML:")
            print("="*70)
            print(xml)
