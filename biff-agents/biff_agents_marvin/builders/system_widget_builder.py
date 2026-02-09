"""
System Widget Builder for BIFF Marvin GUI Composer

Creates system information widgets displaying multiple metrics in a
multi-line text panel format.

Phase 3 Week 8 Day 4
"""

from .widget_builder import WidgetBuilder
from typing import Optional, Tuple, List
from pathlib import Path
import sys


class SystemWidgetBuilder(WidgetBuilder):
    """Builder for system information widgets"""
    
    def __init__(self, config_file: str):
        super().__init__(str(config_file))  # Ensure string
        self.widget_type = 'system'
    
    def build_widget(self) -> str:
        """Build system info widget with interactive wizard"""
        print("\n" + "="*70)
        print("System Widget Builder")
        print("="*70)
        print("\nSystem widgets display multiple metrics in a text panel")
        
        # Step 1: Select data sources (multiple)
        print("\nStep 1: Select Data Sources (can select multiple)")
        print("-" * 70)
        
        # Filter for system-related sources
        system_sources = self.discovery.search('system')
        if not system_sources:
            # Also search for other system terms
            for term in ['info', 'host', 'os', 'kernel', 'uptime']:
                system_sources.extend(self.discovery.search(term))
        
        if not system_sources:
            # Fallback to all sources
            system_sources = self.discovery.data_sources
        
        if not system_sources:
            print("❌ No data sources found. Create Minion config first.")
            return ""
        
        # Remove duplicates
        seen = set()
        unique_sources = []
        for source in system_sources:
            key = f"{source.namespace}:{source.collector_id}"
            if key not in seen:
                seen.add(key)
                unique_sources.append(source)
        system_sources = unique_sources
        
        print(f"\nAvailable sources ({len(system_sources)}):")
        for i, source in enumerate(system_sources, 1):
            print(f"  {i}. {source.namespace}:{source.collector_id}")
        
        # Get selections
        selected_sources = []
        print("\nEnter source numbers separated by commas (e.g., 1,3,5)")
        print("Or press Enter to select first 3 sources")
        
        while True:
            try:
                choice = input("\nSelect sources: ").strip()
                
                if not choice:
                    # Default: first 3 sources
                    selected_sources = system_sources[:min(3, len(system_sources))]
                    break
                
                # Parse comma-separated numbers
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                if all(0 <= idx < len(system_sources) for idx in indices):
                    selected_sources = [system_sources[idx] for idx in indices]
                    break
                print(f"❌ Please enter valid numbers 1-{len(system_sources)}")
            except (ValueError, EOFError):
                print("❌ Invalid input")
                return ""
        
        print(f"✅ Selected {len(selected_sources)} sources:")
        for source in selected_sources:
            print(f"   • {source.namespace}:{source.collector_id}")
        
        # Step 2: Panel title
        print("\n" + "-" * 70)
        print("Step 2: Panel Title")
        print("-" * 70)
        
        title = input("\nPanel title (default='System Info'): ").strip() or "System Info"
        print(f"✅ Title: {title}")
        
        # Step 3: Font size
        print("\n" + "-" * 70)
        print("Step 3: Font Size")
        print("-" * 70)
        print("\nAvailable sizes:")
        print("  1. Small (10pt)")
        print("  2. Medium (12pt)")
        print("  3. Large (14pt)")
        
        while True:
            try:
                size_choice = input("\nSelect size (1-3, default=2): ").strip() or "2"
                size_idx = int(size_choice)
                if 1 <= size_idx <= 3:
                    break
                print("❌ Please enter 1-3")
            except (ValueError, EOFError):
                print("❌ Invalid input")
                return ""
        
        size_map = {1: '10', 2: '12', 3: '14'}
        font_size = size_map[size_idx]
        print(f"✅ Font size: {font_size}pt")
        
        # Step 4: Grid position
        print("\n" + "-" * 70)
        print("Step 4: Grid Position")
        print("-" * 70)
        
        row = int(input("\nRow (default=0): ").strip() or "0")
        col = int(input("Column (default=0): ").strip() or "0")
        width = int(input("Width (default=4): ").strip() or "4")
        height = int(input("Height (default=2): ").strip() or "2")
        
        print(f"✅ Position: Row={row}, Col={col}, Size={width}x{height}")
        
        # Generate XML
        widget_xml = self._generate_system_panel_xml(
            selected_sources, title, font_size,
            row, col, width, height
        )
        
        print("\n" + "="*70)
        print("✅ System widget generated successfully!")
        print("="*70)
        
        return widget_xml
    
    def _generate_system_panel_xml(self, sources: List, title: str, font_size: str,
                                   row: int, col: int, width: int, height: int) -> str:
        """Generate system info panel XML"""
        
        # Build MinionSrc elements for each source
        minion_src_xml = []
        for source in sources:
            # Create label from collector ID (capitalize, replace dots/underscores)
            label = source.collector_id.replace('_', ' ').replace('.', ' ').title()
            minion_src_xml.append(
                f'    <MinionSrc Namespace="{source.namespace}" ID="{source.collector_id}"/>'
            )
        
        minion_src_str = '\n'.join(minion_src_xml)
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- System Info Panel: {len(sources)} sources -->
<Widget Type="Text" row="{row}" column="{col}" rowSpan="{height}" columnSpan="{width}">
  <Title>{title}</Title>
  <FontSize>{font_size}</FontSize>
  <Alignment>LEFT</Alignment>
  <MultiLine>true</MultiLine>
{minion_src_str}
</Widget>"""


if __name__ == '__main__':
    """Test system widget builder standalone"""
    if len(sys.argv) < 2:
        print("Usage: python system_widget_builder.py <config_file> [-o output_file]")
        sys.exit(1)
    
    config_file = sys.argv[1]
    output_file = None
    
    if '-o' in sys.argv:
        output_file = sys.argv[sys.argv.index('-o') + 1]
    
    builder = SystemWidgetBuilder(config_file)
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
