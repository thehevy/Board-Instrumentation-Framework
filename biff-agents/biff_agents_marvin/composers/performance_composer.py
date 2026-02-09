"""
Performance Dashboard Composer for BIFF Marvin GUI

Generates performance-focused 2-tab dashboard:
- Tab 1: System Overview (CPU, Memory, System Info)
- Tab 2: Network Performance (Throughput charts, Status LEDs)

Phase 3 Week 8 Day 4
"""

from .dashboard_composer import DashboardComposer
from pathlib import Path


class PerformanceDashboardComposer(DashboardComposer):
    """Composer for performance-focused dashboards"""
    
    def __init__(self, config_file: str):
        super().__init__(str(config_file))  # Ensure string
        self.template_name = 'performance'
    
    def generate_dashboard(self, output_dir: str) -> dict:
        """Generate performance dashboard with 2 tabs"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        sources = self.data_sources
        if not sources:
            print("❌ No data sources found. Generate Minion config first.")
            return {}
        
        print(f"\nData sources: {len(sources)} found")
        
        # Separate sources by type
        cpu_sources = [s for s in sources if 'cpu' in s.collector_id.lower()]
        memory_sources = [s for s in sources if 'memory' in s.collector_id.lower() or 'mem' in s.collector_id.lower()]
        network_sources = [s for s in sources if 'network' in s.collector_id.lower() or 'net' in s.collector_id.lower() or 'eth' in s.collector_id.lower()]
        other_sources = [s for s in sources if s not in cpu_sources + memory_sources + network_sources]
        
        # Generate Tab 1: System Overview
        tab1_widgets = self._generate_system_overview_tab(cpu_sources, memory_sources, other_sources)
        tab1_xml = self._generate_tab('Tab.System.xml', tab1_widgets, 4)
        tab1_file = output_path / 'Tab.System.xml'
        tab1_file.write_text(tab1_xml, encoding='utf-8')
        print(f"✅ Generated: Tab.System.xml")
        
        # Generate Tab 2: Network Performance
        if network_sources:
            tab2_widgets = self._generate_network_performance_tab(network_sources)
            tab2_xml = self._generate_tab('Tab.Network.xml', tab2_widgets, 4)
            tab2_file = output_path / 'Tab.Network.xml'
            tab2_file.write_text(tab2_xml, encoding='utf-8')
            print(f"✅ Generated: Tab.Network.xml")
            tabs = [
                {'file': 'Tab.System.xml', 'name': 'System Overview'},
                {'file': 'Tab.Network.xml', 'name': 'Network Performance'}
            ]
        else:
            print("⚠️  No network sources found, skipping network tab")
            tabs = [{'file': 'Tab.System.xml', 'name': 'System Overview'}]
        
        # Generate App.Config.xml
        app_config = self._generate_app_config('Performance Dashboard', tabs)
        app_file = output_path / 'App.Config.xml'
        app_file.write_text(app_config, encoding='utf-8')
        print(f"✅ Generated: App.Config.xml")
        
        print(f"\nGenerated {len(tabs) + 1} files")
        return {
            'App.Config.xml': app_config,
            'tabs': tabs
        }
    
    def _generate_system_overview_tab(self, cpu_sources, memory_sources, other_sources):
        """Generate System Overview tab widgets"""
        widgets = []
        current_row = 0
        
        # Row 0: CPU Gauges (2x2 each, up to 2 CPUs)
        cpu_count = 0
        for source in cpu_sources[:2]:  # Max 2 CPU gauges
            col = cpu_count * 2
            # Determine range
            min_val = 0
            max_val = 100
            units = '%'
            if source.suggested_min_max and source.suggested_min_max[0] is not None:
                min_val, max_val = source.suggested_min_max
            if source.suggested_unit:
                units = source.suggested_unit
            
            widget = self._create_gauge_widget(
                'CPU', source, row=current_row, col=col, 
                min_val=min_val, max_val=max_val, units=units,
                row_span=2, col_span=2
            )
            widgets.append(widget)
            cpu_count += 1
        
        # Row 2: Memory Bar Charts (4x1 each, or 2x2 if only one)
        if memory_sources:
            current_row = 2
            if len(memory_sources) == 1:
                # Single memory: use 4x1 bar
                widget = self._create_memory_bar_widget(
                    memory_sources[0], row=current_row, col=0, width=4, height=1
                )
                widgets.append(widget)
                current_row += 1
            else:
                # Multiple memory: 2x1 bars
                for i, source in enumerate(memory_sources[:2]):
                    col = i * 2
                    widget = self._create_memory_bar_widget(
                        source, row=current_row, col=col, width=2, height=1
                    )
                    widgets.append(widget)
                current_row += 1
        
        # Row 3+: System Info Panel (4x2 if we have other sources)
        if other_sources:
            current_row = max(3, current_row)
            # Create system info panel with up to 3 sources
            system_sources = other_sources[:3]
            widget = self._create_system_info_widget(
                system_sources, row=current_row, col=0, width=4, height=2
            )
            widgets.append(widget)
        
        return widgets
    
    def _generate_network_performance_tab(self, network_sources):
        """Generate Network Performance tab widgets"""
        widgets = []
        current_row = 0
        
        # Create time-series charts for each network source (4x2 each)
        for i, source in enumerate(network_sources[:3]):  # Max 3 charts
            widget = self._create_chart_widget(
                'Network', [source], row=current_row, col=0,
                row_span=2, col_span=4, history=100
            )
            widgets.append(widget)
            current_row += 2
        
        # Row 6+: Status LEDs for all network interfaces (1x1 each)
        led_row = current_row
        for i, source in enumerate(network_sources):
            col = i % 4
            row = led_row + (i // 4)
            widget = self._create_led_widget(
                source.collector_id, source, row=row, col=col, condition=">70"
            )
            widgets.append(widget)
        
        return widgets
    
    def _create_memory_bar_widget(self, source, row: int, col: int, width: int, height: int) -> str:
        """Create memory bar chart widget"""
        # Determine range based on source
        min_val = 0
        max_val = 100
        units = '%'
        
        if source.suggested_units:
            units = source.suggested_units
        if source.suggested_min_max and source.suggested_min_max[0] is not None:
            min_val, max_val = source.suggested_min_max
        
        # Memory zones: Green 0-70%, Yellow 70-90%, Red 90-100%
        zone1_end = min_val + (max_val - min_val) * 0.70
        zone2_end = min_val + (max_val - min_val) * 0.90
        
        zones_xml = f"""    <Zones>
      <Zone Color="Green" Begin="{min_val}" End="{zone1_end}"/>
      <Zone Color="Yellow" Begin="{zone1_end}" End="{zone2_end}"/>
      <Zone Color="Red" Begin="{zone2_end}" End="{max_val}"/>
    </Zones>"""
        
        return f"""  <Widget Type="ProgressBar" row="{row}" column="{col}" rowSpan="{height}" columnSpan="{width}">
    <Title>Memory</Title>
    <MinValue>{min_val}</MinValue>
    <MaxValue>{max_val}</MaxValue>
    <Units>{units}</Units>
    <MinionSrc Namespace="{source.namespace}" ID="{source.collector_id}"/>
{zones_xml}
  </Widget>"""
    
    def _create_system_info_widget(self, sources, row: int, col: int, width: int, height: int) -> str:
        """Create system info panel with multiple sources"""
        minion_src_xml = []
        for source in sources:
            minion_src_xml.append(
                f'    <MinionSrc Namespace="{source.namespace}" ID="{source.collector_id}"/>'
            )
        minion_src_str = '\n'.join(minion_src_xml)
        
        return f"""  <Widget Type="Text" row="{row}" column="{col}" rowSpan="{height}" columnSpan="{width}">
    <Title>System Info</Title>
    <FontSize>12</FontSize>
    <Alignment>LEFT</Alignment>
    <MultiLine>true</MultiLine>
{minion_src_str}
  </Widget>"""


if __name__ == '__main__':
    """Test performance dashboard composer standalone"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Performance Dashboard')
    parser.add_argument('-c', '--config', required=True, help='Minion config file')
    parser.add_argument('-o', '--output', default='performance_dashboard', 
                       help='Output directory')
    
    args = parser.parse_args()
    
    composer = PerformanceDashboardComposer(args.config)
    result = composer.generate_dashboard(args.output)
    
    if result:
        print(f"\n✅ Performance dashboard generated in: {args.output}")
        print(f"   Files: App.Config.xml + {len(result.get('tabs', []))} tabs")
