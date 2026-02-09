"""
Memory Widget Builder for BIFF Marvin GUI Composer

Creates memory monitoring widgets (bars, gauges, text) with smart defaults
and zone-based visualization.

Phase 3 Week 8 Day 4
"""

from .widget_builder import WidgetBuilder
from typing import Optional, Tuple
from pathlib import Path
import sys


class MemoryWidgetBuilder(WidgetBuilder):
    """Builder for memory monitoring widgets"""
    
    def __init__(self, config_file: str):
        super().__init__(str(config_file))  # Ensure string
        self.widget_type = 'memory'
    
    def build_widget(self) -> str:
        """Build memory widget with interactive wizard"""
        print("\n" + "="*70)
        print("Memory Widget Builder")
        print("="*70)
        
        # Step 1: Select data source
        print("\nStep 1: Select Memory Data Source")
        print("-" * 70)
        
        # Filter for memory-related sources
        memory_sources = self.discovery.search('memory')
        if not memory_sources:
            # Fallback to all sources
            memory_sources = self.discovery.data_sources
        
        if not memory_sources:
            print("❌ No data sources found. Create Minion config first.")
            return ""
        
        print(f"\nAvailable memory sources ({len(memory_sources)}):")
        for i, source in enumerate(memory_sources, 1):
            units = source.suggested_unit or "?"
            print(f"  {i}. {source.namespace}:{source.collector_id} ({units})")
        
        # Get selection
        while True:
            try:
                choice = input("\nSelect source (number): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(memory_sources):
                    selected_source = memory_sources[idx]
                    break
                print(f"❌ Please enter 1-{len(memory_sources)}")
            except (ValueError, EOFError):
                print("❌ Invalid input")
                return ""
        
        print(f"✅ Selected: {selected_source.namespace}:{selected_source.collector_id}")
        
        # Step 2: Widget display style
        print("\n" + "-" * 70)
        print("Step 2: Display Style")
        print("-" * 70)
        print("\nAvailable styles:")
        print("  1. Bar Chart (horizontal bar with zones)")
        print("  2. Gauge (radial gauge)")
        print("  3. Text (simple text display)")
        
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
        
        style_map = {1: 'bar', 2: 'gauge', 3: 'text'}
        display_style = style_map[style_idx]
        print(f"✅ Style: {display_style}")
        
        # Step 3: Range configuration
        print("\n" + "-" * 70)
        print("Step 3: Value Range")
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
            max_val = float(input("Maximum value (default=100): ") or "100")
        
        print(f"✅ Range: {min_val} - {max_val}")
        
        # Step 4: Units
        print("\n" + "-" * 70)
        print("Step 4: Units")
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
            units = input("Enter units (e.g., MB, %, GB): ").strip() or ""
        
        print(f"✅ Units: {units or '(none)'}")
        
        # Step 5: Color zones (for bar and gauge)
        zones_xml = ""
        if display_style in ['bar', 'gauge']:
            print("\n" + "-" * 70)
            print("Step 5: Color Zones")
            print("-" * 70)
            print("\n💡 Memory zones preset:")
            print("  Green:  0-70% (Good)")
            print("  Yellow: 70-90% (Warning)")
            print("  Red:    90-100% (Critical)")
            
            use_preset = input("\nUse memory preset zones? (Y/n): ").strip().lower()
            if use_preset != 'n':
                # Calculate zone boundaries based on range
                zone1_end = min_val + (max_val - min_val) * 0.70
                zone2_end = min_val + (max_val - min_val) * 0.90
                
                zones_xml = f"""    <Zones>
      <Zone Color="Green" Begin="{min_val}" End="{zone1_end}"/>
      <Zone Color="Yellow" Begin="{zone1_end}" End="{zone2_end}"/>
      <Zone Color="Red" Begin="{zone2_end}" End="{max_val}"/>
    </Zones>"""
                print("✅ Using memory preset zones")
        
        # Step 6: Grid position
        print("\n" + "-" * 70)
        print("Step 6: Grid Position")
        print("-" * 70)
        
        row = int(input("\nRow (default=0): ").strip() or "0")
        col = int(input("Column (default=0): ").strip() or "0")
        
        # Size based on style
        if display_style == 'bar':
            width = int(input("Width (default=4): ").strip() or "4")
            height = int(input("Height (default=1): ").strip() or "1")
        elif display_style == 'gauge':
            width = int(input("Width (default=2): ").strip() or "2")
            height = int(input("Height (default=2): ").strip() or "2")
        else:  # text
            width = int(input("Width (default=2): ").strip() or "2")
            height = int(input("Height (default=1): ").strip() or "1")
        
        print(f"✅ Position: Row={row}, Col={col}, Size={width}x{height}")
        
        # Generate XML based on style
        if display_style == 'gauge':
            widget_xml = self._generate_gauge_xml(
                selected_source, min_val, max_val, units, zones_xml,
                row, col, width, height
            )
        elif display_style == 'bar':
            widget_xml = self._generate_bar_xml(
                selected_source, min_val, max_val, units, zones_xml,
                row, col, width, height
            )
        else:  # text
            widget_xml = self._generate_text_xml(
                selected_source, units, row, col, width, height
            )
        
        print("\n" + "="*70)
        print("✅ Memory widget generated successfully!")
        print("="*70)
        
        return widget_xml
    
    def _generate_gauge_xml(self, source, min_val: float, max_val: float,
                           units: str, zones_xml: str,
                           row: int, col: int, width: int, height: int) -> str:
        """Generate gauge-style memory widget XML"""
        units_attr = f' Units="{units}"' if units else ''
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Memory Gauge Widget: {source.collector_id} -->
<Widget Type="Gauge" row="{row}" column="{col}" rowSpan="{height}" columnSpan="{width}">
  <Title>Memory</Title>
  <MinValue>{min_val}</MinValue>
  <MaxValue>{max_val}</MaxValue>{units_attr}
  <MinionSrc Namespace="{source.namespace}" ID="{source.collector_id}"/>
{zones_xml}
</Widget>"""
    
    def _generate_bar_xml(self, source, min_val: float, max_val: float,
                         units: str, zones_xml: str,
                         row: int, col: int, width: int, height: int) -> str:
        """Generate bar chart memory widget XML"""
        units_attr = f' Units="{units}"' if units else ''
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Memory Bar Widget: {source.collector_id} -->
<Widget Type="ProgressBar" row="{row}" column="{col}" rowSpan="{height}" columnSpan="{width}">
  <Title>Memory</Title>
  <MinValue>{min_val}</MinValue>
  <MaxValue>{max_val}</MaxValue>{units_attr}
  <MinionSrc Namespace="{source.namespace}" ID="{source.collector_id}"/>
{zones_xml}
</Widget>"""
    
    def _generate_text_xml(self, source, units: str,
                          row: int, col: int, width: int, height: int) -> str:
        """Generate text-style memory widget XML"""
        units_attr = f' Units="{units}"' if units else ''
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Memory Text Widget: {source.collector_id} -->
<Widget Type="Text" row="{row}" column="{col}" rowSpan="{height}" columnSpan="{width}">
  <Title>Memory</Title>
  <MinionSrc Namespace="{source.namespace}" ID="{source.collector_id}"/>{units_attr}
</Widget>"""


if __name__ == '__main__':
    """Test memory widget builder standalone"""
    if len(sys.argv) < 2:
        print("Usage: python memory_widget_builder.py <config_file> [-o output_file]")
        sys.exit(1)
    
    config_file = sys.argv[1]
    output_file = None
    
    if '-o' in sys.argv:
        output_file = sys.argv[sys.argv.index('-o') + 1]
    
    builder = MemoryWidgetBuilder(config_file)
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
