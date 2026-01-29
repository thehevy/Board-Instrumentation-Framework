"""
Generator for Oscar configuration files.

Creates OscarConfig.xml with upstream (Minion) and downstream (Marvin) connections.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Dict, List
from .base_generator import BaseGenerator


class OscarConfigGenerator(BaseGenerator):
    """Generate Oscar configuration XML"""
    
    def generate(self, config: Dict) -> str:
        """Generate Oscar configuration XML
        
        Args:
            config: Configuration dict from SetupWizard
                - oscar_port: int (upstream Minion port)
                - marvin_port: int (downstream Marvin port)
                - oscar_ip: str (for downstream connection)
                - minion_namespace: str (optional, for filtering)
        
        Returns:
            XML string
        """
        root = ET.Element("Oscar")
        root.set("ID", "QuickStart")
        
        # Optional: Add namespace comment
        namespace = config.get("minion_namespace")
        if namespace and namespace != "QuickStart":
            # Add comment about namespace routing
            comment = ET.Comment(
                f" Oscar routes all data from namespace '{namespace}' to Marvin "
            )
            root.append(comment)
        
        # Incoming Minion connections (upstream)
        incoming = ET.SubElement(root, "IncomingMinionConnection")
        incoming.set("PORT", str(config.get("oscar_port", 1100)))
        
        # Target connections (downstream to Marvins)
        target = ET.SubElement(root, "TargetConnection")
        
        # Use localhost for single-machine, or specified IP for network deployment
        oscar_ip = config.get("oscar_ip", "localhost")
        if oscar_ip in ["localhost", "127.0.0.1"]:
            target.set("IP", "localhost")
        else:
            target.set("IP", oscar_ip)
        
        target.set("PORT", str(config.get("marvin_port", 52001)))
        
        # Convert to pretty-printed XML
        return self._prettify(root)
    
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
        """Generate and write Oscar config to file
        
        Args:
            config: Configuration dict
            output_path: Directory to write OscarConfig.xml
        
        Returns:
            Path to generated file
        """
        xml_content = self.generate(config)
        
        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Write file
        file_path = output_path / "OscarConfig.xml"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        return file_path
