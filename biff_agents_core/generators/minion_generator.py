"""
Generator for Minion configuration files.

Creates MinionConfig.xml with collectors, namespaces, and target connections.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Dict, List, Optional
from .base_generator import BaseGenerator


class MinionConfigGenerator(BaseGenerator):
    """Generate Minion configuration XML"""
    
    # Collector definitions with their parameters
    COLLECTOR_TEMPLATES = {
        "RandomVal": {
            "executable": "Collectors/RandomVal.py",
            "params": ["0", "100"],
            "description": "Random value between 0-100"
        },
        "Timer": {
            "executable": "Collectors/Timer.py",
            "params": [],
            "description": "Elapsed time in milliseconds"
        },
        "CPU": {
            "executable": "Collectors/CPU.py",
            "params": ["GetUsage"],
            "description": "CPU utilization percentage"
        },
        "Memory": {
            "executable": "Collectors/CPU.py",
            "params": ["GetMemory"],
            "description": "Memory usage (MB used, MB total)"
        },
        "Network": {
            "executable": "Collectors/Network.py",
            "params": ["GetBytesRecv"],
            "description": "Network bytes received"
        },
        "Storage": {
            "executable": "Collectors/CPU.py",
            "params": ["GetDiskUsage"],
            "description": "Disk usage percentage"
        }
    }
    
    def generate(self, config: Dict) -> str:
        """Generate Minion configuration XML
        
        Args:
            config: Configuration dict from SetupWizard
                - minion_namespace: str
                - collectors: List[str]
                - oscar_ip: str
                - oscar_port: int
                - use_existing: bool
                - biff_root: Optional[str]
        
        Returns:
            XML string
        """
        root = ET.Element("Minion")
        
        # Add single threading option (recommended for simple setups)
        root.set("SingleThreading", "false")
        
        # Create namespace
        namespace = ET.SubElement(root, "Namespace")
        
        # Namespace name
        name = ET.SubElement(namespace, "Name")
        name.text = config.get("minion_namespace", "QuickStart")
        
        # Default frequency (1000ms = 1 second)
        freq = ET.SubElement(namespace, "DefaultFrequency")
        freq.text = "1000"
        
        # Target connection (Oscar)
        target = ET.SubElement(namespace, "TargetConnection")
        target.set("IP", config.get("oscar_ip", "localhost"))
        target.set("PORT", str(config.get("oscar_port", 1100)))
        
        # Add collectors
        for collector_name in config.get("collectors", ["RandomVal"]):
            self._add_collector(namespace, collector_name, config)
        
        # Convert to pretty-printed XML
        return self._prettify(root)
    
    def _add_collector(self, namespace: ET.Element, collector_name: str, config: Dict):
        """Add a collector to the namespace
        
        Args:
            namespace: Parent namespace element
            collector_name: Name of collector (e.g., "RandomVal")
            config: Full configuration dict
        """
        if collector_name not in self.COLLECTOR_TEMPLATES:
            # Unknown collector - add comment
            comment = ET.Comment(f" Unknown collector: {collector_name} - add manually ")
            namespace.append(comment)
            return
        
        template = self.COLLECTOR_TEMPLATES[collector_name]
        
        # Create collector element
        collector = ET.SubElement(namespace, "Collector")
        collector.set("ID", f"{collector_name.lower()}.value")
        
        # Add executable path
        executable = ET.SubElement(collector, "Executable")
        
        if config.get("use_existing") and config.get("biff_root"):
            # Use existing BIFF installation paths
            biff_root = Path(config["biff_root"])
            exec_path = biff_root / "Minion" / template["executable"]
            executable.text = str(exec_path)
        else:
            # Relative path (assumes running from Minion directory)
            executable.text = template["executable"]
        
        # Add parameters
        for param_value in template["params"]:
            param = ET.SubElement(collector, "Param")
            param.text = param_value
    
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
    
    def generate_file(self, config: Dict, output_path: Path) -> Path:
        """Generate and write Minion config to file
        
        Args:
            config: Configuration dict
            output_path: Directory to write MinionConfig.xml
        
        Returns:
            Path to generated file
        """
        xml_content = self.generate(config)
        
        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Write file
        file_path = output_path / "MinionConfig.xml"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        return file_path
    
    @staticmethod
    def get_available_collectors() -> List[str]:
        """Get list of available collector names"""
        return list(MinionConfigGenerator.COLLECTOR_TEMPLATES.keys())
    
    @staticmethod
    def get_collector_description(name: str) -> str:
        """Get description for a collector
        
        Args:
            name: Collector name
        
        Returns:
            Description string or "Unknown collector"
        """
        template = MinionConfigGenerator.COLLECTOR_TEMPLATES.get(name)
        if template:
            return template["description"]
        return "Unknown collector"
