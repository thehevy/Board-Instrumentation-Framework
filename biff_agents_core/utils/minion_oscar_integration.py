"""
Minion to Oscar Integration

Bridges Minion configurations with Oscar routing, automatically generating
Oscar configs from Minion namespace configurations.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from biff_agents_core.config.xml_parser import BIFFXMLParser
from biff_agents_core.utils.oscar_routing import (
    OscarConfigGenerator,
    OscarConfigParser,
    OscarRoutingAnalyzer
)


@dataclass
class MinionNamespace:
    """Represents a Minion namespace configuration"""
    name: str
    target_ip: str
    target_port: int
    default_frequency: int
    collectors: List[Dict]
    actors: List[Dict]
    
    def __str__(self):
        return f"{self.name} → {self.target_ip}:{self.target_port} ({len(self.collectors)} collectors)"


class MinionConfigParser:
    """Parse Minion configurations with namespace extraction"""
    
    def __init__(self):
        self.xml_parser = BIFFXMLParser()
    
    def parse(self, config_path: Path) -> List[MinionNamespace]:
        """
        Parse Minion configuration and extract all namespaces
        
        Args:
            config_path: Path to MinionConfig.xml
        
        Returns:
            List of MinionNamespace objects
        """
        root = self.xml_parser.parse_config(config_path)
        namespaces = []
        
        for ns_elem in root.findall('.//Namespace'):
            namespace = self._parse_namespace(ns_elem)
            if namespace:
                namespaces.append(namespace)
        
        return namespaces
    
    def _parse_namespace(self, ns_elem: ET.Element) -> Optional[MinionNamespace]:
        """Parse a single namespace element"""
        # Extract name
        name_elem = ns_elem.find('Name')
        if name_elem is None or not name_elem.text:
            return None
        name = name_elem.text.strip()
        
        # Extract target connection
        target_elem = ns_elem.find('TargetConnection')
        if target_elem is None:
            return None
        
        target_ip = target_elem.get('IP', 'localhost')
        target_port = int(target_elem.get('PORT', '1100'))
        
        # Extract default frequency
        freq_elem = ns_elem.find('DefaultFrequency')
        default_frequency = int(freq_elem.text) if freq_elem is not None and freq_elem.text else 1000
        
        # Extract collectors
        collectors = []
        for collector_elem in ns_elem.findall('.//Collector'):
            collector_info = {
                'id': collector_elem.get('ID'),
                'frequency': collector_elem.get('Frequency', str(default_frequency)),
                'executable': collector_elem.findtext('Executable'),
                'params': [p.text for p in collector_elem.findall('Param') if p.text]
            }
            collectors.append(collector_info)
        
        # Extract actors
        actors = []
        for actor_elem in ns_elem.findall('.//Actor'):
            actor_info = {
                'id': actor_elem.get('ID'),
                'executable': actor_elem.findtext('Executable'),
                'params': [p.text for p in actor_elem.findall('Param') if p.text]
            }
            actors.append(actor_info)
        
        return MinionNamespace(
            name=name,
            target_ip=target_ip,
            target_port=target_port,
            default_frequency=default_frequency,
            collectors=collectors,
            actors=actors
        )


class MinionOscarIntegration:
    """Generate Oscar configurations from Minion namespaces"""
    
    def __init__(self):
        self.minion_parser = MinionConfigParser()
        self.oscar_generator = OscarConfigGenerator()
        self.oscar_parser = OscarConfigParser()
        self.oscar_analyzer = OscarRoutingAnalyzer()
    
    def generate_oscar_from_minion(self,
                                   minion_config_path: Path,
                                   marvin_ips: List[str] = None,
                                   base_marvin_port: int = 52001) -> Dict[str, str]:
        """
        Generate Oscar configs for all Minion namespaces
        
        Args:
            minion_config_path: Path to MinionConfig.xml
            marvin_ips: List of Marvin IPs to route to
            base_marvin_port: Starting port for Marvins
        
        Returns:
            Dictionary mapping namespace names to Oscar XML configs
        """
        if marvin_ips is None:
            marvin_ips = ['localhost']
        
        namespaces = self.minion_parser.parse(minion_config_path)
        oscar_configs = {}
        
        for namespace in namespaces:
            oscar_xml = self.oscar_generator.generate_from_minion_namespace(
                namespace_name=namespace.name,
                target_ip=namespace.target_ip,
                target_port=namespace.target_port,
                oscar_listen_port=namespace.target_port,
                marvin_ips=marvin_ips
            )
            oscar_configs[namespace.name] = oscar_xml
        
        return oscar_configs
    
    def generate_unified_oscar(self,
                              minion_config_path: Path,
                              oscar_id: str = "UnifiedOscar",
                              marvin_count: int = 1,
                              base_marvin_port: int = 52001) -> Tuple[str, Dict]:
        """
        Generate a single Oscar config handling all Minion namespaces
        
        Args:
            minion_config_path: Path to MinionConfig.xml
            oscar_id: ID for the Oscar instance
            marvin_count: Number of Marvin instances
            base_marvin_port: Starting port for Marvins
        
        Returns:
            Tuple of (oscar_xml, port_mapping)
        """
        namespaces = self.minion_parser.parse(minion_config_path)
        
        if not namespaces:
            raise ValueError("No namespaces found in Minion config")
        
        # Use the first namespace's target port as Oscar listen port
        # (Assume all namespaces target the same Oscar)
        listen_port = namespaces[0].target_port
        
        # Verify all namespaces target the same port
        for ns in namespaces:
            if ns.target_port != listen_port:
                raise ValueError(
                    f"Namespace '{ns.name}' targets port {ns.target_port}, "
                    f"but expected {listen_port}. All namespaces must target the same Oscar port."
                )
        
        # Generate Oscar config with multiple Marvins
        oscar_xml, port_map = self.oscar_generator.generate_multi_marvin(
            oscar_id=oscar_id,
            minion_port=listen_port,
            marvin_count=marvin_count,
            base_marvin_port=base_marvin_port
        )
        
        return oscar_xml, port_map
    
    def validate_minion_oscar_routing(self,
                                     minion_config_path: Path,
                                     oscar_config_path: Path) -> List[str]:
        """
        Validate that Minion and Oscar configurations are compatible
        
        Args:
            minion_config_path: Path to MinionConfig.xml
            oscar_config_path: Path to OscarConfig.xml
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Parse both configs
        namespaces = self.minion_parser.parse(minion_config_path)
        oscar_config = self.oscar_parser.parse(oscar_config_path)
        
        # Check each namespace's target matches Oscar's incoming port
        for namespace in namespaces:
            ns_errors = self.oscar_analyzer.validate_minion_oscar_connection(
                namespace.target_port,
                oscar_config
            )
            
            if ns_errors:
                errors.extend([
                    f"Namespace '{namespace.name}': {err}"
                    for err in ns_errors
                ])
        
        # Check Oscar has target connections
        if not oscar_config.target_connections and not oscar_config.chained_oscars:
            errors.append(
                "Oscar has no TargetConnections configured - data will not be forwarded to Marvin"
            )
        
        return errors
    
    def generate_deployment_guide(self,
                                 minion_config_path: Path,
                                 oscar_xml: str,
                                 port_map: Dict) -> str:
        """
        Generate deployment instructions for Minion → Oscar → Marvin setup
        
        Args:
            minion_config_path: Path to MinionConfig.xml
            oscar_xml: Generated Oscar configuration
            port_map: Marvin port mapping
        
        Returns:
            Markdown-formatted deployment guide
        """
        namespaces = self.minion_parser.parse(minion_config_path)
        
        guide = ["# BIFF Deployment Guide\n"]
        guide.append("## Configuration Summary\n")
        
        guide.append("### Minion Namespaces\n")
        for ns in namespaces:
            guide.append(f"- **{ns.name}**")
            guide.append(f"  - Collectors: {len(ns.collectors)}")
            guide.append(f"  - Actors: {len(ns.actors)}")
            guide.append(f"  - Target: {ns.target_ip}:{ns.target_port}")
            guide.append("")
        
        guide.append("### Oscar Configuration\n")
        guide.append("```xml")
        guide.append(oscar_xml)
        guide.append("```\n")
        
        guide.append("### Marvin Instances\n")
        for marvin_name, config in port_map.items():
            guide.append(f"- **{marvin_name}**")
            guide.append(f"  - IP: {config['ip']}")
            guide.append(f"  - Port: {config['port']}")
            guide.append("")
        
        guide.append("## Deployment Steps\n")
        guide.append("### 1. Deploy Oscar\n")
        guide.append("```bash")
        guide.append("# Copy Oscar configuration")
        guide.append("cp OscarConfig.xml Oscar/")
        guide.append("")
        guide.append("# Start Oscar")
        guide.append("cd Oscar")
        guide.append("python Oscar.py")
        guide.append("```\n")
        
        guide.append("### 2. Deploy Minion(s)\n")
        guide.append("```bash")
        guide.append("# Start Minion with existing configuration")
        guide.append("cd Minion")
        guide.append("python Minion.py -c MinionConfig.xml")
        guide.append("```\n")
        
        guide.append("### 3. Deploy Marvin(s)\n")
        for marvin_name, config in port_map.items():
            guide.append(f"#### {marvin_name}\n")
            guide.append("Update Marvin application config with:\n")
            guide.append("```xml")
            guide.append(f'<Network Port="{config["port"]}">')
            guide.append(f'  <Oscar IP="localhost" Port="{config["port"]}" />')
            guide.append("</Network>")
            guide.append("```\n")
            guide.append("```bash")
            guide.append("cd Marvin")
            guide.append("java -jar BIFF.Marvin.jar Application.xml")
            guide.append("```\n")
        
        guide.append("## Verification\n")
        guide.append("### Check Oscar is receiving from Minion\n")
        guide.append("Oscar logs should show: `Received Connection from Minion <namespace>`\n")
        
        guide.append("### Check Marvin is receiving from Oscar\n")
        guide.append("Marvin UI should show Oscar connection status (green = connected)\n")
        
        guide.append("### Check Data Flow\n")
        guide.append("Marvin widgets should update with collector data within a few seconds\n")
        
        return '\n'.join(guide)


