"""
Monitoring Dashboard Composer

Generates a comprehensive monitoring dashboard with multiple tabs.
Includes overview, detailed metrics, and status indicators.
"""

from pathlib import Path
from typing import Dict, List

from .dashboard_composer import DashboardComposer
from ..utils.minion_discovery import DataSource


class MonitoringDashboardComposer(DashboardComposer):
    """Composer for monitoring dashboards"""
    
    def generate_dashboard(self, output_dir: Path) -> Dict[str, str]:
        """
        Generate monitoring dashboard.
        
        Creates:
        - App.Config.xml: Main application config
        - Tab.Overview.xml: High-level overview with gauges
        - Tab.Details.xml: Detailed metrics with charts
        - Tab.Status.xml: LED status indicators
        
        Args:
            output_dir: Output directory
            
        Returns:
            Dictionary of filename -> content
        """
        if not self.data_sources:
            print("⚠️  No data sources found. Dashboard will be empty.")
            return {'App.Config.xml': self._generate_app_config("Empty Dashboard", [])}
        
        files = {}
        
        # Tab 1: Overview (Gauges)
        files['Tab.Overview.xml'] = self._generate_overview_tab()
        
        # Tab 2: Details (Charts)
        files['Tab.Details.xml'] = self._generate_details_tab()
        
        # Tab 3: Status (LEDs)
        files['Tab.Status.xml'] = self._generate_status_tab()
        
        # Generate app config
        tabs = [
            {'name': 'Overview', 'file': 'Tab.Overview.xml'},
            {'name': 'Details', 'file': 'Tab.Details.xml'},
            {'name': 'Status', 'file': 'Tab.Status.xml'}
        ]
        
        app_config = self._generate_app_config(
            title="BIFF Monitoring Dashboard",
            tabs=tabs
        )
        files['App.Config.xml'] = app_config
        
        return files
    
    def _generate_overview_tab(self) -> str:
        """Generate overview tab with gauges"""
        widgets = []
        
        # Create 2x2 gauges for all sources (4 per row)
        row = 1
        col = 1
        
        for i, source in enumerate(self.data_sources):
            # Get smart defaults
            units = source.suggested_unit
            min_val, max_val = source.suggested_min_max
            if min_val is None:
                min_val, max_val = 0.0, 100.0
            
            title = source.collector_id.replace('.', ' ').title()
            
            widget = self._create_gauge_widget(
                title=title,
                source=source,
                row=row,
                col=col,
                min_val=min_val,
                max_val=max_val,
                units=units,
                row_span=2,
                col_span=2
            )
            widgets.append(widget)
            
            # Move to next position (2 gauges per row in 4-column grid)
            col += 2
            if col > 3:  # Reset to column 1
                col = 1
                row += 2  # Move down 2 rows (gauge height)
        
        return self._generate_tab("Overview", widgets, columns=4)
    
    def _generate_details_tab(self) -> str:
        """Generate details tab with charts"""
        widgets = []
        
        # Group sources by namespace for multi-series charts
        namespace_groups: Dict[str, List[DataSource]] = {}
        for source in self.data_sources:
            if source.namespace not in namespace_groups:
                namespace_groups[source.namespace] = []
            namespace_groups[source.namespace].append(source)
        
        row = 1
        for namespace, sources in namespace_groups.items():
            # Create one chart per namespace showing all sources
            widget = self._create_chart_widget(
                title=f"{namespace} Metrics",
                sources=sources,
                row=row,
                col=1,
                row_span=3,
                col_span=4,
                history=120  # 2 minutes of history
            )
            widgets.append(widget)
            row += 3  # Move down for next chart
        
        return self._generate_tab("Details", widgets, columns=4)
    
    def _generate_status_tab(self) -> str:
        """Generate status tab with LED indicators"""
        widgets = []
        
        # Create 1x1 LEDs in grid pattern (4 per row)
        row = 1
        col = 1
        
        for source in self.data_sources:
            title = source.collector_id.replace('.', ' ').title()
            
            # Determine condition based on metric type
            id_lower = source.collector_id.lower()
            if 'usage' in id_lower or 'percent' in id_lower:
                condition = '&gt;70'  # Alert above 70%
            else:
                condition = '&gt;50'  # Default threshold
            
            widget = self._create_led_widget(
                title=title,
                source=source,
                row=row,
                col=col,
                condition=condition
            )
            widgets.append(widget)
            
            # Move to next position (4 per row)
            col += 1
            if col > 4:
                col = 1
                row += 1
        
        return self._generate_tab("Status", widgets, columns=4)


# CLI entry point
def main():
    """Command-line interface for monitoring composer"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate BIFF Monitoring Dashboard'
    )
    parser.add_argument(
        '-c', '--config',
        type=Path,
        required=True,
        help='Path to MinionConfig.xml'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=Path('monitoring_dashboard'),
        help='Output directory for dashboard files'
    )
    
    args = parser.parse_args()
    
    # Create composer
    composer = MonitoringDashboardComposer(args.config)
    
    # Generate dashboard
    print(f"\n{'='*70}")
    print(f"  BIFF Monitoring Dashboard Generator")
    print(f"{'='*70}\n")
    print(f"Data sources: {len(composer.data_sources)} found")
    print(f"Output directory: {args.output}")
    print()
    
    saved_paths = composer.save_dashboard(args.output)
    
    print(f"\n{'='*70}")
    print(f"✅ Dashboard generated successfully!")
    print(f"{'='*70}")
    print(f"\nGenerated {len(saved_paths)} files:")
    for path in saved_paths:
        print(f"  • {path.name}")
    print(f"\nTo run with Marvin:")
    print(f"  java -jar BIFF.Marvin.jar -i {args.output / 'App.Config.xml'}")
    print()


if __name__ == '__main__':
    main()
