"""
Configuration Validator for BIFF

Validates Minion, Oscar, and Marvin configurations for common errors.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Union
from dataclasses import dataclass
import os
import shutil

from ..config.xml_parser import BIFFXMLParser
from ..config.env_var_resolver import EnvVarResolver


@dataclass
class ValidationError:
    """Represents a validation error"""
    severity: str  # 'error', 'warning', 'info'
    component: str  # Component where error occurred
    message: str  # Error description
    fix_suggestion: Optional[str] = None  # How to fix


@dataclass
class ValidationResult:
    """Result of configuration validation"""
    valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info: List[ValidationError]
    
    def __str__(self) -> str:
        """String representation of validation result"""
        lines = []
        
        if self.errors:
            lines.append(f"\n❌ {len(self.errors)} Error(s):")
            for err in self.errors:
                lines.append(f"  • {err.message}")
                if err.fix_suggestion:
                    lines.append(f"    Fix: {err.fix_suggestion}")
        
        if self.warnings:
            lines.append(f"\n⚠️  {len(self.warnings)} Warning(s):")
            for warn in self.warnings:
                lines.append(f"  • {warn.message}")
        
        if self.info:
            lines.append(f"\nℹ️  {len(self.info)} Info:")
            for info_item in self.info:
                lines.append(f"  • {info_item.message}")
        
        if self.valid and not self.warnings:
            lines.append("\n✓ Configuration is valid")
        
        return '\n'.join(lines)


class ConfigValidator:
    """Validate BIFF configurations"""
    
    def __init__(self):
        """Initialize validator"""
        self.parser = BIFFXMLParser()
        self.env_resolver = EnvVarResolver()
    
    def validate_minion_config(self, path: Union[str, Path]) -> ValidationResult:
        """
        Validate Minion configuration
        
        Args:
            path: Path to MinionConfig.xml
            
        Returns:
            ValidationResult with any errors/warnings
        """
        errors = []
        warnings = []
        info = []
        
        try:
            root = self.parser.parse_config(path)
        except Exception as e:
            errors.append(ValidationError(
                severity='error',
                component='XML',
                message=f"Failed to parse XML: {e}",
                fix_suggestion="Check XML syntax, ensure all tags are closed"
            ))
            return ValidationResult(valid=False, errors=errors, warnings=warnings, info=info)
        
        # Check component type
        if root.tag != 'Minion':
            errors.append(ValidationError(
                severity='error',
                component='Root',
                message=f"Expected <Minion> root element, got <{root.tag}>",
                fix_suggestion="Ensure root element is <Minion>"
            ))
        
        # Extract and validate aliases
        aliases = self.parser.extract_aliases(root)
        if aliases:
            info.append(ValidationError(
                severity='info',
                component='Aliases',
                message=f"Found {len(aliases)} alias definition(s)"
            ))
        
        # Check environment variables
        xml_string = ET.tostring(root, encoding='unicode')
        missing_vars = self.env_resolver.get_missing_env_vars(xml_string)
        
        if missing_vars:
            warnings.append(ValidationError(
                severity='warning',
                component='Environment',
                message=f"Environment variables not set: {', '.join(missing_vars)}",
                fix_suggestion=f"Export these variables: {', '.join([f'export {v}=VALUE' for v in missing_vars])}"
            ))
        
        # Validate namespaces
        namespaces = self.parser.extract_namespaces(root)
        if not namespaces:
            errors.append(ValidationError(
                severity='error',
                component='Namespace',
                message="No namespaces defined",
                fix_suggestion="Add at least one <Namespace> section"
            ))
        
        for ns in namespaces:
            if not ns['name']:
                errors.append(ValidationError(
                    severity='error',
                    component='Namespace',
                    message="Namespace missing <Name>",
                    fix_suggestion="Add <Name>YourNamespace</Name> to Namespace"
                ))
            
            if not ns['target_ip']:
                warnings.append(ValidationError(
                    severity='warning',
                    component='Namespace',
                    message=f"Namespace '{ns['name']}' has no TargetConnection",
                    fix_suggestion="Add <TargetConnection IP=\"...\" PORT=\"...\"/>"
                ))
        
        # Validate collectors
        collectors = self.parser.extract_collectors(root)
        if collectors:
            info.append(ValidationError(
                severity='info',
                component='Collectors',
                message=f"Found {len(collectors)} collector(s)"
            ))
            
            for collector in collectors:
                if not collector['id']:
                    errors.append(ValidationError(
                        severity='error',
                        component='Collector',
                        message="Collector missing ID attribute",
                        fix_suggestion='Add ID="collector.name" to <Collector>'
                    ))
                
                # Check if collector has a data source (executable, plugin, operator, or value)
                has_source = (
                    collector['executable'] or 
                    collector['plugin'] or 
                    collector['operator'] or 
                    collector['value']
                )
                
                if not has_source:
                    errors.append(ValidationError(
                        severity='error',
                        component='Collector',
                        message=f"Collector '{collector['id']}' has no data source",
                        fix_suggestion="Add <Executable>, <Plugin>, <Operator>, or <Value>"
                    ))
        
        # Validate actors
        actors = self.parser.extract_actors(root)
        if actors:
            info.append(ValidationError(
                severity='info',
                component='Actors',
                message=f"Found {len(actors)} actor(s)"
            ))
            
            for actor in actors:
                if not actor['id']:
                    errors.append(ValidationError(
                        severity='error',
                        component='Actor',
                        message="Actor missing ID attribute",
                        fix_suggestion='Add ID="actor_name" to <Actor>'
                    ))
                
                if actor['executable']:
                    # Check if executable exists and is executable
                    exec_path = Path(actor['executable'])
                    
                    if exec_path.exists():
                        if not os.access(exec_path, os.X_OK) and exec_path.suffix in ['.sh', '.py']:
                            warnings.append(ValidationError(
                                severity='warning',
                                component='Actor',
                                message=f"Actor '{actor['id']}' script not executable: {exec_path}",
                                fix_suggestion=f"chmod +x {exec_path}"
                            ))
                    else:
                        # Check if it's a command in PATH
                        cmd = actor['executable'].split()[0]
                        if not shutil.which(cmd):
                            warnings.append(ValidationError(
                                severity='warning',
                                component='Actor',
                                message=f"Actor '{actor['id']}' executable not found: {cmd}",
                                fix_suggestion=f"Ensure {cmd} is installed or provide full path"
                            ))
        
        # Validate modifiers
        modifiers = self.parser.extract_modifiers(root)
        if modifiers:
            regex_modifiers = [m for m in modifiers if m['is_regex']]
            if regex_modifiers:
                info.append(ValidationError(
                    severity='info',
                    component='Modifiers',
                    message=f"Found {len(regex_modifiers)} regex modifier(s)"
                ))
        
        valid = len(errors) == 0
        return ValidationResult(valid=valid, errors=errors, warnings=warnings, info=info)
    
    def validate_oscar_config(self, path: Union[str, Path]) -> ValidationResult:
        """
        Validate Oscar configuration
        
        Args:
            path: Path to OscarConfig.xml
            
        Returns:
            ValidationResult with any errors/warnings
        """
        errors = []
        warnings = []
        info = []
        
        try:
            root = self.parser.parse_config(path)
        except Exception as e:
            errors.append(ValidationError(
                severity='error',
                component='XML',
                message=f"Failed to parse XML: {e}",
                fix_suggestion="Check XML syntax"
            ))
            return ValidationResult(valid=False, errors=errors, warnings=warnings, info=info)
        
        # Check component type
        if root.tag != 'Oscar':
            errors.append(ValidationError(
                severity='error',
                component='Root',
                message=f"Expected <Oscar> root element, got <{root.tag}>",
                fix_suggestion="Ensure root element is <Oscar>"
            ))
        
        # Extract connections
        connections = self.parser.extract_oscar_connections(root)
        
        if not connections['incoming_port']:
            errors.append(ValidationError(
                severity='error',
                component='Connection',
                message="No IncomingMinionConnection defined",
                fix_suggestion='Add <IncomingMinionConnection PORT="10020"/>'
            ))
        
        if connections['autoconnect_key']:
            info.append(ValidationError(
                severity='info',
                component='Connection',
                message=f"MarvinAutoConnect enabled with key: {connections['autoconnect_key']}"
            ))
        else:
            # Standard push mode, need targets
            if not connections['targets']:
                warnings.append(ValidationError(
                    severity='warning',
                    component='Connection',
                    message="No TargetConnection defined (Oscar won't forward data)",
                    fix_suggestion='Add <TargetConnection IP="..." PORT="..."/> or use MarvinAutoConnect'
                ))
        
        valid = len(errors) == 0
        return ValidationResult(valid=valid, errors=errors, warnings=warnings, info=info)
    
    def validate_marvin_config(self, path: Union[str, Path]) -> ValidationResult:
        """
        Validate Marvin configuration
        
        Args:
            path: Path to Marvin config XML
            
        Returns:
            ValidationResult with any errors/warnings
        """
        errors = []
        warnings = []
        info = []
        
        try:
            root = self.parser.parse_config(path)
        except Exception as e:
            errors.append(ValidationError(
                severity='error',
                component='XML',
                message=f"Failed to parse XML: {e}",
                fix_suggestion="Check XML syntax"
            ))
            return ValidationResult(valid=False, errors=errors, warnings=warnings, info=info)
        
        # Check component type
        if root.tag != 'Marvin':
            errors.append(ValidationError(
                severity='error',
                component='Root',
                message=f"Expected <Marvin> root element, got <{root.tag}>",
                fix_suggestion="Ensure root element is <Marvin>"
            ))
        
        # Extract network config
        network = self.parser.extract_marvin_network(root)
        
        if not network['port']:
            warnings.append(ValidationError(
                severity='warning',
                component='Network',
                message="No Network Port defined",
                fix_suggestion='Add <Network Port="5301">...</Network>'
            ))
        
        if network['oscars']:
            info.append(ValidationError(
                severity='info',
                component='Network',
                message=f"Connected to {len(network['oscars'])} Oscar instance(s)"
            ))
            
            # Check for authentication keys
            oscars_with_keys = [o for o in network['oscars'] if o['key']]
            if oscars_with_keys:
                info.append(ValidationError(
                    severity='info',
                    component='Network',
                    message=f"{len(oscars_with_keys)} Oscar(s) use authentication"
                ))
        
        valid = len(errors) == 0
        return ValidationResult(valid=valid, errors=errors, warnings=warnings, info=info)