class MinionNamespaceAnalyzer:
    """Analyze Minion namespace configurations"""
    
    def __init__(self):
        self.minion_parser = MinionConfigParser()
    
    def analyze_namespaces(self, minion_config_path: Path) -> Dict:
        """
        Analyze Minion configuration and provide insights
        
        Args:
            minion_config_path: Path to MinionConfig.xml
        
        Returns:
            Dictionary with analysis results
        """
        namespaces = self.minion_parser.parse(minion_config_path)
        
        # Group by target
        targets = {}
        for ns in namespaces:
            target_key = f"{ns.target_ip}:{ns.target_port}"
            if target_key not in targets:
                targets[target_key] = []
            targets[target_key].append(ns)
        
        # Count collectors
        total_collectors = sum(len(ns.collectors) for ns in namespaces)
        total_actors = sum(len(ns.actors) for ns in namespaces)
        
        # Find high-frequency collectors
        high_freq = []
        for ns in namespaces:
            for collector in ns.collectors:
                freq = int(collector.get('frequency', ns.default_frequency))
                if freq < 500:  # Less than 500ms = high frequency
                    high_freq.append({
                        'namespace': ns.name,
                        'collector': collector['id'],
                        'frequency': freq
                    })
        
        return {
            'namespace_count': len(namespaces),
            'unique_targets': len(targets),
            'targets': {k: [ns.name for ns in v] for k, v in targets.items()},
            'total_collectors': total_collectors,
            'total_actors': total_actors,
            'high_frequency_collectors': high_freq,
            'avg_collectors_per_namespace': total_collectors / len(namespaces) if namespaces else 0,
            'avg_actors_per_namespace': total_actors / len(namespaces) if namespaces else 0
        }
