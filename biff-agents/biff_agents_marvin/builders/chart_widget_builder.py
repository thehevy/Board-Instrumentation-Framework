"""
Chart Widget Builder

Creates line/area chart widgets for time-series visualization.
Supports multiple data series, legends, and axis configuration.
"""

from pathlib import Path
from typing import Optional, Dict, List

from .widget_builder import WidgetBuilder
from ..utils.minion_discovery import DataSource


class ChartWidgetBuilder(WidgetBuilder):
    """Builder for line/area chart widgets"""
    
    WIDGET_FILE = "Chart/LineChart.xml"
    
    CHART_TYPES = [
        ("Line Chart", "Chart/LineChart.xml"),
        ("Area Chart", "Chart/AreaChart.xml"),
        ("Stacked Area", "Chart/StackedAreaChart.xml"),
    ]
    
    def build_widget(self) -> str:
        """
        Interactive wizard to create chart widget.
        
        Returns:
            Widget XML string
        """
        config = {}
        
        # Step 1: Title
        config['title'] = self._prompt("Chart title", "Metrics Over Time")
        
        # Step 2: Chart type
        print("\n📊 Step 2: Chart Type")
        chart_idx = self._prompt_choice(
            "Select chart type",
            [name for name, _ in self.CHART_TYPES],
            default=1
        )
        config['chart_file'] = self.CHART_TYPES[chart_idx][1]
        config['chart_type'] = self.CHART_TYPES[chart_idx][0]
        
        # Step 3: Data series
        print("\n📈 Step 3: Data Series")
        print("Add data sources to plot on the chart.")
        
        config['series'] = self._collect_data_series()
        
        if not config['series']:
            print("❌ Error: Chart requires at least one data series")
            return ""
        
        # Step 4: X-Axis (time series)
        print("\n⏱️  Step 4: Time Range")
        config['history_seconds'] = self._prompt(
            "History to display (seconds)",
            "60"
        )
        
        # Step 5: Y-Axis
        print("\n📏 Step 5: Y-Axis Range")
        
        auto_scale = self._prompt("Auto-scale Y-axis? (y/n)", "y").lower()
        
        if auto_scale == 'y':
            config['auto_scale'] = True
        else:
            config['auto_scale'] = False
            config['y_min'] = self._prompt("Y-axis minimum", "0")
            config['y_max'] = self._prompt("Y-axis maximum", "100")
        
        # Step 6: Legend
        print("\n📋 Step 6: Legend")
        config['show_legend'] = self._prompt("Show legend? (y/n)", "y").lower() == 'y'
        
        # Step 7: Grid position
        print("\n📍 Step 7: Grid Position")
        config['row'] = int(self._prompt("Grid row", "1"))
        config['column'] = int(self._prompt("Grid column", "1"))
        
        col_span = self._prompt("Column span (width)", "4")
        row_span = self._prompt("Row span (height)", "2")
        config['col_span'] = int(col_span) if col_span else 1
        config['row_span'] = int(row_span) if row_span else 1
        
        # Print summary
        self.print_summary("Chart Widget", config)
        
        # Generate XML
        return self._generate_xml(config)
    
    def _collect_data_series(self) -> List[Dict]:
        """
        Collect data series from user.
        
        Returns:
            List of series dictionaries
        """
        series_list = []
        
        print("\n   Add data series (at least 1 required)")
        
        while True:
            series_num = len(series_list) + 1
            print(f"\n   Series {series_num}:")
            
            # Select data source
            source = self.select_data_source(hint=f"Select data for series {series_num}")
            
            if not source:
                if series_list:
                    # User chose to skip, we have at least one series
                    break
                else:
                    # No series yet, need at least one
                    print("   ⚠️  At least one series is required")
                    continue
            
            # Series label
            default_label = f"{source.namespace}:{source.collector_id}"
            label = self._prompt(f"  Series label", default_label)
            
            # Line color
            color_choice = self._prompt_choice(
                "  Line color",
                ["Blue", "Green", "Red", "Orange", "Purple", "Cyan"],
                default=1
            )
            
            color_map = {
                0: '#0000FF',  # Blue
                1: '#00FF00',  # Green
                2: '#FF0000',  # Red
                3: '#FF8800',  # Orange
                4: '#8800FF',  # Purple
                5: '#00FFFF',  # Cyan
            }
            
            series_list.append({
                'source': source,
                'label': label,
                'color': color_map[color_choice]
            })
            
            # Ask if more series needed
            if len(series_list) >= 1:
                add_more = self._prompt("  Add another series? (y/n)", "n").lower()
                if add_more != 'y':
                    break
        
        return series_list
    
    def _generate_xml(self, config: Dict) -> str:
        """
        Generate chart widget XML from configuration.
        
        Args:
            config: Widget configuration
            
        Returns:
            XML string
        """
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
            f'  Chart Widget: {config["title"]}',
            f'  Type: {config["chart_type"]}',
            f'  Generated by BIFF Agents - Marvin GUI Composer',
            '-->',
            f'<Widget File="{config["chart_file"]}" {position}>',
        ]
        
        # Add title
        if config['title']:
            xml_lines.append(f'    <Title>{config["title"]}</Title>')
        
        # Add X-axis (time)
        xml_lines.append(f'    <xAxisLabel>Time</xAxisLabel>')
        xml_lines.append(f'    <HistorySize>{config["history_seconds"]}</HistorySize>')
        
        # Add Y-axis
        xml_lines.append(f'    <yAxisLabel>Value</yAxisLabel>')
        
        if not config.get('auto_scale', True):
            xml_lines.append(f'    <yAxisMinValue>{config["y_min"]}</yAxisMinValue>')
            xml_lines.append(f'    <yAxisMaxValue>{config["y_max"]}</yAxisMaxValue>')
        
        # Add legend
        if config.get('show_legend', True):
            xml_lines.append('    <ShowLegend>true</ShowLegend>')
        
        # Add series
        xml_lines.append('    <Series>')
        
        for series in config['series']:
            source = series['source']
            xml_lines.append('        <SeriesSet>')
            xml_lines.append(f'            <Title>{series["label"]}</Title>')
            xml_lines.append(f'            {self._generate_minion_src(source)}')
            xml_lines.append(f'            <Color>{series["color"]}</Color>')
            xml_lines.append('        </SeriesSet>')
        
        xml_lines.append('    </Series>')
        
        # Close widget
        xml_lines.append('</Widget>')
        
        return '\n'.join(xml_lines)


# CLI entry point
def main():
    """Command-line interface for chart widget builder"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Create Marvin chart widget configuration'
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
    builder = ChartWidgetBuilder(args.config)
    
    # Generate widget
    xml = builder.create_widget(args.output)
    
    if xml and not args.output:
        # Print to stdout if no output file
        print("\nGenerated XML:")
        print("=" * 70)
        print(xml)


if __name__ == '__main__':
    main()
