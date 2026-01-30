"""
Collector Discovery and Metadata Extraction

Scans BIFF Minion/Collectors directory to discover available collectors,
parse their metadata, and provide search/filter capabilities.
"""

import ast
import inspect
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Callable
import importlib.util


@dataclass
class FunctionParameter:
    """Represents a function parameter"""
    name: str
    type_hint: Optional[str] = None
    default: Optional[str] = None
    description: Optional[str] = None


@dataclass
class FunctionInfo:
    """Metadata about a collector function"""
    name: str
    description: str
    parameters: List[FunctionParameter]
    return_type: Optional[str] = None
    example: Optional[str] = None


@dataclass
class CollectorInfo:
    """Complete metadata about a collector"""
    name: str
    file_path: Path
    description: str
    functions: List[FunctionInfo] = field(default_factory=list)
    category: str = "other"
    dependencies: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    
    def matches_query(self, query: str) -> bool:
        """Check if collector matches search query"""
        query_lower = query.lower()
        return (
            query_lower in self.name.lower() or
            query_lower in self.description.lower() or
            query_lower in self.category.lower() or
            any(query_lower in func.name.lower() for func in self.functions)
        )


class CollectorDiscovery:
    """Discovers and parses collector metadata from BIFF installation"""
    
    # Category mapping based on collector purpose
    CATEGORIES = {
        'CPU': 'system',
        'Memory': 'system',
        'Network': 'system',
        'Storage': 'system',
        'SystemInfo_Linux': 'system',
        'Linux_CPU': 'system',
        'LinuxNetwork': 'system',
        'Docker_Stats': 'containers',
        'Docker_CgroupStats': 'containers',
        'LibVirt': 'virtualization',
        'esxHostCollector': 'virtualization',
        'Prometheus': 'monitoring',
        'InfluxDB': 'monitoring',
        'Collectd': 'monitoring',
        'TelegrafJsonCollector': 'monitoring',
        'RandomVal': 'testing',
        'Timer': 'testing',
        'Parrot': 'testing',
        'PluginTester': 'testing',
        'StockTicker': 'demo',
        'JsonCollector': 'data',
        'FileCollector': 'data',
        'SimpleCSVReader': 'data',
        'NetCat': 'networking',
        'PowerShell': 'scripting',
        'MinionInfo': 'meta'
    }
    
    def __init__(self, biff_root: Path):
        """Initialize discovery with BIFF installation root"""
        self.biff_root = biff_root
        self.collectors_dir = biff_root / "Minion" / "Collectors"
        self._cache: Dict[str, CollectorInfo] = {}
        
        if not self.collectors_dir.exists():
            raise ValueError(f"Collectors directory not found: {self.collectors_dir}")
    
    def list_collectors(self, category: Optional[str] = None) -> List[CollectorInfo]:
        """
        List all discovered collectors
        
        Args:
            category: Optional category filter (system, containers, monitoring, etc.)
            
        Returns:
            List of CollectorInfo objects
        """
        if not self._cache:
            self._scan_collectors()
        
        collectors = list(self._cache.values())
        
        if category:
            collectors = [c for c in collectors if c.category == category.lower()]
        
        return sorted(collectors, key=lambda c: c.name)
    
    def get_collector(self, name: str) -> Optional[CollectorInfo]:
        """
        Get detailed info for a specific collector
        
        Args:
            name: Collector name (e.g., "CPU", "RandomVal")
            
        Returns:
            CollectorInfo or None if not found
        """
        if not self._cache:
            self._scan_collectors()
        
        return self._cache.get(name)
    
    def search(self, query: str) -> List[CollectorInfo]:
        """
        Search collectors by keyword
        
        Args:
            query: Search term (matches name, description, category, functions)
            
        Returns:
            List of matching collectors sorted by relevance
        """
        if not self._cache:
            self._scan_collectors()
        
        matches = [
            collector for collector in self._cache.values()
            if collector.matches_query(query)
        ]
        
        # Simple relevance scoring: exact name match scores highest
        def relevance_score(collector: CollectorInfo) -> int:
            query_lower = query.lower()
            score = 0
            if collector.name.lower() == query_lower:
                score += 100
            if query_lower in collector.name.lower():
                score += 50
            if query_lower in collector.description.lower():
                score += 25
            if query_lower == collector.category.lower():
                score += 10
            return score
        
        return sorted(matches, key=relevance_score, reverse=True)
    
    def get_by_category(self, category: str) -> List[CollectorInfo]:
        """Get all collectors in a specific category"""
        return self.list_collectors(category=category)
    
    def get_categories(self) -> List[str]:
        """Get list of all available categories"""
        if not self._cache:
            self._scan_collectors()
        
        categories = set(c.category for c in self._cache.values())
        return sorted(categories)
    
    def _scan_collectors(self):
        """Scan collectors directory and populate cache"""
        if not self.collectors_dir.exists():
            return
        
        for py_file in self.collectors_dir.glob("*.py"):
            # Skip special files
            if py_file.name.startswith('__') or py_file.name.startswith('.'):
                continue
            
            collector_name = py_file.stem
            collector_info = self._parse_collector(py_file, collector_name)
            
            if collector_info:
                self._cache[collector_name] = collector_info
    
    def _parse_collector(self, file_path: Path, name: str) -> Optional[CollectorInfo]:
        """
        Parse a collector Python file to extract metadata
        
        Args:
            file_path: Path to collector .py file
            name: Collector name
            
        Returns:
            CollectorInfo or None if parsing fails
        """
        try:
            # Read with UTF-8-SIG to handle BOM (byte order mark)
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                source = f.read()
            
            # Parse AST
            tree = ast.parse(source)
            
            # Extract module-level docstring (file abstract)
            description = self._extract_file_abstract(source)
            if not description:
                description = f"{name} collector"
            
            # Extract functions
            functions = self._extract_functions(tree, source)
            
            # Detect dependencies
            dependencies = self._extract_dependencies(tree)
            
            # Determine category
            category = self.CATEGORIES.get(name, 'other')
            
            return CollectorInfo(
                name=name,
                file_path=file_path,
                description=description,
                functions=functions,
                category=category,
                dependencies=dependencies
            )
            
        except Exception as e:
            # Log error but don't fail entire discovery
            print(f"Warning: Could not parse {file_path.name}: {e}")
            return None
    
    def _extract_file_abstract(self, source: str) -> str:
        """Extract file abstract from header comments"""
        # Look for "File Abstract:" in header
        match = re.search(r'#\s*File Abstract:\s*\n#\s*(.+?)(?:\n#\s*\n|$)', source, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # Fallback: look for module docstring
        match = re.search(r'^"""(.+?)"""', source, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(1).strip().split('\n')[0]  # First line
        
        return ""
    
    def _extract_functions(self, tree: ast.AST, source: str) -> List[FunctionInfo]:
        """Extract function definitions from AST"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions
                if node.name.startswith('_'):
                    continue
                
                # Extract function docstring
                docstring = ast.get_docstring(node) or ""
                
                # Extract parameters
                parameters = []
                for arg in node.args.args:
                    if arg.arg == 'self':
                        continue
                    
                    param = FunctionParameter(
                        name=arg.arg,
                        type_hint=self._get_type_hint(arg.annotation) if arg.annotation else None
                    )
                    parameters.append(param)
                
                functions.append(FunctionInfo(
                    name=node.name,
                    description=docstring.split('\n')[0] if docstring else "",
                    parameters=parameters,
                    return_type=self._get_type_hint(node.returns) if node.returns else None
                ))
        
        return functions
    
    def _extract_dependencies(self, tree: ast.AST) -> List[str]:
        """Extract required dependencies from imports"""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Skip stdlib modules
                    if alias.name not in ['os', 'sys', 're', 'time', 'random', 'json']:
                        dependencies.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module not in ['os', 'sys', 're', 'time', 'random', 'json']:
                    dependencies.append(node.module)
        
        return list(set(dependencies))  # Deduplicate
    
    def _get_type_hint(self, annotation) -> Optional[str]:
        """Convert AST type annotation to string"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        return None


def main():
    """Test collector discovery"""
    import sys
    from pathlib import Path
    
    # Assume BIFF is in parent directory
    biff_root = Path(__file__).parent.parent.parent
    
    try:
        discovery = CollectorDiscovery(biff_root)
        collectors = discovery.list_collectors()
        
        print(f"Found {len(collectors)} collectors:")
        for collector in collectors:
            print(f"  - {collector.name} ({collector.category}): {collector.description[:60]}...")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
