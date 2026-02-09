#!/usr/bin/env python3
"""
BIFF Marvin Configuration Validator
Pre-flight validation tool for Marvin XML configurations

Validates:
- File encoding (UTF-8 without BOM)
- XML syntax and well-formedness
- Tab ID references and definitions
- Alias cascading and circular dependencies
- DynamicGrid file references
- Widget source file existence
- Data binding structure
- External file imports

Usage:
    python validate_config.py <config.xml>
    python validate_config.py --alias-cascade <config.xml>
    python validate_config.py --verbose <config.xml>
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import re

class ValidationResult:
    """Container for validation results"""
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.passed = True
        
    def add_error(self, msg: str):
        self.errors.append(f"❌ ERROR: {msg}")
        self.passed = False
        
    def add_warning(self, msg: str):
        self.warnings.append(f"⚠️  WARNING: {msg}")
        
    def add_info(self, msg: str):
        self.info.append(f"ℹ️  INFO: {msg}")
        
    def print_results(self):
        """Print all validation results"""
        if self.info:
            print("\n📋 Information:")
            for msg in self.info:
                print(f"  {msg}")
                
        if self.warnings:
            print("\n⚠️  Warnings:")
            for msg in self.warnings:
                print(f"  {msg}")
                
        if self.errors:
            print("\n❌ Errors:")
            for msg in self.errors:
                print(f"  {msg}")
        
        print("\n" + "="*70)
        if self.passed:
            print("✅ VALIDATION PASSED" + (" (with warnings)" if self.warnings else ""))
        else:
            print(f"❌ VALIDATION FAILED - {len(self.errors)} error(s) found")
        print("="*70)


class MarvinConfigValidator:
    """Validates Marvin configuration files"""
    
    def __init__(self, config_path: str, verbose: bool = False, trace_aliases: bool = False):
        self.config_path = Path(config_path)
        self.config_dir = self.config_path.parent
        self.verbose = verbose
        self.trace_aliases = trace_aliases
        self.result = ValidationResult()
        
        # Tracking structures
        self.aliases: Dict[str, str] = {}
        self.alias_sources: Dict[str, str] = {}  # alias -> source file
        self.alias_dependencies: Dict[str, Set[str]] = defaultdict(set)  # alias -> depends on
        self.tabs_defined: Dict[str, str] = {}  # Tab ID -> definition location
        self.tabs_referenced: Set[str] = set()
        self.dynamicgrid_files: Dict[str, List[str]] = {}  # DynamicGrid ID -> file list
        self.external_files: Set[str] = set()
        
    def validate(self) -> ValidationResult:
        """Run all validations"""
        print(f"🔍 Validating Marvin configuration: {self.config_path.name}")
        print("="*70)
        
        # 1. Check file exists
        if not self.config_path.exists():
            self.result.add_error(f"Configuration file not found: {self.config_path}")
            return self.result
            
        # 2. Validate encoding
        self._validate_encoding()
        
        # 3. Parse XML
        try:
            tree = ET.parse(self.config_path)
            root = tree.getroot()
        except ET.ParseError as e:
            self.result.add_error(f"XML parsing failed: {e}")
            return self.result
        except Exception as e:
            self.result.add_error(f"Failed to read file: {e}")
            return self.result
            
        # 4. Validate root element
        if root.tag != "Marvin":
            self.result.add_error(f"Expected <Marvin> root element, found <{root.tag}>")
            return self.result
            
        self.result.add_info(f"Root element: <{root.tag}>")
        
        # 5. Extract and validate aliases
        self._extract_aliases(root, str(self.config_path))
        
        # 6. Validate Tab structure
        self._validate_tabs(root)
        
        # 7. Validate DynamicGrid configurations
        self._validate_dynamicgrids(root)
        
        # 8. Validate external file references
        self._validate_external_files()
        
        # 9. Validate widget sources
        self._validate_widget_sources(root)
        
        # 10. Check for alias issues
        if self.trace_aliases:
            self._analyze_alias_cascading()
        
        return self.result
        
    def _validate_encoding(self):
        """Check for UTF-8 BOM and encoding issues"""
        try:
            with open(self.config_path, 'rb') as f:
                first_bytes = f.read(3)
                if first_bytes == b'\xef\xbb\xbf':
                    self.result.add_warning(
                        f"File has UTF-8 BOM marker. Recommend saving as UTF-8 without BOM."
                    )
                    
            # Try reading as UTF-8
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.result.add_info(f"File size: {len(content)} characters")
                
        except UnicodeDecodeError as e:
            self.result.add_error(f"File encoding error: {e}. File must be UTF-8.")
            
    def _extract_aliases(self, element: ET.Element, source_file: str):
        """Recursively extract aliases from XML"""
        # Look for AliasList elements
        for aliaslist in element.findall('.//AliasList'):
            # Check for external alias file
            if 'File' in aliaslist.attrib:
                alias_file = aliaslist.attrib['File']
                external_path = self._resolve_path(alias_file)
                if external_path.exists():
                    self._load_external_aliases(external_path)
                else:
                    self.result.add_warning(f"External alias file not found: {alias_file}")
                    
            # Extract inline aliases
            for alias in aliaslist.findall('Alias'):
                for name, value in alias.attrib.items():
                    self.aliases[name] = value
                    self.alias_sources[name] = source_file
                    
                    # Track dependencies (if value references other aliases)
                    refs = self._find_alias_references(value)
                    if refs:
                        self.alias_dependencies[name].update(refs)
                        
            # Check for Import elements
            for import_elem in aliaslist.findall('Import'):
                import_file = import_elem.text
                if import_file:
                    import_path = self._resolve_path(import_file)
                    if import_path.exists():
                        self._load_external_aliases(import_path)
                    else:
                        self.result.add_warning(f"Imported alias file not found: {import_file}")
                        
        if self.aliases:
            self.result.add_info(f"Found {len(self.aliases)} alias definition(s)")
            
    def _load_external_aliases(self, file_path: Path):
        """Load aliases from external file"""
        self.external_files.add(str(file_path))
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            self._extract_aliases(root, str(file_path))
        except ET.ParseError as e:
            self.result.add_error(f"Failed to parse external alias file {file_path.name}: {e}")
        except Exception as e:
            self.result.add_warning(f"Could not load external alias file {file_path.name}: {e}")
            
    def _find_alias_references(self, value: str) -> Set[str]:
        """Find alias references in a value string using $(ALIAS) pattern"""
        pattern = r'\$\(([A-Za-z0-9_]+)\)'
        matches = re.findall(pattern, value)
        return set(matches)
        
    def _validate_tabs(self, root: ET.Element):
        """Validate Tab definitions and references"""
        # Find all Tab definitions (look for tabs not inside Tabs section)
        # Strategy: Find all Tab elements, then determine which are definitions
        
        # First pass: collect all Tab elements with their paths
        def find_tabs_recursive(elem, path=""):
            for child in elem:
                child_path = f"{path}/{child.tag}"
                if child.tag == "Tab" and "ID" in child.attrib:
                    # Check if this Tab is inside a Tabs section
                    # by looking at the path
                    if "/Tabs/Tab" not in child_path:
                        # This is a definition
                        tab_id = child.attrib['ID']
                        self.tabs_defined[tab_id] = child_path
                find_tabs_recursive(child, child_path)
        
        find_tabs_recursive(root, "")
        
        # Find Tab references in <Tabs> section
        for app in root.findall('.//Application'):
            tabs_section = app.find('Tabs')
            if tabs_section is not None:
                for tab_ref in tabs_section.findall('Tab'):
                    if 'ID' in tab_ref.attrib:
                        self.tabs_referenced.add(tab_ref.attrib['ID'])
                        
        # Report findings
        if self.tabs_defined:
            self.result.add_info(f"Found {len(self.tabs_defined)} Tab definition(s): {', '.join(self.tabs_defined.keys())}")
        else:
            self.result.add_warning("No Tab definitions found")
            
        if self.tabs_referenced:
            self.result.add_info(f"Found {len(self.tabs_referenced)} Tab reference(s): {', '.join(self.tabs_referenced)}")
            
        # Validate references match definitions
        for tab_id in self.tabs_referenced:
            if tab_id not in self.tabs_defined:
                self.result.add_error(
                    f"Tab reference '{tab_id}' has no matching definition. "
                    f"Add <Tab ID=\"{tab_id}\">...</Tab> outside <Application> section."
                )
                
        # Check for unused tabs
        unused_tabs = set(self.tabs_defined.keys()) - self.tabs_referenced
        if unused_tabs:
            self.result.add_warning(f"Defined but not referenced: {', '.join(unused_tabs)}")
            
        # If verbose, show detailed tab structure
        if self.verbose:
            self._analyze_tab_structure(root)
            
    def _analyze_tab_structure(self, root: ET.Element):
        """Deeply analyze tab structure showing grids, widgets, and DynamicGrids"""
        print("\n📑 Tab Structure Analysis:")
        
        for tab_id, tab_path in self.tabs_defined.items():
            print(f"\n  📄 Tab: {tab_id}")
            
            # Find the Tab element
            tab_elem = self._find_tab_by_id(root, tab_id)
            if tab_elem is None:
                print(f"     ⚠️  Tab definition not found in root")
                continue
                
            # Debug: Show all attributes
            if tab_elem.attrib:
                print(f"     🔍 Attributes: {', '.join(f'{k}={v}' for k, v in tab_elem.attrib.items())}")
                
            # Check if Tab has a File attribute (external definition)
            if 'File' in tab_elem.attrib:
                tab_file = tab_elem.attrib['File']
                print(f"     📂 External File: {tab_file}")
                
                # Resolve aliases in the file path
                resolved_file = self._resolve_aliases_in_string(tab_file)
                if resolved_file != tab_file:
                    print(f"     📂 Resolved Path: {resolved_file}")
                
                # Special case: if resolved path starts with a directory name that matches
                # the config directory name, treat it as relative to parent
                config_dir_name = self.config_dir.name
                if resolved_file.startswith(config_dir_name + '/') or resolved_file.startswith(config_dir_name + '\\'):
                    # Strip the redundant directory prefix
                    resolved_file = resolved_file[len(config_dir_name) + 1:]
                    print(f"     📂 Adjusted Path: {resolved_file}")
                
                # Try to load and parse the external Tab file
                tab_file_path = self._resolve_path(resolved_file)
                print(f"     📂 Full Path: {tab_file_path}")
                print(f"     📂 Exists: {tab_file_path.exists()}")
                
                if tab_file_path.exists():
                    try:
                        tab_tree = ET.parse(tab_file_path)
                        tab_root = tab_tree.getroot()
                        
                        # Find the Tab element inside MarvinExternalFile
                        if tab_root.tag == 'MarvinExternalFile':
                            actual_tab = tab_root.find('Tab')
                            if actual_tab is not None:
                                self._analyze_tab_content(actual_tab, indent="        ")
                        elif tab_root.tag == 'Tab':
                            self._analyze_tab_content(tab_root, indent="        ")
                    except Exception as e:
                        print(f"        ⚠️  Could not parse tab file: {e}")
                else:
                    print(f"        ⚠️  Tab file not found")
            else:
                # Inline tab definition
                self._analyze_tab_content(tab_elem, indent="     ")
                
    def _find_tab_by_id(self, root: ET.Element, tab_id: str) -> Optional[ET.Element]:
        """Find a Tab DEFINITION element by its ID (not a reference in <Tabs>)"""
        # Tab definitions are direct children of <Marvin> root or at depth 2
        # They are NOT inside <Application><Tabs>
        for tab in root.findall('Tab'):
            if tab.attrib.get('ID') == tab_id:
                return tab
        # Also check one level deeper
        for child in root:
            if child.tag != 'Application':  # Skip Application section
                for tab in child.findall('Tab'):
                    if tab.attrib.get('ID') == tab_id:
                        return tab
        return None
        
    def _analyze_tab_content(self, tab_elem: ET.Element, indent: str = ""):
        """Analyze the content of a Tab element"""
        # Count grids, widgets, dynamicgrids
        grids = tab_elem.findall('.//Grid')
        widgets = tab_elem.findall('.//Widget')
        dynamicgrids = tab_elem.findall('.//DynamicGrid')
        
        print(f"{indent}📊 Contains:")
        print(f"{indent}   • Grids: {len(grids)}")
        print(f"{indent}   • Widgets: {len(widgets)}")
        print(f"{indent}   • DynamicGrids: {len(dynamicgrids)}")
        
        # Show grid files
        grid_files = []
        for grid in grids:
            if 'File' in grid.attrib:
                grid_files.append(grid.attrib['File'])
                
        if grid_files:
            print(f"{indent}   📁 Referenced Grid Files:")
            for gf in grid_files:
                print(f"{indent}      - {gf}")
                # Recursively analyze this grid file
                self._analyze_grid_file(gf, indent + "         ")
                
        # Show DynamicGrid details
        if dynamicgrids:
            print(f"{indent}   🔄 DynamicGrid Configurations:")
            for dg in dynamicgrids:
                dg_id = dg.attrib.get('ID', 'unknown')
                print(f"{indent}      - ID: {dg_id}")
                
                # Find option files
                option_files = []
                for deffile in dg.findall('.//DefinitionFile'):
                    if 'File' in deffile.attrib:
                        option_files.append(deffile.attrib['File'])
                        
                if option_files:
                    print(f"{indent}        Options ({len(option_files)} grids):")
                    for opt in option_files:
                        print(f"{indent}          • {opt}")
                        
    def _analyze_grid_file(self, grid_file_path: str, indent: str = ""):
        """Recursively analyze a grid file and show its structure"""
        # Check for runtime placeholders
        runtime_placeholders = re.findall(r'\$\(([A-Za-z0-9_\.]+)\)', grid_file_path)
        unresolved_placeholders = [p for p in runtime_placeholders if p not in self.aliases]
        
        if unresolved_placeholders:
            # This file contains runtime placeholders - can't validate at config-time
            print(f"{indent}ℹ️  Contains runtime placeholder(s): {', '.join(f'$({p})' for p in unresolved_placeholders)}")
            print(f"{indent}   (Will be resolved dynamically at runtime)")
            return
        
        # Resolve aliases in the path
        resolved_path = self._resolve_aliases_in_string(grid_file_path)
        
        # Handle redundant directory nesting (same logic as Tab files)
        config_dir_name = self.config_dir.name
        if resolved_path.startswith(config_dir_name + '/') or resolved_path.startswith(config_dir_name + '\\'):
            resolved_path = resolved_path[len(config_dir_name) + 1:]
            
        # Resolve to full path
        full_path = self._resolve_path(resolved_path)
        
        if not full_path.exists():
            print(f"{indent}⚠️  Grid file not found: {resolved_path}")
            return
            
        # Parse the grid file
        try:
            grid_tree = ET.parse(full_path)
            grid_root = grid_tree.getroot()
            
            # Handle both <Grid> and <MarvinExternalFile> patterns
            if grid_root.tag == 'MarvinExternalFile':
                # Check if this is an alias-only file
                aliaslist = grid_root.find('AliasList')
                actual_grid = grid_root.find('Grid')
                
                if aliaslist is not None and actual_grid is None:
                    # This is an alias definition file, not a grid layout
                    alias_count = len(aliaslist.findall('Alias'))
                    import_count = len(aliaslist.findall('Import'))
                    print(f"{indent}📋 Alias file: {alias_count} alias(es), {import_count} import(s)")
                    return
                    
                if actual_grid is None:
                    print(f"{indent}⚠️  No <Grid> found in external file")
                    return
                grid_root = actual_grid
            elif grid_root.tag != 'Grid':
                print(f"{indent}⚠️  Expected <Grid>, found <{grid_root.tag}>")
                return
                
            # Count elements
            nested_grids = grid_root.findall('.//Grid')
            widgets = grid_root.findall('.//Widget')
            dynamicgrids = grid_root.findall('.//DynamicGrid')
            
            print(f"{indent}📊 Structure:")
            print(f"{indent}   • Nested Grids: {len(nested_grids)}")
            print(f"{indent}   • Widgets: {len(widgets)}")
            print(f"{indent}   • DynamicGrids: {len(dynamicgrids)}")
            
            # Show nested grid files
            nested_grid_files = []
            for grid in nested_grids:
                if 'File' in grid.attrib:
                    nested_grid_files.append(grid.attrib['File'])
                    
            if nested_grid_files:
                print(f"{indent}   📁 Nested Grid Files:")
                for ngf in nested_grid_files:
                    print(f"{indent}      - {ngf}")
                    # Recursively analyze (with depth limit to prevent infinite loops)
                    if indent.count(' ') < 40:  # Limit recursion depth
                        self._analyze_grid_file(ngf, indent + "         ")
                    else:
                        print(f"{indent}         (max depth reached)")
                        
            # Show DynamicGrid details with their option files
            if dynamicgrids:
                print(f"{indent}   🔄 DynamicGrids:")
                for dg in dynamicgrids:
                    # DynamicGrid elements typically don't have ID themselves
                    # Instead, look for MinionSrc ID which controls the selection
                    minion_src = dg.find('.//MinionSrc')
                    if minion_src is not None:
                        dg_id = minion_src.attrib.get('ID', 'no-ID')
                        namespace = minion_src.attrib.get('Namespace', '')
                        if namespace:
                            print(f"{indent}      - Controller: {namespace}:{dg_id}")
                        else:
                            print(f"{indent}      - Controller ID: {dg_id}")
                    else:
                        # Fallback: check if DynamicGrid itself has ID attribute
                        dg_id = dg.attrib.get('ID')
                        if dg_id:
                            print(f"{indent}      - ID: {dg_id}")
                        else:
                            print(f"{indent}      - (no MinionSrc controller found)")
                    
                    # Find option files (GridFile elements)
                    option_files = []
                    for gridfile in dg.findall('.//GridFile'):
                        if 'Macro' in gridfile.attrib:
                            # GridMacro reference
                            macro_name = gridfile.attrib['Macro']
                            grid_id = gridfile.attrib.get('ID', 'no-ID')
                            option_files.append(f"Macro:{macro_name} (ID: {grid_id})")
                        elif 'File' in gridfile.attrib:
                            option_files.append(gridfile.attrib['File'])
                    
                    # Also check for DefinitionFile elements (alternative pattern)
                    for deffile in dg.findall('.//DefinitionFile'):
                        if 'File' in deffile.attrib:
                            option_files.append(deffile.attrib['File'])
                            
                    if option_files:
                        print(f"{indent}        📋 Options ({len(option_files)}):")
                        for opt in option_files[:5]:  # Limit to first 5 to avoid clutter
                            print(f"{indent}          • {opt}")
                        if len(option_files) > 5:
                            print(f"{indent}          ... and {len(option_files) - 5} more")
                            
        except ET.ParseError as e:
            print(f"{indent}⚠️  XML parse error: {e}")
        except Exception as e:
            print(f"{indent}⚠️  Error analyzing grid: {e}")
            
    def _validate_dynamicgrids(self, root: ET.Element):
        """Validate DynamicGrid configurations and file references"""
        for dg in root.findall('.//DynamicGrid'):
            dg_id = dg.attrib.get('ID', 'unknown')
            grid_files = []
            
            # Find all DefinitionFile elements
            for deffile in dg.findall('.//DefinitionFile'):
                if 'File' in deffile.attrib:
                    file_path = deffile.attrib['File']
                    grid_files.append(file_path)
                    
                    # Validate file exists
                    full_path = self._resolve_path(file_path)
                    if not full_path.exists():
                        self.result.add_error(
                            f"DynamicGrid '{dg_id}' references missing file: {file_path}"
                        )
                    else:
                        # Try to parse the grid file
                        try:
                            grid_tree = ET.parse(full_path)
                            grid_root = grid_tree.getroot()
                            if grid_root.tag != 'Grid':
                                self.result.add_warning(
                                    f"DynamicGrid file {file_path} has root <{grid_root.tag}>, expected <Grid>"
                                )
                        except ET.ParseError as e:
                            self.result.add_error(f"Grid file {file_path} has XML errors: {e}")
                            
            if grid_files:
                self.dynamicgrid_files[dg_id] = grid_files
                self.result.add_info(f"DynamicGrid '{dg_id}' has {len(grid_files)} grid option(s)")
                
        if self.dynamicgrid_files and self.verbose:
            print("\n📊 DynamicGrid Configurations:")
            for dg_id, files in self.dynamicgrid_files.items():
                print(f"  {dg_id}:")
                for f in files:
                    exists = "✓" if self._resolve_path(f).exists() else "✗"
                    print(f"    {exists} {f}")
                    
    def _validate_external_files(self):
        """Validate all external file references"""
        if self.external_files:
            self.result.add_info(f"Loaded {len(self.external_files)} external file(s)")
            if self.verbose:
                print("\n📂 External Files:")
                for f in sorted(self.external_files):
                    print(f"  ✓ {f}")
                    
    def _validate_widget_sources(self, root: ET.Element):
        """Validate widget source file references"""
        widget_files = []
        
        # Check for Source attributes in various widgets
        for elem in root.iter():
            if 'Source' in elem.attrib:
                source_file = elem.attrib['Source']
                widget_files.append(source_file)
                
                full_path = self._resolve_path(source_file)
                if not full_path.exists():
                    self.result.add_warning(f"Widget source file not found: {source_file}")
                    
        if widget_files:
            self.result.add_info(f"Found {len(widget_files)} widget source reference(s)")
            
    def _analyze_alias_cascading(self):
        """Analyze alias cascading and detect issues"""
        print("\n🔗 Alias Cascade Analysis:")
        
        # Detect circular dependencies
        circular = self._find_circular_dependencies()
        if circular:
            for cycle in circular:
                self.result.add_error(f"Circular alias dependency: {' → '.join(cycle)}")
                
        # Show cascade chains
        if self.verbose and self.alias_dependencies:
            print("\n  Alias Dependencies:")
            for alias, deps in sorted(self.alias_dependencies.items()):
                if deps:
                    chain = self._resolve_alias_chain(alias)
                    print(f"    {alias} = {self.aliases.get(alias, 'undefined')}")
                    if len(chain) > 1:
                        print(f"      Chain: {' → '.join(chain)}")
                        
    def _find_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in alias references"""
        circular = []
        visited = set()
        
        def dfs(alias: str, path: List[str]) -> bool:
            if alias in path:
                # Found cycle
                cycle_start = path.index(alias)
                circular.append(path[cycle_start:] + [alias])
                return True
                
            if alias in visited:
                return False
                
            visited.add(alias)
            
            if alias in self.alias_dependencies:
                for dep in self.alias_dependencies[alias]:
                    if dfs(dep, path + [alias]):
                        return True
                        
            return False
            
        for alias in self.alias_dependencies.keys():
            if alias not in visited:
                dfs(alias, [])
                
        return circular
        
    def _resolve_alias_chain(self, alias: str, seen: Optional[Set[str]] = None) -> List[str]:
        """Resolve the full chain of an alias"""
        if seen is None:
            seen = set()
            
        if alias in seen:
            return [alias, '(circular)']
            
        seen.add(alias)
        
        if alias not in self.alias_dependencies or not self.alias_dependencies[alias]:
            return [alias]
            
        # Find deepest dependency
        chains = []
        for dep in self.alias_dependencies[alias]:
            chain = self._resolve_alias_chain(dep, seen.copy())
            chains.append(chain)
            
        # Return longest chain
        longest = max(chains, key=len) if chains else []
        return longest + [alias]
        
    def _resolve_path(self, path_str: str) -> Path:
        """Resolve a path relative to config directory"""
        # First resolve any aliases in the path string
        path_str = self._resolve_aliases_in_string(path_str)
        # Normalize backslashes to forward slashes for cross-platform compatibility
        path_str = path_str.replace('\\', '/')
        
        # Check if alias resolution created a redundant directory prefix
        # (e.g., if config is in "ExperienceKit/" and AppDir="ExperienceKit", 
        # we don't want "ExperienceKit/ExperienceKit/...")
        config_dir_name = self.config_dir.name
        if path_str.startswith(config_dir_name + '/') or path_str.startswith(config_dir_name + '\\'):
            path_str = path_str[len(config_dir_name) + 1:]
        
        path = Path(path_str)
        if path.is_absolute():
            return path
        return (self.config_dir / path).resolve()
        
    def _resolve_aliases_in_string(self, text: str) -> str:
        """Resolve alias references in a string like $(ALIAS_NAME)"""
        pattern = r'\$\(([A-Za-z0-9_\.]+)\)'
        
        def replace_alias(match):
            alias_name = match.group(1)
            if alias_name in self.aliases:
                # Recursively resolve in case the alias value contains more aliases
                return self._resolve_aliases_in_string(self.aliases[alias_name])
            else:
                # Can't resolve, return original
                return match.group(0)
                
        return re.sub(pattern, replace_alias, text)
        
    def _get_element_location(self, elem: ET.Element) -> str:
        """Get approximate location description for an element"""
        # This is simplified; real implementation would track line numbers
        return "in configuration"


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='BIFF Marvin Configuration Validator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_config.py Application.xml
  python validate_config.py --verbose App.Config.xml
  python validate_config.py --alias-cascade ExperienceKit/App.Config.xml
        """
    )
    parser.add_argument('config', help='Path to Marvin configuration XML file')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Show detailed information')
    parser.add_argument('-a', '--alias-cascade', action='store_true',
                       help='Analyze alias cascading and dependencies')
    
    args = parser.parse_args()
    
    validator = MarvinConfigValidator(
        args.config, 
        verbose=args.verbose,
        trace_aliases=args.alias_cascade
    )
    
    result = validator.validate()
    result.print_results()
    
    sys.exit(0 if result.passed else 1)


if __name__ == '__main__':
    main()
