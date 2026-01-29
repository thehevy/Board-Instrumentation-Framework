"""
XML Parser for BIFF Configurations

Parses Minion, Oscar, and Marvin XML configurations with support for
aliases, environment variables, and all BIFF-specific patterns.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Union
from pathlib import Path
import re


class BIFFXMLParser:
    """Parse and manipulate BIFF XML configurations"""
    
    def __init__(self):
        """Initialize parser"""
        self.aliases = {}
        self.env_vars = []
        
    def parse_config(self, path: Union[str, Path]) -> ET.Element:
        """
        Parse XML file and return root element
        
        Args:
            path: Path to XML configuration file
            
        Returns:
            Root element of parsed XML
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ET.ParseError: If XML is malformed
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        try:
            tree = ET.parse(path)
            return tree.getroot()
        except ET.ParseError as e:
            raise ET.ParseError(f"Invalid XML in {path}: {e}")
    
    def extract_aliases(self, xml_root: ET.Element) -> Dict[str, str]:
        """
        Extract all alias definitions from configuration
        
        Args:
            xml_root: Root element of XML
            
        Returns:
            Dictionary mapping alias names to values
        """
        aliases = {}
        
        # Find all AliasList sections
        for alias_list in xml_root.findall('.//AliasList'):
            # Handle <Import> tags
            for import_tag in alias_list.findall('Import'):
                import_file = import_tag.text
                # TODO: Parse imported files recursively
                pass
            
            # Handle <Alias> tags
            for alias in alias_list.findall('Alias'):
                # Format: <Alias NAME="value"/>
                for key, value in alias.attrib.items():
                    aliases[key] = value
        
        self.aliases = aliases
        return aliases
    
    def extract_environment_vars(self, xml_root: ET.Element) -> List[str]:
        """
        Extract all environment variable references from configuration
        
        Args:
            xml_root: Root element of XML
            
        Returns:
            List of environment variable names referenced
        """
        xml_string = ET.tostring(xml_root, encoding='unicode')
        
        # Find all $(VAR_NAME) patterns
        pattern = r'\$\(([A-Z_][A-Z0-9_]*)\)'
        matches = re.findall(pattern, xml_string)
        
        # Remove duplicates and exclude known aliases
        env_vars = list(set(matches) - set(self.aliases.keys()))
        self.env_vars = env_vars
        return env_vars
    
    def extract_collectors(self, xml_root: ET.Element) -> List[Dict]:
        """
        Extract all collector definitions
        
        Args:
            xml_root: Root element of XML
            
        Returns:
            List of dictionaries containing collector info
        """
        collectors = []
        
        for collector in xml_root.findall('.//Collector'):
            collector_info = {
                'id': collector.get('ID'),
                'frequency': collector.get('Frequency'),
                'executable': collector.findtext('Executable'),
                'plugin': collector.findtext('Plugin'),
                'entry_point': collector.findtext('EntryPoint'),
                'params': [p.text for p in collector.findall('Param')],
                'operator': collector.findtext('Operator'),
                'value': collector.findtext('Value'),
                'inputs': [inp.text for inp in collector.findall('Input')],
            }
            collectors.append(collector_info)
        
        return collectors
    
    def extract_actors(self, xml_root: ET.Element) -> List[Dict]:
        """
        Extract all Actor definitions
        
        Args:
            xml_root: Root element of XML
            
        Returns:
            List of dictionaries containing Actor info
        """
        actors = []
        
        for actor in xml_root.findall('.//Actor'):
            actor_info = {
                'id': actor.get('ID'),
                'executable': actor.findtext('Executable'),
                'params': [p.text for p in actor.findall('Param')],
            }
            actors.append(actor_info)
        
        return actors
    
    def extract_modifiers(self, xml_root: ET.Element) -> List[Dict]:
        """
        Extract all Modifier definitions
        
        Args:
            xml_root: Root element of XML
            
        Returns:
            List of dictionaries containing Modifier info
        """
        modifiers = []
        
        for modifier in xml_root.findall('.//Modifier'):
            modifier_info = {
                'id': modifier.get('ID'),
                'precision': modifier.findtext('Precision'),
                'normalize': modifier.findtext('Normalize'),
                'is_regex': self._is_regex_pattern(modifier.get('ID', '')),
            }
            modifiers.append(modifier_info)
        
        return modifiers
    
    def extract_namespaces(self, xml_root: ET.Element) -> List[Dict]:
        """
        Extract all Namespace definitions from Minion config
        
        Args:
            xml_root: Root element of XML
            
        Returns:
            List of dictionaries containing Namespace info
        """
        namespaces = []
        
        for namespace in xml_root.findall('.//Namespace'):
            target_conn = namespace.find('TargetConnection')
            
            namespace_info = {
                'name': namespace.findtext('Name'),
                'default_frequency': namespace.findtext('DefaultFrequency'),
                'target_ip': target_conn.get('IP') if target_conn is not None else None,
                'target_port': target_conn.get('PORT') if target_conn is not None else None,
            }
            namespaces.append(namespace_info)
        
        return namespaces
    
    def extract_oscar_connections(self, xml_root: ET.Element) -> Dict:
        """
        Extract Oscar connection configuration
        
        Args:
            xml_root: Root element of Oscar config XML
            
        Returns:
            Dictionary with connection info
        """
        incoming = xml_root.find('.//IncomingMinionConnection')
        targets = xml_root.findall('.//TargetConnection')
        autoconnect = xml_root.find('.//MarvinAutoConnect')
        
        return {
            'incoming_port': incoming.get('PORT') if incoming is not None else None,
            'autoconnect_key': autoconnect.get('Key') if autoconnect is not None else None,
            'targets': [
                {'ip': t.get('IP'), 'port': t.get('PORT')}
                for t in targets
            ]
        }
    
    def extract_marvin_network(self, xml_root: ET.Element) -> Dict:
        """
        Extract Marvin network configuration
        
        Args:
            xml_root: Root element of Marvin config XML
            
        Returns:
            Dictionary with network info
        """
        network = xml_root.find('.//Network')
        
        if network is None:
            return {'port': None, 'oscars': []}
        
        oscars = network.findall('Oscar')
        
        return {
            'port': network.get('Port'),
            'oscars': [
                {
                    'ip': o.get('IP'),
                    'port': o.get('Port'),
                    'key': o.get('Key')
                }
                for o in oscars
            ]
        }
    
    def _is_regex_pattern(self, pattern: str) -> bool:
        """Check if pattern contains regex wildcards"""
        return bool(
            '(*)' in pattern or 
            '(.*)' in pattern or 
            '*' in pattern
        )
    
    def get_component_type(self, xml_root: ET.Element) -> str:
        """
        Determine which BIFF component the config is for
        
        Args:
            xml_root: Root element of XML
            
        Returns:
            'Minion', 'Oscar', or 'Marvin'
        """
        tag = xml_root.tag
        
        if tag == 'Minion':
            return 'Minion'
        elif tag == 'Oscar':
            return 'Oscar'
        elif tag == 'Marvin':
            return 'Marvin'
        else:
            return 'Unknown'
