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
    
    def __init__(self, biff_root: Optional[Path] = None):
        """Initialize generator
        
        Args:
            biff_root: Optional BIFF installation root for CollectorDiscovery
        """
        super().__init__()
        self._discovery = None
        self._biff_root = biff_root
    
    def _get_discovery(self):
        """Lazy load CollectorDiscovery"""
        if self._discovery is None and self._biff_root:
            try:
                from biff_agents_core.utils.collector_discovery import CollectorDiscovery
                self._discovery = CollectorDiscovery(self._biff_root)
            except Exception:
                pass  # Discovery not available
        return self._discovery
    
    # Collector definitions with their parameters
    COLLECTOR_TEMPLATES = {
        "RandomVal": {
            "executable": "Collectors/RandomVal.py",
            "params": ["GetBoundedRandomValue", "0", "100"],  # Function name + parameters
            "description": "Random value between 0-100"
        },
        # Note: Timer.py has complex state management requirements
        # Requires specific action sequences (create, start, get)
        # Consider using RandomVal for simple testing instead
        # "Timer": {
        #     "executable": "Collectors/Timer.py",
        #     "params": ["Timer", "timer_id", "get_auto_create"],
        #     "description": "Elapsed time (requires state management)"
        # },
        "CPU": {
            "executable": "Collectors/CPU.py",
            "params": ["GetCPU_Percentage"],  # Correct function name
            "description": "CPU utilization percentage"
        },
        "Network": {
            "executable": "Collectors/Network.py",
            "params": ["GetBytesRecv"],
            "description": "Network bytes received"
        }
        # Note: Memory and Storage functions do not exist in CPU.py
        # Remove these templates - they reference non-existent functions
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
    
    def suggest_collectors(self, use_case: str) -> List[str]:
        """Suggest collectors based on use case
        
        Args:
            use_case: Description of what user wants to monitor
                (e.g., "system performance", "docker containers", "testing")
        
        Returns:
            List of suggested collector names
        """
        discovery = self._get_discovery()
        if not discovery:
            # Fallback to hardcoded suggestions
            use_case_lower = use_case.lower()
            if "system" in use_case_lower or "performance" in use_case_lower:
                return ["CPU", "Memory", "Network", "Storage"]
            elif "docker" in use_case_lower or "container" in use_case_lower:
                return ["Docker_Stats"]
            elif "test" in use_case_lower:
                return ["RandomVal", "Timer"]
            else:
                return ["RandomVal"]
        
        # Use discovery to find relevant collectors
        results = discovery.search(use_case)
        return [c.name for c in results[:5]]  # Return top 5
    
    def get_collector_by_category(self, category: str) -> List[str]:
        """Get all collectors in a category
        
        Args:
            category: Category name (system, containers, monitoring, etc.)
        
        Returns:
            List of collector names in category
        """
        discovery = self._get_discovery()
        if not discovery:
            return []
        
        collectors = discovery.get_by_category(category)
        return [c.name for c in collectors]
    
    def get_available_categories(self) -> List[str]:
        """Get list of all collector categories
        
        Returns:
            List of category names
        """
        discovery = self._get_discovery()
        if not discovery:
            return ["system", "containers", "monitoring", "testing"]
        
        return discovery.get_categories()
    
    def get_collector_info(self, collector_name: str) -> Optional[Dict]:
        """Get detailed information about a collector
        
        Args:
            collector_name: Name of collector
        
        Returns:
            Dict with collector info or None if not found
        """
        discovery = self._get_discovery()
        if not discovery:
            # Fallback to templates
            if collector_name in self.COLLECTOR_TEMPLATES:
                return self.COLLECTOR_TEMPLATES[collector_name]
            return None
        
        collector = discovery.get_collector(collector_name)
        if not collector:
            return None
        
        # Convert CollectorInfo to dict format
        return {
            "name": collector.name,
            "executable": f"Collectors/{collector.file_path.name}",
            "description": collector.description,
            "functions": [f.name for f in collector.functions],
            "parameters": [p.name for f in collector.functions for p in f.parameters],
            "category": collector.category,
            "dependencies": collector.dependencies
        }

    
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
