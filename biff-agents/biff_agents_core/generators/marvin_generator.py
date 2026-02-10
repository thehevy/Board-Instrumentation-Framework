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
        
        # Add AliasList at the top with import for DefinitionFiles
        alias_list = ET.SubElement(root, "AliasList")
        alias_list.append(ET.Comment(" Import alias definitions from DefinitionFiles folder "))
        import_elem = ET.SubElement(alias_list, "Import")
        import_elem.text = "DefinitionFiles/Aliases.xml"
        
        # Application element
        app = ET.SubElement(root, "Application")
        app.set("Scale", "auto")
        
        # Creation size (use aliases)
        size = ET.SubElement(app, "CreationSize")
        size.set("Width", "$(WindowWidth)")
        size.set("Height", "$(WindowHeight)")
        
        # Network port (use alias)
        network = ET.SubElement(app, "Network")
        network.set("Port", "$(MarvinPort)")
        
        # Title (use alias for namespace)
        title = ET.SubElement(app, "Title")
        title.text = f"BIFF Quick Start - $(MinionNamespace)"
        
        # Padding (use aliases)
        padding = ET.SubElement(app, "Padding")
        padding.set("top", "$(Padding)")
        padding.set("bottom", "$(Padding)")
        padding.set("right", "$(Padding)")
        padding.set("left", "$(Padding)")
        
        # Stylesheet
        stylesheet = ET.SubElement(app, "StyleSheet")
        stylesheet.text = "Widget/Modena-BIFF.css"
        
        # Heartbeat (use alias)
        heartbeat = ET.SubElement(app, "Heartbeat")
        heartbeat.set("Rate", "$(HeartbeatRate)")
        
        # Tasks
        tasks = ET.SubElement(app, "Tasks")
        tasks.set("Enabled", "True")
        
        # Main menu
        menu = ET.SubElement(app, "MainMenu")
        menu.set("Show", "True")
        
        # Tabs
        tabs = ET.SubElement(app, "Tabs")
        
        # Add Quick Start tab reference
        tab_ref = ET.SubElement(tabs, "Tab")
        tab_ref.set("ID", "Tab.QuickStart")
        
        # Add Tab definition outside Application (required by Marvin)
        tab_def = ET.SubElement(root, "Tab")
        tab_def.set("ID", "Tab.QuickStart")
        tab_def.set("hgap", "$(GridHGap)")
        tab_def.set("vgap", "$(GridVGap)")
        tab_def.set("Align", "N")
        tab_def.set("TabTitle", "$(MinionNamespace) Dashboard")
        tab_def.set("File", "Tab.QuickStart.xml")
        
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
        
        # Title (use alias)
        title = ET.SubElement(tab, "Title")
        title.text = "$(MinionNamespace) Dashboard"
        
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
        widget.set("Height", "$(WidgetHeight)")  # Use alias
        widget.set("Width", "$(WidgetWidth)")    # Use alias
        
        # Widget file reference (for reusable widgets)
        widget.set("File", template["file"])
        
        # Title
        title_elem = ET.SubElement(widget, "Title")
        title_elem.text = template["title"]
        
        # Minion data source (use alias for namespace)
        minion_src = ET.SubElement(widget, "MinionSrc")
        minion_src.set("Namespace", "$(MinionNamespace)")
        minion_src.set("ID", f"{collector_name.lower()}.value")
        
        # Widget-specific settings
        # Note: Properties like MinValue, MaxValue, Decimals, UnitText are widget 
        # definition properties and belong in the widget definition files 
        # (Widget/Gauge/*.xml), not in the grid instantiation.
        if template["type"] == "Text":
            # Text widget initial value
            initial = ET.SubElement(widget, "InitialValue")
            initial.text = "Waiting for data..."
    
    def generate_aliases(self, config: Dict) -> str:
        """Generate DefinitionFiles/Aliases.xml
        
        Args:
            config: Configuration dict
        
        Returns:
            XML string with alias definitions
        """
        root = ET.Element("AliasList")
        root.append(ET.Comment(" Configuration Aliases - Modify these values to customize your dashboard "))
        
        # Add configuration comment sections
        root.append(ET.Comment(" Namespace Configuration "))
        self._add_alias(root, "MinionNamespace", config.get("minion_namespace", "QuickStart"))
        
        root.append(ET.Comment(" Network Configuration "))
        self._add_alias(root, "MarvinPort", str(config.get("marvin_port", 52001)))
        self._add_alias(root, "OscarIP", config.get("oscar_ip", "localhost"))
        self._add_alias(root, "OscarPort", str(config.get("oscar_port", 1100)))
        
        root.append(ET.Comment(" Window Dimensions "))
        self._add_alias(root, "WindowWidth", "1920")
        self._add_alias(root, "WindowHeight", "1050")
        
        root.append(ET.Comment(" Layout Configuration "))
        self._add_alias(root, "Padding", "5")
        self._add_alias(root, "GridHGap", "5")
        self._add_alias(root, "GridVGap", "5")
        self._add_alias(root, "HeartbeatRate", "10")
        
        root.append(ET.Comment(" Widget Dimensions "))
        self._add_alias(root, "WidgetHeight", "300")
        self._add_alias(root, "WidgetWidth", "400")
        
        root.append(ET.Comment(" Color Palette - Customize widget colors "))
        self._add_alias(root, "ColorPrimary", "#2196F3")
        self._add_alias(root, "ColorSuccess", "#4CAF50")
        self._add_alias(root, "ColorWarning", "#FF9800")
        self._add_alias(root, "ColorDanger", "#F44336")
        
        return self._prettify(root)
    
    def _add_alias(self, parent: ET.Element, name: str, value: str):
        """Add an alias element
        
        Args:
            parent: Parent element (AliasList or root)
            name: Alias name
            value: Alias value
        """
        alias = ET.SubElement(parent, "Alias")
        alias.set(name, value)
    
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
        
        # Create DefinitionFiles directory
        def_files_dir = output_dir / "DefinitionFiles"
        def_files_dir.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        # Generate DefinitionFiles/Aliases.xml
        aliases_xml = self.generate_aliases(config)
        aliases_file = def_files_dir / "Aliases.xml"
        with open(aliases_file, 'w', encoding='utf-8') as f:
            f.write(aliases_xml)
        files['aliases'] = aliases_file
        
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
