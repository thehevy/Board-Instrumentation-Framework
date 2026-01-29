"""Base generator class for creating BIFF configurations."""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Dict, Optional


class BaseGenerator:
    """Base class for configuration generators"""
    
    def __init__(self):
        """Initialize generator"""
        pass
    
    def prettify_xml(self, elem: ET.Element) -> str:
        """
        Convert Element to pretty-printed XML string
        
        Args:
            elem: XML element to prettify
            
        Returns:
            Formatted XML string
        """
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def write_xml(self, elem: ET.Element, path: Path):
        """
        Write XML element to file with proper formatting
        
        Args:
            elem: XML element to write
            path: Output file path
        """
        xml_string = self.prettify_xml(elem)
        
        # Remove extra blank lines
        lines = [line for line in xml_string.split('\n') if line.strip()]
        xml_string = '\n'.join(lines)
        
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(xml_string, encoding='utf-8')
    
    def create_collector(self, collector_id: str, executable: str, 
                        frequency: Optional[str] = None,
                        params: Optional[list] = None) -> ET.Element:
        """
        Create a Collector element
        
        Args:
            collector_id: Unique collector ID
            executable: Path to collector script
            frequency: Collection frequency in ms
            params: List of parameters
            
        Returns:
            Collector XML element
        """
        attribs = {'ID': collector_id}
        if frequency:
            attribs['Frequency'] = frequency
        
        collector = ET.Element('Collector', attribs)
        
        exe_elem = ET.SubElement(collector, 'Executable')
        exe_elem.text = executable
        
        if params:
            for param in params:
                param_elem = ET.SubElement(collector, 'Param')
                param_elem.text = str(param)
        
        return collector
    
    def create_actor(self, actor_id: str, executable: str,
                    params: Optional[list] = None) -> ET.Element:
        """
        Create an Actor element
        
        Args:
            actor_id: Unique actor ID
            executable: Path to actor script
            params: List of parameters
            
        Returns:
            Actor XML element
        """
        actor = ET.Element('Actor', {'ID': actor_id})
        
        exe_elem = ET.SubElement(actor, 'Executable')
        exe_elem.text = executable
        
        if params:
            for param in params:
                param_elem = ET.SubElement(actor, 'Param')
                param_elem.text = str(param)
        
        return actor
    
    def create_modifier(self, modifier_id: str, 
                       precision: Optional[str] = None,
                       normalize: Optional[str] = None) -> ET.Element:
        """
        Create a Modifier element
        
        Args:
            modifier_id: Modifier ID (can include regex like P(*))
            precision: Decimal precision
            normalize: Normalization factor
            
        Returns:
            Modifier XML element
        """
        modifier = ET.Element('Modifier', {'ID': modifier_id})
        
        if precision:
            prec_elem = ET.SubElement(modifier, 'Precision')
            prec_elem.text = precision
        
        if normalize:
            norm_elem = ET.SubElement(modifier, 'Normalize')
            norm_elem.text = normalize
        
        return modifier
    
    def create_alias(self, name: str, value: str) -> Dict[str, str]:
        """
        Create an alias definition
        
        Args:
            name: Alias name
            value: Alias value
            
        Returns:
            Dictionary suitable for Alias element attributes
        """
        return {name: value}
