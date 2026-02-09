"""
Minion Data Source Discovery

Parses MinionConfig.xml to discover available data sources for Marvin widgets.
This bridges Phase 2 (Minion collectors) with Phase 3 (Marvin visualization).
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Union
import re


@dataclass
class DataSource:
    """Represents a data source available from Minion"""
    namespace: str
    collector_id: str
    description: str
    source_type: str  # 'collector', 'plugin', 'dynamic'
    collector_file: Optional[str] = None
    frequency: int = 1000  # milliseconds
    metadata: Dict[str, str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def display_name(self) -> str:
        """User-friendly display name"""
        return f"{self.namespace}:{self.collector_id}"
    
    @property
    def suggested_unit(self) -> str:
        """Suggest unit based on collector ID"""
        id_lower = self.collector_id.lower()
        
        if 'temp' in id_lower or 'temperature' in id_lower:
            return '°C'
        elif 'percent' in id_lower or 'usage' in id_lower:
            return '%'
        elif 'bytes' in id_lower or 'size' in id_lower:
            return 'MB'
        elif 'freq' in id_lower or 'hz' in id_lower:
            return 'MHz'
        elif 'count' in id_lower or 'num' in id_lower:
            return '#'
        elif 'speed' in id_lower or 'rate' in id_lower or 'throughput' in id_lower:
            return 'Mbps'
        else:
            return ''
    
    @property
    def suggested_min_max(self) -> Tuple[Optional[float], Optional[float]]:
        """Suggest min/max range based on collector ID"""
        id_lower = self.collector_id.lower()
        
        if 'percent' in id_lower or 'usage' in id_lower:
            return (0.0, 100.0)
        elif 'temp' in id_lower or 'temperature' in id_lower:
            return (0.0, 120.0)
        elif 'freq' in id_lower and 'cpu' in id_lower:
            return (800.0, 5000.0)  # MHz
        elif 'bytes' in id_lower or 'throughput' in id_lower:
            return (0.0, 10000.0)  # 10 Gbps
        else:
            # No default - return None for truly unknown metrics
            return (None, None)


class MinionDataSourceDiscovery:
    """Discover available data sources from Minion configuration"""
    
    def __init__(self, minion_config_path: Optional[Path] = None):
        """
        Initialize data source discovery.
        
        Args:
            minion_config_path: Path to MinionConfig.xml (optional)
        """
        self.config_path = Path(minion_config_path) if minion_config_path else None
        self.data_sources: List[DataSource] = []
        self._namespaces: Dict[str, str] = {}  # namespace_id -> name
        
        if self.config_path and self.config_path.exists():
            self.discover()
    
    def discover(self) -> List[DataSource]:
        """
        Discover all data sources from MinionConfig.xml.
        
        Returns:
            List of DataSource objects
        """
        if not self.config_path or not self.config_path.exists():
            return []
        
        try:
            tree = ET.parse(self.config_path)
            root = tree.getroot()
            
            self.data_sources = []
            
            # Parse each namespace
            for namespace_elem in root.findall('.//Namespace'):
                namespace_name = namespace_elem.find('Name')
                if namespace_name is not None:
                    ns_name = namespace_name.text or 'default'
                    
                    # Extract namespace metadata
                    self._namespaces[ns_name] = self._extract_namespace_info(namespace_elem)
                    
                    # Discover collectors
                    self.data_sources.extend(self._discover_collectors(namespace_elem, ns_name))
                    
                    # Discover plugins
                    self.data_sources.extend(self._discover_plugins(namespace_elem, ns_name))
                    
                    # Discover dynamic collectors
                    self.data_sources.extend(self._discover_dynamic_collectors(namespace_elem, ns_name))
            
            return self.data_sources
            
        except ET.ParseError as e:
            print(f"Error parsing MinionConfig.xml: {e}")
            return []
        except Exception as e:
            print(f"Error discovering data sources: {e}")
            return []
    
    def _extract_namespace_info(self, namespace_elem: ET.Element) -> str:
        """Extract namespace description"""
        # Try to get description from comments or name
        name = namespace_elem.find('Name')
        if name is not None and name.text:
            return name.text
        return "Unknown"
    
    def _discover_collectors(self, namespace_elem: ET.Element, namespace: str) -> List[DataSource]:
        """Discover standard collectors in namespace"""
        sources = []
        
        for collector in namespace_elem.findall('Collector'):
            collector_id = collector.get('ID', '')
            if not collector_id:
                continue
            
            frequency = int(collector.get('Frequency', 1000))
            
            # Get executable file
            executable = collector.find('Executable')
            collector_file = executable.text if executable is not None else None
            
            # Extract description from comments or ID
            description = self._generate_description(collector_id, collector_file)
            
            sources.append(DataSource(
                namespace=namespace,
                collector_id=collector_id,
                description=description,
                source_type='collector',
                collector_file=collector_file,
                frequency=frequency
            ))
        
        return sources
    
    def _discover_plugins(self, namespace_elem: ET.Element, namespace: str) -> List[DataSource]:
        """Discover plugin-based collectors (framework interface)"""
        sources = []
        
        for plugin in namespace_elem.findall('Plugin'):
            # Plugin collectors are discovered at runtime
            # We need to infer possible collectors from the plugin file
            
            python_file = plugin.find('PythonFile')
            entry_point = plugin.find('EntryPoint')
            
            if python_file is None:
                continue
            
            plugin_file = python_file.text
            entry_func = entry_point.text if entry_point is not None else 'collect'
            
            # Try to infer collector pattern from filename
            # e.g., Docker_Stats.py -> docker.*
            # e.g., LinuxNetwork.py -> netdev.*
            
            base_name = Path(plugin_file).stem if plugin_file else 'plugin'
            pattern = self._infer_plugin_pattern(base_name)
            
            description = f"Plugin: {base_name} (dynamic collectors)"
            
            # Create a generic source indicating this is a plugin
            sources.append(DataSource(
                namespace=namespace,
                collector_id=f"{pattern}.*",
                description=description,
                source_type='plugin',
                collector_file=plugin_file,
                metadata={'entry_point': entry_func, 'pattern': pattern}
            ))
        
        return sources
    
    def _discover_dynamic_collectors(self, namespace_elem: ET.Element, namespace: str) -> List[DataSource]:
        """Discover dynamic collectors (file watchers)"""
        sources = []
        
        for dynamic in namespace_elem.findall('DynamicCollector'):
            prefix = dynamic.get('Prefix', '')
            if not prefix:
                continue
            
            frequency = int(dynamic.get('Frequency', 1000))
            
            # Dynamic collectors create multiple IDs with the prefix
            # e.g., Prefix="port.1.netdev.eth0." creates port.1.netdev.eth0.tx_bytes, etc.
            
            description = f"Dynamic collector: {prefix}* (runtime discovery)"
            
            sources.append(DataSource(
                namespace=namespace,
                collector_id=f"{prefix}*",
                description=description,
                source_type='dynamic',
                frequency=frequency,
                metadata={'prefix': prefix}
            ))
        
        return sources
    
    def _infer_plugin_pattern(self, plugin_name: str) -> str:
        """Infer collector ID pattern from plugin filename"""
        name_lower = plugin_name.lower()
        
        # Common patterns
        patterns = {
            'docker': 'docker',
            'network': 'netdev',
            'linux_network': 'netdev',
            'cpu': 'cpu',
            'memory': 'mem',
            'disk': 'disk',
            'system': 'system',
        }
        
        for key, pattern in patterns.items():
            if key in name_lower:
                return pattern
        
        # Default: use filename as pattern
        return plugin_name.lower().replace('_', '.')
    
    def _generate_description(self, collector_id: str, collector_file: Optional[str]) -> str:
        """Generate human-readable description"""
        # Convert collector_id to readable format
        # e.g., cpu.usage -> CPU Usage
        # e.g., network.eth0.tx_bytes -> Network eth0 TX Bytes
        
        parts = collector_id.replace('_', ' ').split('.')
        readable = ' '.join(word.capitalize() for word in parts)
        
        if collector_file:
            filename = Path(collector_file).stem
            return f"{readable} ({filename})"
        
        return readable
    
    def search(self, query: str) -> List[DataSource]:
        """
        Search data sources by keyword.
        
        Args:
            query: Search query (matches namespace, ID, or description)
            
        Returns:
            Matching data sources
        """
        query_lower = query.lower()
        results = []
        
        for source in self.data_sources:
            if (query_lower in source.namespace.lower() or
                query_lower in source.collector_id.lower() or
                query_lower in source.description.lower()):
                results.append(source)
        
        return results
    
    def get_by_namespace(self, namespace: str) -> List[DataSource]:
        """Get all data sources in a specific namespace"""
        return [s for s in self.data_sources if s.namespace == namespace]
    
    def get_by_type(self, source_type: str) -> List[DataSource]:
        """Get all data sources of a specific type"""
        return [s for s in self.data_sources if s.source_type == source_type]
    
    def list_namespaces(self) -> List[str]:
        """Get list of all namespaces"""
        return list(set(s.namespace for s in self.data_sources))
    
    def format_source_list(self, sources: Optional[List[DataSource]] = None) -> str:
        """
        Format data sources as readable table.
        
        Args:
            sources: Data sources to format (defaults to all)
            
        Returns:
            Formatted table string
        """
        if sources is None:
            sources = self.data_sources
        
        if not sources:
            return "No data sources found"
        
        lines = []
        lines.append("=" * 80)
        lines.append("Available Data Sources")
        lines.append("=" * 80)
        lines.append(f"{'Namespace':<20} {'ID':<30} {'Type':<10} {'Description'}")
        lines.append("-" * 80)
        
        for source in sources:
            namespace = source.namespace[:19]
            collector_id = source.collector_id[:29]
            source_type = source.source_type[:9]
            description = source.description[:50]
            
            lines.append(f"{namespace:<20} {collector_id:<30} {source_type:<10} {description}")
        
        lines.append("=" * 80)
        lines.append(f"Total: {len(sources)} data sources")
        
        return '\n'.join(lines)


def discover_from_config(config_path: Path) -> MinionDataSourceDiscovery:
    """
    Convenience function to discover data sources from config file.
    
    Args:
        config_path: Path to MinionConfig.xml
        
    Returns:
        MinionDataSourceDiscovery instance with discovered sources
    """
    return MinionDataSourceDiscovery(config_path)


# Example usage
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python minion_discovery.py <MinionConfig.xml>")
        sys.exit(1)
    
    config_path = Path(sys.argv[1])
    
    discovery = discover_from_config(config_path)
    print(discovery.format_source_list())
    
    print("\n" + "=" * 80)
    print("Example Searches:")
    print("=" * 80)
    
    # Search examples
    for query in ['cpu', 'network', 'docker']:
        results = discovery.search(query)
        if results:
            print(f"\nSearch '{query}': {len(results)} results")
            for source in results[:3]:  # Show first 3
                print(f"  • {source.display_name} - {source.description}")
