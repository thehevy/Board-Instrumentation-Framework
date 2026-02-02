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
    
    def search_collectors(
        self,
        by_category: Optional[str] = None,
        by_dependency: Optional[str] = None,
        has_function: Optional[str] = None,
        min_functions: Optional[int] = None
    ) -> List[CollectorInfo]:
        """Advanced search with multiple filters
        
        Args:
            by_category: Filter by category (e.g., 'system', 'docker', 'monitoring')
            by_dependency: Filter by required dependency (e.g., 'psutil', 'docker')
            has_function: Filter collectors that have a function matching this name (partial match)
            min_functions: Filter collectors with at least this many functions
            
        Returns:
            List of collectors matching all specified filters
            
        Example:
            # Find system collectors with at least 2 functions
            results = discovery.search_collectors(by_category='system', min_functions=2)
            
            # Find collectors using psutil
            results = discovery.search_collectors(by_dependency='psutil')
        """
        collectors = self.list_collectors()
        results = []
        
        for collector in collectors:
            # Apply category filter
            if by_category and collector.category != by_category:
                continue
            
            # Apply dependency filter
            if by_dependency:
                if by_dependency not in collector.dependencies:
                    continue
            
            # Apply function name filter (partial match, case-insensitive)
            if has_function:
                has_func_lower = has_function.lower()
                if not any(has_func_lower in func.name.lower() for func in collector.functions):
                    continue
            
            # Apply minimum functions filter
            if min_functions and len(collector.functions) < min_functions:
                continue
            
            results.append(collector)
        
        return results
    
    def full_text_search(self, query: str, max_results: int = 10) -> List[tuple[CollectorInfo, float]]:
        """Full-text search with relevance scoring
        
        Searches in:
        - Collector name (highest weight)
        - Collector description
        - Function names
        - Function descriptions
        - Parameter descriptions
        - Examples
        
        Args:
            query: Search query (space-separated keywords)
            max_results: Maximum number of results to return
            
        Returns:
            List of (collector, score) tuples sorted by relevance score (highest first)
            
        Example:
            results = discovery.full_text_search("cpu usage monitoring")
            for collector, score in results:
                print(f"{collector.name}: {score:.2f}")
        """
        collectors = self.list_collectors()
        keywords = query.lower().split()
        scored_results = []
        
        for collector in collectors:
            score = 0.0
            
            # Score collector name (weight: 5.0)
            for keyword in keywords:
                if keyword in collector.name.lower():
                    score += 5.0
            
            # Score collector description (weight: 2.0)
            for keyword in keywords:
                if keyword in collector.description.lower():
                    score += 2.0
            
            # Score category (weight: 1.5)
            for keyword in keywords:
                if keyword in collector.category.lower():
                    score += 1.5
            
            # Score function names (weight: 3.0)
            for func in collector.functions:
                for keyword in keywords:
                    if keyword in func.name.lower():
                        score += 3.0
            
            # Score function descriptions (weight: 1.0)
            for func in collector.functions:
                if func.description:
                    for keyword in keywords:
                        if keyword in func.description.lower():
                            score += 1.0
            
            # Score parameter descriptions (weight: 0.5)
            for func in collector.functions:
                for param in func.parameters:
                    if param.description:
                        for keyword in keywords:
                            if keyword in param.description.lower():
                                score += 0.5
            
            # Score examples (weight: 0.8)
            for example in collector.examples:
                for keyword in keywords:
                    if keyword in example.lower():
                        score += 0.8
            
            if score > 0:
                scored_results.append((collector, score))
        
        # Sort by score (highest first) and limit results
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:max_results]
    
    def search_by_function(self, function_name: str, exact: bool = False) -> List[CollectorInfo]:
        """Search collectors by function name
        
        Args:
            function_name: Function name to search for
            exact: If True, require exact match; if False, partial match (default)
            
        Returns:
            List of collectors containing matching functions
            
        Example:
            # Find collectors with "GetUsage" function
            results = discovery.search_by_function("GetUsage", exact=True)
            
            # Find collectors with any function containing "cpu"
            results = discovery.search_by_function("cpu", exact=False)
        """
        collectors = self.list_collectors()
        results = []
        
        func_lower = function_name.lower()
        
        for collector in collectors:
            for func in collector.functions:
                if exact:
                    if func.name == function_name:
                        results.append(collector)
                        break
                else:
                    if func_lower in func.name.lower():
                        results.append(collector)
                        break
        
        return results
    
    def regex_search(
        self,
        pattern: str,
        search_in: str = 'all'
    ) -> List[CollectorInfo]:
        """Regular expression search
        
        Args:
            pattern: Regular expression pattern
            search_in: Where to search - 'name', 'description', 'functions', or 'all'
            
        Returns:
            List of collectors matching the pattern
            
        Raises:
            re.error: If pattern is invalid
            
        Example:
            # Find collectors starting with "Docker"
            results = discovery.regex_search(r'^Docker', search_in='name')
            
            # Find collectors with functions matching pattern
            results = discovery.regex_search(r'Get\\w+Usage', search_in='functions')
        """
        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        
        collectors = self.list_collectors()
        results = []
        
        for collector in collectors:
            match_found = False
            
            # Search in name
            if search_in in ('name', 'all'):
                if compiled_pattern.search(collector.name):
                    match_found = True
            
            # Search in description
            if not match_found and search_in in ('description', 'all'):
                if compiled_pattern.search(collector.description):
                    match_found = True
            
            # Search in function names
            if not match_found and search_in in ('functions', 'all'):
                for func in collector.functions:
                    if compiled_pattern.search(func.name):
                        match_found = True
                        break
            
            if match_found:
                results.append(collector)
        
        return results
    
    def generate_collector_xml(
        self,
        collector_name: str,
        function_name: Optional[str] = None,
        collector_id: Optional[str] = None,
        frequency: int = 1000,
        include_all_params: bool = False
    ) -> str:
        """Generate XML configuration snippet for a collector
        
        Args:
            collector_name: Name of the collector
            function_name: Specific function to use (default: first function)
            collector_id: Custom ID for the collector (default: collector_name.function_name)
            frequency: Collection frequency in milliseconds (default: 1000)
            include_all_params: Include optional parameters with defaults (default: False)
            
        Returns:
            XML configuration string
            
        Raises:
            ValueError: If collector or function not found
            
        Example:
            xml = discovery.generate_collector_xml('RandomVal', 'GetBoundedRandomValue')
            # Returns:
            # <Collector ID="RandomVal.GetBoundedRandomValue" Frequency="1000">
            #   <Executable>Collectors\\RandomVal.py</Executable>
            #   <Param>GetBoundedRandomValue</Param>
            #   <Param>0</Param>
            #   <Param>100</Param>
            # </Collector>
        """
        # Get collector info
        collector = self.get_collector(collector_name)
        if not collector:
            raise ValueError(f"Collector '{collector_name}' not found")
        
        # Find function
        if function_name:
            func = next((f for f in collector.functions if f.name == function_name), None)
            if not func:
                raise ValueError(f"Function '{function_name}' not found in collector '{collector_name}'")
        else:
            if not collector.functions:
                raise ValueError(f"Collector '{collector_name}' has no functions")
            func = collector.functions[0]
        
        # Generate ID
        if not collector_id:
            collector_id = f"{collector_name}.{func.name}"
        
        # Build XML
        xml_lines = []
        xml_lines.append(f'  <Collector ID="{collector_id}" Frequency="{frequency}">')
        
        # Executable path (relative to Minion directory)
        relative_path = collector.file_path.relative_to(self.biff_root / "Minion")
        xml_lines.append(f'    <Executable>{relative_path}</Executable>')
        
        # Function name as first param
        xml_lines.append(f'    <Param>{func.name}</Param>')
        
        # Add required parameters
        for param in func.parameters:
            if param.default is None:  # Required parameter
                xml_lines.append(f'    <Param><!-- {param.name}: {param.description or "value"} --></Param>')
            elif include_all_params:  # Optional parameter with default
                default_val = param.default.strip("'\"")  # Remove quotes
                xml_lines.append(f'    <Param>{default_val}</Param>  <!-- {param.name} (optional) -->')
        
        xml_lines.append('  </Collector>')
        
        return '\n'.join(xml_lines)
    
    def validate_collector_config(self, xml_string: str) -> tuple[bool, List[str]]:
        """Validate collector XML configuration
        
        Args:
            xml_string: XML configuration to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
            
        Example:
            valid, errors = discovery.validate_collector_config(xml_str)
            if not valid:
                for error in errors:
                    print(f"Error: {error}")
        """
        import xml.dom.minidom as minidom
        
        errors = []
        
        try:
            doc = minidom.parseString(xml_string)
        except Exception as e:
            errors.append(f"Invalid XML: {e}")
            return False, errors
        
        # Check for Collector element
        collectors = doc.getElementsByTagName('Collector')
        if not collectors:
            errors.append("No <Collector> element found")
            return False, errors
        
        for collector in collectors:
            # Check required attributes
            if not collector.hasAttribute('ID'):
                errors.append("Collector missing 'ID' attribute")
            
            if not collector.hasAttribute('Frequency'):
                errors.append("Collector missing 'Frequency' attribute")
            else:
                try:
                    freq = int(collector.getAttribute('Frequency'))
                    if freq <= 0:
                        errors.append(f"Frequency must be positive, got {freq}")
                except ValueError:
                    errors.append(f"Frequency must be a number")
            
            # Check for Executable element
            executables = collector.getElementsByTagName('Executable')
            if not executables:
                errors.append("Collector missing <Executable> element")
            
            # Check for at least one Param (function name)
            params = collector.getElementsByTagName('Param')
            if not params:
                errors.append("Collector missing <Param> elements (at least function name required)")
        
        return len(errors) == 0, errors
    
    def customize_template(
        self,
        xml_string: str,
        new_id: Optional[str] = None,
        new_frequency: Optional[int] = None,
        param_values: Optional[Dict[int, str]] = None
    ) -> str:
        """Customize an XML collector template
        
        Args:
            xml_string: Original XML template
            new_id: New collector ID (optional)
            new_frequency: New frequency in ms (optional)
            param_values: Dict of {param_index: value} to replace (0-based, excluding function name)
            
        Returns:
            Customized XML string
            
        Example:
            xml = discovery.generate_collector_xml('RandomVal', 'GetBoundedRandomValue')
            custom = discovery.customize_template(
                xml,
                new_id='cpu.usage',
                new_frequency=500,
                param_values={0: '0', 1: '1000'}  # min=0, max=1000
            )
        """
        import xml.dom.minidom as minidom
        
        try:
            doc = minidom.parseString(xml_string)
        except Exception as e:
            raise ValueError(f"Invalid XML: {e}")
        
        collectors = doc.getElementsByTagName('Collector')
        if not collectors:
            raise ValueError("No <Collector> element found")
        
        collector = collectors[0]
        
        # Update ID
        if new_id:
            collector.setAttribute('ID', new_id)
        
        # Update Frequency
        if new_frequency:
            collector.setAttribute('Frequency', str(new_frequency))
        
        # Update parameter values
        if param_values:
            params = collector.getElementsByTagName('Param')
            # Skip first param (function name)
            for idx, value in param_values.items():
                param_idx = idx + 1  # +1 to skip function name
                if param_idx < len(params):
                    # Clear existing content
                    while params[param_idx].firstChild:
                        params[param_idx].removeChild(params[param_idx].firstChild)
                    # Add new text node
                    params[param_idx].appendChild(doc.createTextNode(value))
        
        return doc.toxml()
    
    def generate_namespace_config(
        self,
        namespace_name: str,
        collectors: List[tuple[str, str]],
        target_ip: str = "localhost",
        target_port: int = 5100,
        default_frequency: int = 1000
    ) -> str:
        """Generate complete namespace configuration with multiple collectors
        
        Args:
            namespace_name: Name of the namespace
            collectors: List of (collector_name, function_name) tuples
            target_ip: Target connection IP (default: localhost)
            target_port: Target connection port (default: 5100)
            default_frequency: Default frequency for collectors (default: 1000)
            
        Returns:
            Complete namespace XML configuration
            
        Example:
            config = discovery.generate_namespace_config(
                'System',
                [('CPU', 'GetCPU_Percentage'), ('Memory', 'GetMemory')],
                target_ip='192.168.1.100',
                target_port=5100
            )
        """
        xml_lines = []
        xml_lines.append(f'<Namespace>')
        xml_lines.append(f'  <Name>{namespace_name}</Name>')
        xml_lines.append(f'  <DefaultFrequency>{default_frequency}</DefaultFrequency>')
        xml_lines.append(f'  <TargetConnection IP="{target_ip}" PORT="{target_port}"/>')
        xml_lines.append('')
        
        for collector_name, function_name in collectors:
            try:
                collector_xml = self.generate_collector_xml(
                    collector_name,
                    function_name,
                    frequency=default_frequency
                )
                xml_lines.append(collector_xml)
                xml_lines.append('')
            except ValueError as e:
                xml_lines.append(f'  <!-- Error: {e} -->')
                xml_lines.append('')
        
        xml_lines.append('</Namespace>')
        
        return '\n'.join(xml_lines)


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
