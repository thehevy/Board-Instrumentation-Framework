"""
Quickstart Dashboard Composer

Generates a simple dashboard for getting started with BIFF.
Single tab with gauges and text displays for all discovered data sources.
"""

from pathlib import Path
from typing import Dict

from .dashboard_composer import DashboardComposer


class QuickstartDashboardComposer(DashboardComposer):
    """Composer for quickstart dashboards"""
    
    def generate_dashboard(self, output_dir: Path) -> Dict[str, str]:
        """
        Generate quickstart dashboard.
        
        Creates:
        - App.Config.xml: Main application config
        - Tab.Overview.xml: Single overview tab with all metrics
        
        Layout (4 columns):
        Row 1-2: Gauges (2x2 each) for first 2 metrics
        Row 3: Text displays (1x1 each) for remaining metrics
        
        Args:
            output_dir: Output directory
            
        Returns:
            Dictionary of filename -> content
        """
        if not self.data_sources:
            print("⚠️  No data sources found. Dashboard will be empty.")
        
        files = {}
        
        # Generate tab content
        widgets = []
        
        # Add gauges for first 2 sources (2x2 each, side by side)
        for i, source in enumerate(self.data_sources[:2]):
            col = (i * 2) + 1  # Column 1 or 3
            
            # Get smart defaults
            units = source.suggested_unit
            min_val, max_val = source.suggested_min_max
            if min_val is None:
                min_val, max_val = 0.0, 100.0
            
            title = source.collector_id.replace('.', ' ').title()
            
            widget = self._create_gauge_widget(
                title=title,
                source=source,
                row=1,
                col=col,
                min_val=min_val,
                max_val=max_val,
                units=units,
                row_span=2,
                col_span=2
            )
            widgets.append(widget)
        
        # Add text displays for remaining sources (1x1 each)
        current_row = 3
        current_col = 1
        max_cols = 4
        
        for source in self.data_sources[2:]:
            title = source.collector_id.replace('.', ' ').title()
            units = source.suggested_unit
            
            widget = self._create_text_widget(
                title=title,
                source=source,
                row=current_row,
                col=current_col,
                units=units
            )
            widgets.append(widget)
            
            # Move to next position
            current_col += 1
            if current_col > max_cols:
                current_col = 1
                current_row += 1
        
        # Generate tab file
        tab_content = self._generate_tab(
            tab_name="Overview",
            widgets=widgets,
            columns=4
        )
        files['Tab.Overview.xml'] = tab_content
        
        # Generate app config
        tabs = [
            {'name': 'Overview', 'file': 'Tab.Overview.xml'}
        ]
        
        app_config = self._generate_app_config(
            title="BIFF Quickstart Dashboard",
            tabs=tabs
        )
        files['App.Config.xml'] = app_config
        
        return files


# CLI entry point
def main():
    """Command-line interface for quickstart composer"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate BIFF Quickstart Dashboard'
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
        default=Path('quickstart_dashboard'),
        help='Output directory for dashboard files'
    )
    
    args = parser.parse_args()
    
    # Create composer
    composer = QuickstartDashboardComposer(args.config)
    
    # Generate dashboard
    print(f"\n{'='*70}")
    print(f"  BIFF Quickstart Dashboard Generator")
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
