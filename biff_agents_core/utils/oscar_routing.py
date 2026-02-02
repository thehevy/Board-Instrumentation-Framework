"""
Oscar Routing Configuration Parser and Generator

Provides utilities for parsing, analyzing, and generating Oscar routing configurations.
Oscar acts as a data broker routing data from Minions to Marvins.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET


@dataclass
class OscarConnection:
    """Represents an Oscar connection point"""
    ip: str
    port: int
    connection_type: str  # 'incoming_minion', 'incoming_marvin', 'target_marvin', 'oscar_chain'
    key: Optional[str] = None  # For chained Oscars or MarvinAutoConnect
    
    def __str__(self):
        return f"{self.ip}:{self.port}"


@dataclass
class OscarConfig:
    """Complete Oscar configuration"""
    oscar_id: str
    incoming_minion: Optional[OscarConnection]
    incoming_marvin: Optional[OscarConnection]
    target_connections: List[OscarConnection]
    chained_oscars: List[OscarConnection]  # Upstream Oscars
    downstream_oscars: List[OscarConnection]  # Downstream Oscars accepting connection
    record_file: Optional[str] = None
    shunting_file: Optional[str] = None
    
    def __str__(self):
        lines = [f"Oscar ID: {self.oscar_id}"]
        if self.incoming_minion:
            lines.append(f"  Incoming Minion: {self.incoming_minion}")
        if self.incoming_marvin:
            lines.append(f"  Incoming Marvin: {self.incoming_marvin}")
        if self.target_connections:
            lines.append(f"  Target Marvins: {len(self.target_connections)}")
            for target in self.target_connections:
                lines.append(f"    → {target}")
        return "\n".join(lines)


class OscarConfigParser:
    """Parse Oscar XML configurations"""
    
    def parse(self, config_path: Path) -> OscarConfig:
        """Parse Oscar configuration file"""
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        oscar_id = root.get('ID', 'UnknownOscar')
        
        # Parse incoming Minion connection
        incoming_minion = self._parse_incoming_minion(root)
        
        # Parse incoming Marvin connection
        incoming_marvin = self._parse_incoming_marvin(root)
        
        # Parse target connections (to Marvins)
        target_connections = self._parse_target_connections(root)
        
        # Parse chained Oscars (upstream)
        chained_oscars = self._parse_chained_oscars(root)
        
        # Parse downstream Oscars
        downstream_oscars = self._parse_downstream_oscars(root)
        
        # Parse recording config
        record_file = None
        record_elem = root.find('.//RecordFile')
        if record_elem is not None and record_elem.text:
            record_file = record_elem.text.strip()
        
        # Parse shunting config
        shunting_file = None
        shunt_elem = root.find('.//Shunting[@File]')
        if shunt_elem is not None:
            shunting_file = shunt_elem.get('File')
        
        return OscarConfig(
            oscar_id=oscar_id,
            incoming_minion=incoming_minion,
            incoming_marvin=incoming_marvin,
            target_connections=target_connections,
            chained_oscars=chained_oscars,
            downstream_oscars=downstream_oscars,
            record_file=record_file,
            shunting_file=shunting_file
        )
    
    def _parse_incoming_minion(self, root: ET.Element) -> Optional[OscarConnection]:
        """Parse IncomingMinionConnection element"""
        elem = root.find('.//IncomingMinionConnection')
        if elem is None:
            return None
        
        port = int(elem.get('PORT', '1100'))
        ip = elem.get('IP', '0.0.0.0')  # Default: listen on all interfaces
        
        # Check for MarvinAutoConnect key
        key = None
        autoconnect = elem.find('.//MarvinAutoConnect')
        if autoconnect is not None:
            key = autoconnect.get('Key')
        
        return OscarConnection(
            ip=ip,
            port=port,
            connection_type='incoming_minion',
            key=key
        )
    
    def _parse_incoming_marvin(self, root: ET.Element) -> Optional[OscarConnection]:
        """Parse IncomingMarvinConnection element"""
        elem = root.find('.//IncomingMarvinConnection')
        if elem is None:
            return None
        
        port = int(elem.get('PORT', '1101'))
        ip = elem.get('IP', '0.0.0.0')
        
        return OscarConnection(
            ip=ip,
            port=port,
            connection_type='incoming_marvin'
        )
    
    def _parse_target_connections(self, root: ET.Element) -> List[OscarConnection]:
        """Parse TargetConnection elements (connections to Marvins)"""
        connections = []
        
        for elem in root.findall('.//TargetConnection'):
            ip = elem.get('IP')
            port = int(elem.get('PORT'))
            
            if ip and port:
                connections.append(OscarConnection(
                    ip=ip,
                    port=port,
                    connection_type='target_marvin'
                ))
        
        return connections
    
    def _parse_chained_oscars(self, root: ET.Element) -> List[OscarConnection]:
        """Parse chained Oscar connections (upstream)"""
        connections = []
        
        # Look for Oscar elements inside IncomingMinionConnection (upstream Oscars)
        incoming = root.find('.//IncomingMinionConnection')
        if incoming is not None:
            for elem in incoming.findall('.//Oscar'):
                ip = elem.get('IP')
                port = int(elem.get('Port', elem.get('PORT', '0')))
                key = elem.get('Key')
                
                if ip and port:
                    connections.append(OscarConnection(
                        ip=ip,
                        port=port,
                        connection_type='oscar_chain',
                        key=key
                    ))
        
        return connections
    
    def _parse_downstream_oscars(self, root: ET.Element) -> List[OscarConnection]:
        """Parse downstream Oscar connections"""
        # Note: These are typically configured on the downstream Oscar side
        # This method is a placeholder for future use
        return []


class OscarConfigGenerator:
    """Generate Oscar XML configurations"""
    
    def generate_basic(self, 
                      oscar_id: str,
                      minion_port: int = 1100,
                      marvin_targets: List[Tuple[str, int]] = None) -> str:
        """
        Generate a basic Oscar configuration
        
        Args:
            oscar_id: Oscar instance identifier
            minion_port: Port for incoming Minion connections
            marvin_targets: List of (ip, port) tuples for Marvin targets
        
        Returns:
            XML configuration string
        """
        if marvin_targets is None:
            marvin_targets = [('localhost', 52001)]
        
        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            f'<Oscar ID="{oscar_id}">',
            f'  <IncomingMinionConnection PORT="{minion_port}"/>',
            ''
        ]
        
        if marvin_targets:
            lines.append('  <!-- Points towards Marvin -->')
            for ip, port in marvin_targets:
                lines.append(f'  <TargetConnection IP="{ip}" PORT="{port}"/>')
        
        lines.append('</Oscar>')
        
        return '\n'.join(lines)
    
    def generate_from_minion_namespace(self,
                                      namespace_name: str,
                                      target_ip: str,
                                      target_port: int,
                                      oscar_listen_port: int = 1100,
                                      marvin_ips: List[str] = None) -> str:
        """
        Generate Oscar config to route data from a Minion namespace
        
        Args:
            namespace_name: Minion namespace being routed
            target_ip: IP the Minion will send to
            target_port: Port the Minion will send to (should match oscar_listen_port)
            oscar_listen_port: Port Oscar listens on
            marvin_ips: List of Marvin IPs to forward to
        
        Returns:
            Oscar XML configuration
        """
        if marvin_ips is None:
            marvin_ips = ['localhost']
        
        oscar_id = f"Oscar_{namespace_name}"
        
        # Start at port 52001 for first Marvin
        marvin_targets = [(ip, 52001 + i) for i, ip in enumerate(marvin_ips)]
        
        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            f'<!-- Generated Oscar config for namespace: {namespace_name} -->',
            f'<Oscar ID="{oscar_id}">',
            f'  <IncomingMinionConnection PORT="{oscar_listen_port}"/>',
            ''
        ]
        
        lines.append(f'  <!-- Forward to Marvin(s) -->')
        for ip, port in marvin_targets:
            lines.append(f'  <TargetConnection IP="{ip}" PORT="{port}"/>')
        
        lines.append('</Oscar>')
        lines.append('')
        lines.append(f'<!-- Minion should use: <TargetConnection IP="{target_ip}" PORT="{target_port}"/> -->')
        
        return '\n'.join(lines)
    
    def generate_multi_marvin(self,
                             oscar_id: str,
                             minion_port: int,
                             marvin_count: int,
                             base_marvin_port: int = 52001,
                             marvin_ips: List[str] = None) -> Tuple[str, Dict]:
        """
        Generate Oscar config for multiple Marvin instances
        
        Args:
            oscar_id: Oscar instance ID
            minion_port: Port for Minion connections
            marvin_count: Number of Marvin instances
            base_marvin_port: Starting port for Marvins
            marvin_ips: List of Marvin IPs (or None for all localhost)
        
        Returns:
            Tuple of (oscar_xml, marvin_port_map)
        """
        if marvin_ips is None:
            marvin_ips = ['localhost'] * marvin_count
        elif len(marvin_ips) < marvin_count:
            # Pad with localhost
            marvin_ips.extend(['localhost'] * (marvin_count - len(marvin_ips)))
        
        # Allocate ports
        marvin_ports = {}
        for i in range(marvin_count):
            marvin_ports[f'Marvin{i+1}'] = {
                'ip': marvin_ips[i],
                'port': base_marvin_port + i
            }
        
        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            f'<Oscar ID="{oscar_id}">',
            f'  <IncomingMinionConnection PORT="{minion_port}"/>',
            ''
        ]
        
        lines.append(f'  <!-- Routing to {marvin_count} Marvin instances -->')
        for marvin_name, config in marvin_ports.items():
            lines.append(f'  <TargetConnection IP="{config["ip"]}" PORT="{config["port"]}"/>  <!-- {marvin_name} -->')
        
        lines.append('</Oscar>')
        
        return '\n'.join(lines), marvin_ports
    
    def generate_with_chaining(self,
                              oscar_id: str,
                              minion_port: int,
                              upstream_oscar_ip: str,
                              upstream_oscar_port: int,
                              chain_key: str) -> str:
        """
        Generate Oscar config that chains to an upstream Oscar
        
        Args:
            oscar_id: This Oscar's ID
            minion_port: Port to listen for Minions
            upstream_oscar_ip: IP of upstream Oscar
            upstream_oscar_port: Port of upstream Oscar
            chain_key: Authentication key for chain
        
        Returns:
            Oscar XML configuration
        """
        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            f'<Oscar ID="{oscar_id}">',
            f'  <IncomingMinionConnection PORT="{minion_port}">',
            f'    <!-- Forward to upstream Oscar -->',
            f'    <Oscar IP="{upstream_oscar_ip}" Port="{upstream_oscar_port}" Key="{chain_key}"/>',
            '  </IncomingMinionConnection>',
            '</Oscar>'
        ]
        
        return '\n'.join(lines)


class OscarRoutingAnalyzer:
    """Analyze Oscar routing configurations"""
    
    def analyze_routing(self, config: OscarConfig) -> Dict:
        """Analyze Oscar routing configuration"""
        analysis = {
            'oscar_id': config.oscar_id,
            'listens_for_minions': config.incoming_minion is not None,
            'listens_for_marvins': config.incoming_marvin is not None,
            'forwards_to_marvins': len(config.target_connections),
            'chained_to_oscar': len(config.chained_oscars) > 0,
            'has_recording': config.record_file is not None,
            'has_shunting': config.shunting_file is not None,
            'warnings': [],
            'errors': []
        }
        
        # Validate configuration
        if not config.incoming_minion:
            analysis['errors'].append("No IncomingMinionConnection configured - Oscar won't receive data")
        
        if not config.target_connections and not config.chained_oscars:
            analysis['warnings'].append("No TargetConnections or chained Oscars - data will not be forwarded")
        
        if config.incoming_minion and config.target_connections:
            # Check for port conflicts
            minion_port = config.incoming_minion.port
            for target in config.target_connections:
                if target.ip in ['localhost', '127.0.0.1'] and target.port == minion_port:
                    analysis['errors'].append(
                        f"Port conflict: Minion incoming ({minion_port}) same as Marvin target ({target.port})"
                    )
        
        return analysis
    
    def validate_minion_oscar_connection(self,
                                        minion_target_port: int,
                                        oscar_config: OscarConfig) -> List[str]:
        """
        Validate Minion can connect to Oscar
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not oscar_config.incoming_minion:
            errors.append("Oscar has no IncomingMinionConnection configured")
            return errors
        
        if minion_target_port != oscar_config.incoming_minion.port:
            errors.append(
                f"Minion sends to port {minion_target_port}, "
                f"but Oscar listens on port {oscar_config.incoming_minion.port}"
            )
        
        return errors
