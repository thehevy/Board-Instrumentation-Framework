"""
Generator for Marvin application configuration files.

Creates Application.xml, Grid files, and Tab definitions for Marvin GUI.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Dict, List
from .base_generator import BaseGenerator


class MarvinApplicationGenerator(BaseGenerator):
    """Generate Marvin application configuration XML"""
    
    # Widget templates for different collector types
    WIDGET_TEMPLATES = {
        "RandomVal": {
            "type": "SteelSimpleGauge",
            "file": "Gauge/GaugeSimple.xml",
            "title": "Random Value",
            "min": 0,
            "max": 100,
            "unit": "value",
            "decimals": 0
        },
        "Timer": {
            "type": "SteelSimpleGauge",
            "file": "Gauge/GaugeSimple.xml",
            "title": "Timer",
            "min": 0,
            "max": 10000,
            "unit": "ms",
            "decimals": 0
        },
        "CPU": {
            "type": "SteelSimpleGauge",
            "file": "Gauge/GaugeRadial.xml",
            "title": "CPU Usage",
            "min": 0,
            "max": 100,
            "unit": "%",
            "decimals": 1
        },
        "Memory": {
            "type": "Text",
            "file": "Text/Text.xml",
            "title": "Memory"
        },
        "Network": {
            "type": "Text",
            "file": "Text/Text.xml",
            "title": "Network"
        },
        "Storage": {
            "type": "SteelSimpleGauge",
            "file": "Gauge/GaugeRadial.xml",
            "title": "Disk Usage",
            "min": 0,
            "max": 100,
            "unit": "%",
            "decimals": 1
        }
    }
    
    def generate_application(self, config: Dict) -> str:
        """Generate Application.xml
        
        Args:
            config: Configuration dict with:
                - minion_namespace: str
                - output_dir: Path
        
        Returns:
            XML string
        """
        root = ET.Element("Marvin")
        
        # Application element
        app = ET.SubElement(root, "Application")
        app.set("Scale", "auto")
        
        # Creation size
        size = ET.SubElement(app, "CreationSize")
        size.set("Width", "1920")
        size.set("Height", "1050")
        
        # Network port
        network = ET.SubElement(app, "Network")
        network.set("Port", str(config.get("marvin_port", 52001)))
        
        # Title
        title = ET.SubElement(app, "Title")
        title.text = f"BIFF Quick Start - {config.get('minion_namespace', 'QuickStart')}"
        
        # Padding
        padding = ET.SubElement(app, "Padding")
        padding.set("top", "5")
        padding.set("bottom", "5")
        padding.set("right", "5")
        padding.set("left", "5")
        
        # Stylesheet
        stylesheet = ET.SubElement(app, "StyleSheet")
        stylesheet.text = "Widget/Modena-BIFF.css"
        
        # Heartbeat
        heartbeat = ET.SubElement(app, "Heartbeat")
        heartbeat.set("Rate", "10")
        
        # Tasks
        tasks = ET.SubElement(app, "Tasks")
        tasks.set("Enabled", "True")
        
        # Main menu
        menu = ET.SubElement(app, "MainMenu")
        menu.set("Show", "True")
        
        # Tabs
        tabs = ET.SubElement(app, "Tabs")
        
        # Add Quick Start tab
        tab = ET.SubElement(tabs, "Tab")
        tab.set("ID", "Tab.QuickStart")
        
        return self._prettify(root)
    
    def generate_tab(self, config: Dict) -> str:
        """Generate Tab.QuickStart.xml
        
        Args:
            config: Configuration dict
        
        Returns:
            XML string
        """
        root = ET.Element("MarvinExternalFile")
        
        # Tab element
        tab = ET.SubElement(root, "Tab")
        
        # Title
        title = ET.SubElement(tab, "Title")
        title.text = f"{config.get('minion_namespace', 'QuickStart')} Dashboard"
        
        # Grid reference
        grid = ET.SubElement(tab, "Grid")
        grid.set("row", "1")
        grid.set("column", "1")
        grid.set("File", "Grid.QuickStart.xml")
        
        return self._prettify(root)
    
    def generate_grid(self, config: Dict) -> str:
        """Generate Grid.QuickStart.xml with widgets
        
        Args:
            config: Configuration dict with:
                - minion_namespace: str
                - collectors: List[str]
        
        Returns:
            XML string
        """
        root = ET.Element("MarvinExternalFile")
        
        # Grid element
        grid = ET.SubElement(root, "Grid")
        grid.set("Align", "N")
        grid.set("hgap", "10")
        grid.set("vgap", "10")
        
        # Add widgets for each collector
        collectors = config.get("collectors", [])
        namespace = config.get("minion_namespace", "QuickStart")
        
        # Layout: 3 columns max
        row = 1
        col = 1
        
        for collector_name in collectors:
            self._add_widget(grid, collector_name, namespace, row, col)
            
            col += 1
            if col > 3:
                col = 1
                row += 1
        
        return self._prettify(root)
    
    def _add_widget(self, grid: ET.Element, collector_name: str, namespace: str, row: int, col: int):
        """Add a widget to the grid
        
        Args:
            grid: Parent grid element
            collector_name: Name of collector
            namespace: Minion namespace
            row: Grid row position
            col: Grid column position
        """
        if collector_name not in self.WIDGET_TEMPLATES:
            # Unknown collector - add comment
            comment = ET.Comment(f" Unknown collector: {collector_name} - add widget manually ")
            grid.append(comment)
            return
        
        template = self.WIDGET_TEMPLATES[collector_name]
        
        # Create widget element
        widget = ET.SubElement(grid, "Widget")
        widget.set("row", str(row))
        widget.set("column", str(col))
        widget.set("Height", "300")
        widget.set("Width", "400")
        
        # Widget file reference (for reusable widgets)
        widget.set("File", template["file"])
        
        # Title
        title_elem = ET.SubElement(widget, "Title")
        title_elem.text = template["title"]
        
        # Minion data source
        minion_src = ET.SubElement(widget, "MinionSrc")
        minion_src.set("Namespace", namespace)
        minion_src.set("ID", f"{collector_name.lower()}.value")
        
        # Widget-specific settings
        if template["type"].endswith("Gauge"):
            # Gauge settings
            min_val = ET.SubElement(widget, "MinValue")
            min_val.text = str(template["min"])
            
            max_val = ET.SubElement(widget, "MaxValue")
            max_val.text = str(template["max"])
            
            decimals = ET.SubElement(widget, "Decimals")
            decimals.text = str(template["decimals"])
            
            unit = ET.SubElement(widget, "UnitText")
            unit.text = template["unit"]
        
        elif template["type"] == "Text":
            # Text widget settings
            initial = ET.SubElement(widget, "InitialValue")
            initial.text = "Waiting for data..."
    
    def _prettify(self, elem: ET.Element) -> str:
        """Return pretty-printed XML string
        
        Args:
            elem: Root element
        
        Returns:
            Formatted XML string with proper indentation
        """
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def generate_all(self, config: Dict, output_dir: Path) -> Dict[str, Path]:
        """Generate all Marvin configuration files
        
        Args:
            config: Configuration dict
            output_dir: Directory to write files
        
        Returns:
            Dict mapping file type to Path
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        # Generate Application.xml
        app_xml = self.generate_application(config)
        app_file = output_dir / "Application.xml"
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(app_xml)
        files['application'] = app_file
        
        # Generate Tab.QuickStart.xml
        tab_xml = self.generate_tab(config)
        tab_file = output_dir / "Tab.QuickStart.xml"
        with open(tab_file, 'w', encoding='utf-8') as f:
            f.write(tab_xml)
        files['tab'] = tab_file
        
        # Generate Grid.QuickStart.xml
        grid_xml = self.generate_grid(config)
        grid_file = output_dir / "Grid.QuickStart.xml"
        with open(grid_file, 'w', encoding='utf-8') as f:
            f.write(grid_xml)
        files['grid'] = grid_file
        
        return files
