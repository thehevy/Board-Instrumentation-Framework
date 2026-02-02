"""
Collector Discovery and Metadata Extraction

Scans BIFF Minion/Collectors directory to discover available collectors,
parse their metadata, and provide search/filter capabilities.
"""

import ast
import inspect
import re
import sys
import subprocess
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
                
                # Parse parameter descriptions from docstring
                param_descriptions = self._parse_param_descriptions(docstring)
                
                # Extract parameters with defaults
                parameters = []
                defaults = node.args.defaults
                num_defaults = len(defaults)
                num_args = len(node.args.args)
                
                for i, arg in enumerate(node.args.args):
                    if arg.arg == 'self':
                        continue
                    
                    # Check if this parameter has a default value
                    default_value = None
                    if num_args - i <= num_defaults:
                        default_idx = num_defaults - (num_args - i)
                        default_node = defaults[default_idx]
                        default_value = self._ast_to_string(default_node)
                    
                    param = FunctionParameter(
                        name=arg.arg,
                        type_hint=self._get_type_hint(arg.annotation) if arg.annotation else None,
                        default=default_value,
                        description=param_descriptions.get(arg.arg)
                    )
                    parameters.append(param)
                
                # Extract example from docstring
                example = self._extract_example_from_docstring(docstring)
                
                functions.append(FunctionInfo(
                    name=node.name,
                    description=docstring.split('\n')[0] if docstring else "",
                    parameters=parameters,
                    return_type=self._get_type_hint(node.returns) if node.returns else None,
                    example=example
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
    
    def check_dependencies(self, collector_name: str) -> Dict[str, bool]:
        """Check if collector dependencies are installed
        
        Args:
            collector_name: Name of collector to check
            
        Returns:
            Dict mapping dependency name to installed status
        """
        collector = self.get_collector(collector_name)
        if not collector:
            return {}
        
        status = {}
        for dep in collector.dependencies:
            try:
                __import__(dep)
                status[dep] = True
            except ImportError:
                status[dep] = False
        
        return status
    
    def get_missing_dependencies(self, collector_name: str) -> List[str]:
        """Get list of missing dependencies for collector
        
        Args:
            collector_name: Name of collector to check
            
        Returns:
            List of missing dependency names
        """
        dep_status = self.check_dependencies(collector_name)
        return [dep for dep, installed in dep_status.items() if not installed]
    
    def suggest_install_command(self, dependencies: List[str]) -> str:
        """Generate pip install command for missing dependencies
        
        Args:
            dependencies: List of dependency names
            
        Returns:
            pip install command string
        """
        if not dependencies:
            return ""
        
        return f"pip install {' '.join(dependencies)}"
    
    def test_collector(self, collector_name: str, function_name: Optional[str] = None, 
                      params: Optional[List[str]] = None) -> Dict[str, any]:
        """Test a collector by importing and calling it with sample parameters
        
        Args:
            collector_name: Name of collector to test
            function_name: Function to call (default: first function)
            params: List of parameters to pass
            
        Returns:
            Dict with keys: success (bool), output (str), error (str), exit_code (int)
        """
        collector = self.get_collector(collector_name)
        if not collector:
            return {
                'success': False,
                'output': '',
                'error': f"Collector '{collector_name}' not found",
                'exit_code': 1
            }
        
        # Check dependencies
        missing_deps = self.get_missing_dependencies(collector_name)
        if missing_deps:
            return {
                'success': False,
                'output': '',
                'error': f"Missing dependencies: {', '.join(missing_deps)}. Install with: {self.suggest_install_command(missing_deps)}",
                'exit_code': 1
            }
        
        # Select function
        if function_name:
            func = next((f for f in collector.functions if f.name == function_name), None)
            if not func:
                available = [f.name for f in collector.functions]
                return {
                    'success': False,
                    'output': '',
                    'error': f"Function '{function_name}' not found. Available: {', '.join(available)}",
                    'exit_code': 1
                }
        else:
            if not collector.functions:
                return {
                    'success': False,
                    'output': '',
                    'error': "No functions found in collector",
                    'exit_code': 1
                }
            func = collector.functions[0]
            function_name = func.name
        
        # Import collector module dynamically
        try:
            spec = importlib.util.spec_from_file_location(collector_name, collector.file_path)
            if not spec or not spec.loader:
                return {
                    'success': False,
                    'output': '',
                    'error': f'Failed to load collector module',
                    'exit_code': 1
                }
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[collector_name] = module
            spec.loader.exec_module(module)
            
            # Get the function
            if not hasattr(module, function_name):
                return {
                    'success': False,
                    'output': '',
                    'error': f"Function '{function_name}' not found in module",
                    'exit_code': 1
                }
            
            func_obj = getattr(module, function_name)
            
            # Call the function with parameters
            if params:
                result_value = func_obj(*params)
            else:
                result_value = func_obj()
            
            # Convert result to string
            output = str(result_value) if result_value is not None else "(no output)"
            
            return {
                'success': True,
                'output': output,
                'error': '',
                'exit_code': 0
            }
            
        except TypeError as e:
            # Wrong number of parameters
            param_count = len(params) if params else 0
            expected = len(func.parameters)
            return {
                'success': False,
                'output': '',
                'error': f"TypeError: Expected {expected} parameters, got {param_count}. {str(e)}",
                'exit_code': 1
            }
        except Exception as e:
            import traceback
            return {
                'success': False,
                'output': '',
                'error': f'Error calling collector: {str(e)}\n{traceback.format_exc()}',
                'exit_code': 1
            }
    
    def _get_type_hint(self, annotation) -> Optional[str]:
        """Convert AST type annotation to string"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        return None
    
    def _ast_to_string(self, node) -> str:
        """Convert AST node to string representation"""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Num):
            return str(node.n)
        elif isinstance(node, ast.Str):
            return repr(node.s)
        elif isinstance(node, ast.NameConstant):
            return str(node.value)
        elif isinstance(node, ast.List):
            return '[' + ', '.join(self._ast_to_string(e) for e in node.elts) + ']'
        elif isinstance(node, ast.Dict):
            items = [f'{self._ast_to_string(k)}: {self._ast_to_string(v)}' 
                    for k, v in zip(node.keys, node.values)]
            return '{' + ', '.join(items) + '}'
        else:
            return 'None'
    
    def _parse_param_descriptions(self, docstring: str) -> Dict[str, str]:
        """Parse parameter descriptions from docstring
        
        Supports multiple formats:
        - Args: / Parameters: section with param: description
        - @param param_name description
        - :param param_name: description
        """
        descriptions = {}
        if not docstring:
            return descriptions
        
        # Try Args:/Parameters: section
        args_match = re.search(r'(?:Args:|Parameters:)\s*\n((?:\s+\w+.*\n?)+)', docstring, re.MULTILINE)
        if args_match:
            args_section = args_match.group(1)
            # Parse lines like "    param_name: description" or "    param_name - description"
            for line in args_section.split('\n'):
                match = re.match(r'\s+(\w+)[:\-]\s*(.+)', line)
                if match:
                    param_name, desc = match.groups()
                    descriptions[param_name] = desc.strip()
        
        # Try @param format
        for match in re.finditer(r'@param\s+(\w+)\s+(.+)', docstring):
            param_name, desc = match.groups()
            descriptions[param_name] = desc.strip()
        
        # Try :param format
        for match in re.finditer(r':param\s+(\w+):\s*(.+)', docstring):
            param_name, desc = match.groups()
            descriptions[param_name] = desc.strip()
        
        return descriptions
    
    def _extract_example_from_docstring(self, docstring: str) -> Optional[str]:
        """Extract example code from docstring
        
        Looks for:
        - Example: section
        - Examples: section
        - Code blocks in docstring
        """
        if not docstring:
            return None
        
        # Try Example:/Examples: section
        example_match = re.search(r'(?:Example|Examples):\s*\n((?:\s+.+\n?)+)', docstring, re.MULTILINE | re.IGNORECASE)
        if example_match:
            example = example_match.group(1).strip()
            # Remove leading whitespace but preserve relative indentation
            lines = example.split('\n')
            min_indent = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
            return '\n'.join(line[min_indent:] for line in lines)
        
        # Try code blocks (``` or >>>)
        code_block_match = re.search(r'```(?:python)?\s*\n(.+?)\n```', docstring, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1).strip()
        
        # Try >>> prompts
        doctest_match = re.search(r'((?:^\s*>>>.*\n?)+)', docstring, re.MULTILINE)
        if doctest_match:
            return doctest_match.group(1).strip()
        
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
