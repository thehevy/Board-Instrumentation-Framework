"""
Gauge Widget Builder

Creates circular gauge widgets for metric visualization.
Supports radial gauges with color zones, min/max ranges, and dynamic data binding.
"""

from pathlib import Path
from typing import Optional, Dict, List

from .widget_builder import WidgetBuilder
from ..utils.minion_discovery import DataSource


class GaugeWidgetBuilder(WidgetBuilder):
    """Builder for circular gauge widgets"""
    
    WIDGET_FILE = "Gauge/Radial1Horizontal.xml"
    
    GAUGE_STYLES = [
        ("Radial (Horizontal)", "Gauge/Radial1Horizontal.xml"),
        ("Radial (Vertical)", "Gauge/Radial1Vertical.xml"),
        ("Radial (Large)", "Gauge/Radial2.xml"),
        ("Simple Radial", "Gauge/RadialBasic.xml"),
    ]
    
    def build_widget(self) -> str:
        """
        Interactive wizard to create gauge widget.
        
        Returns:
            Widget XML string
        """
        config = {}
        
        # Step 1: Title/Label
        config['title'] = self._prompt("Gauge title", "Metric")
        
        # Step 2: Data source selection
        print("\n📊 Step 2: Data Source")
        print("Select a data source to display on the gauge.")
        
        source = self.select_data_source(hint="Select metric to visualize")
        config['source'] = source
        
        if not source:
            print("❌ Error: Gauge widget requires a data source")
            return ""
        
        # Step 3: Range (min/max)
        print("\n📏 Step 3: Value Range")
        
        # Use smart defaults from data source
        suggested_min, suggested_max = source.suggested_min_max
        
        if suggested_min is not None and suggested_max is not None:
            print(f"   Suggested range: {suggested_min} - {suggested_max}")
            use_suggested = self._prompt("Use suggested range? (y/n)", "y").lower()
            
            if use_suggested == 'y':
                config['min_value'] = str(int(suggested_min))
                config['max_value'] = str(int(suggested_max))
            else:
                config['min_value'] = self._prompt("Minimum value", "0")
                config['max_value'] = self._prompt("Maximum value", "100")
        else:
            print("   No suggested range available")
            config['min_value'] = self._prompt("Minimum value", "0")
            config['max_value'] = self._prompt("Maximum value", "100")
        
        # Step 4: Units
        print("\n📐 Step 4: Units")
        
        suggested_unit = source.suggested_unit
        if suggested_unit:
            print(f"   Suggested unit: {suggested_unit}")
            config['units'] = self._prompt("Units", suggested_unit)
        else:
            config['units'] = self._prompt("Units (e.g., %, °C, MB)", "")
        
        # Step 5: Major Ticks
        config['major_ticks'] = self._prompt("Major tick count", "10")
        
        # Step 6: Color Zones
        print("\n🎨 Step 5: Color Zones")
        print("Define color zones for visual indication (e.g., green=good, yellow=warning, red=critical)")
        
        add_zones = self._prompt("Add color zones? (y/n)", "y").lower()
        
        if add_zones == 'y':
            config['zones'] = self._collect_color_zones(
                float(config['min_value']),
                float(config['max_value'])
            )
        else:
            config['zones'] = []
        
        # Step 7: Gauge Style
        print("\n🎨 Step 6: Gauge Style")
        style_idx = self._prompt_choice(
            "Select gauge style",
            [name for name, _ in self.GAUGE_STYLES],
            default=1
        )
        config['gauge_file'] = self.GAUGE_STYLES[style_idx][1]
        
        # Step 8: Grid position
        print("\n📍 Step 7: Grid Position")
        config['row'] = int(self._prompt("Grid row", "1"))
        config['column'] = int(self._prompt("Grid column", "1"))
        
        col_span = self._prompt("Column span (width)", "2")
        row_span = self._prompt("Row span (height)", "2")
        config['col_span'] = int(col_span) if col_span else 1
        config['row_span'] = int(row_span) if row_span else 1
        
        # Print summary
        self.print_summary("Gauge Widget", config)
        
        # Generate XML
        return self._generate_xml(config)
    
    def _collect_color_zones(self, min_val: float, max_val: float) -> List[Dict]:
        """
        Collect color zone definitions from user.
        
        Args:
            min_val: Minimum gauge value
            max_val: Maximum gauge value
            
        Returns:
            List of zone dictionaries
        """
        zones = []
        
        print(f"\n   Gauge range: {min_val} - {max_val}")
        print("   Common patterns:")
        print("     • 3 zones: Green (0-70%), Yellow (70-90%), Red (90-100%)")
        print("     • 2 zones: Green (0-80%), Red (80-100%)")
        
        use_preset = self._prompt("Use 3-zone preset? (y/n)", "y").lower()
        
        if use_preset == 'y':
            # 3-zone preset: Green, Yellow, Red
            range_span = max_val - min_val
            zones.append({
                'start': min_val,
                'end': min_val + (range_span * 0.7),
                'color': 'rgb(0, 255, 0)'  # Green
            })
            zones.append({
                'start': min_val + (range_span * 0.7),
                'end': min_val + (range_span * 0.9),
                'color': 'rgb(255, 255, 0)'  # Yellow
            })
            zones.append({
                'start': min_val + (range_span * 0.9),
                'end': max_val,
                'color': 'rgb(255, 0, 0)'  # Red
            })
        else:
            # Custom zones
            print("\n   Enter zones (type 'done' when finished)")
            zone_num = 1
            
            while True:
                print(f"\n   Zone {zone_num}:")
                start = self._prompt("  Start value (or 'done')", "")
                
                if start.lower() == 'done':
                    break
                
                end = self._prompt("  End value", "")
                
                color_choice = self._prompt_choice(
                    "  Color",
                    ["Green", "Yellow", "Red", "Blue", "Orange"],
                    default=1
                )
                
                color_map = {
                    0: 'rgb(0, 255, 0)',    # Green
                    1: 'rgb(255, 255, 0)',  # Yellow
                    2: 'rgb(255, 0, 0)',    # Red
                    3: 'rgb(0, 0, 255)',    # Blue
                    4: 'rgb(255, 165, 0)'   # Orange
                }
                
                zones.append({
                    'start': float(start),
                    'end': float(end),
                    'color': color_map[color_choice]
                })
                
                zone_num += 1
        
        return zones
    
    def _generate_xml(self, config: Dict) -> str:
        """
        Generate gauge widget XML from configuration.
        
        Args:
            config: Widget configuration
            
        Returns:
            XML string
        """
        source = config['source']
        
        # Build position attributes
        position = self._generate_position(
            config['row'],
            config['column'],
            config.get('col_span', 1),
            config.get('row_span', 1)
        )
        
        # Start widget
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<!--',
            f'  Gauge Widget: {config["title"]}',
            f'  Generated by BIFF Agents - Marvin GUI Composer',
            '-->',
            f'<Widget File="{config["gauge_file"]}" {position}>',
        ]
        
        # Add title
        if config['title']:
            xml_lines.append(f'    <Title>{config["title"]}</Title>')
        
        # Add data source
        xml_lines.append(f'    {self._generate_minion_src(source)}')
        
        # Add range
        xml_lines.append(f'    <MinValue>{config["min_value"]}</MinValue>')
        xml_lines.append(f'    <MaxValue>{config["max_value"]}</MaxValue>')
        
        # Add units
        if config.get('units'):
            xml_lines.append(f'    <UnitsOverride>{config["units"]}</UnitsOverride>')
        
        # Add major ticks
        xml_lines.append(f'    <MajorTicks>{config["major_ticks"]}</MajorTicks>')
        
        # Add color zones
        if config.get('zones'):
            xml_lines.append('    <Zones>')
            for zone in config['zones']:
                xml_lines.append(f'        <Zone>')
                xml_lines.append(f'            <Start>{zone["start"]}</Start>')
                xml_lines.append(f'            <End>{zone["end"]}</End>')
                xml_lines.append(f'            <Color>{zone["color"]}</Color>')
                xml_lines.append(f'        </Zone>')
            xml_lines.append('    </Zones>')
        
        # Close widget
        xml_lines.append('</Widget>')
        
        return '\n'.join(xml_lines)


# CLI entry point
def main():
    """Command-line interface for gauge widget builder"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Create Marvin gauge widget configuration'
    )
    parser.add_argument(
        '-c', '--config',
        type=Path,
        help='Path to MinionConfig.xml for data source discovery'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file path for widget XML'
    )
    
    args = parser.parse_args()
    
    # Create builder
    builder = GaugeWidgetBuilder(args.config)
    
    # Generate widget
    xml = builder.create_widget(args.output)
    
    if xml and not args.output:
        # Print to stdout if no output file
        print("\nGenerated XML:")
        print("=" * 70)
        print(xml)


if __name__ == '__main__':
    main()
