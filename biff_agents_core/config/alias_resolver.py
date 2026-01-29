"""
Alias Resolution for BIFF Configurations

Resolves $(ALIAS_NAME) references in XML configurations.
"""

import re
from typing import Dict


class AliasResolver:
    """Resolve alias references in BIFF configurations"""
    
    def __init__(self, aliases: Dict[str, str]):
        """
        Initialize resolver with alias definitions
        
        Args:
            aliases: Dictionary mapping alias names to values
        """
        self.aliases = aliases
    
    def resolve(self, text: str, max_iterations: int = 10) -> str:
        """
        Resolve all alias references in text
        
        Args:
            text: Text containing $(ALIAS) references
            max_iterations: Maximum resolution passes (for nested aliases)
            
        Returns:
            Text with all aliases resolved
            
        Raises:
            ValueError: If circular reference detected
        """
        if not text:
            return text
        
        original = text
        
        for iteration in range(max_iterations):
            # Find all $(ALIAS_NAME) patterns
            pattern = r'\$\(([^)]+)\)'
            matches = re.findall(pattern, text)
            
            if not matches:
                # No more aliases to resolve
                return text
            
            # Replace each alias
            for alias_name in matches:
                if alias_name in self.aliases:
                    replacement = self.aliases[alias_name]
                    text = text.replace(f'$({alias_name})', replacement)
            
            # Check if we made progress
            if text == original:
                # No changes made, might be unresolved aliases
                unresolved = re.findall(pattern, text)
                if unresolved:
                    raise ValueError(
                        f"Unresolved aliases: {', '.join(set(unresolved))}"
                    )
                return text
            
            original = text
        
        # If we hit max iterations, might be circular reference
        remaining = re.findall(r'\$\(([^)]+)\)', text)
        if remaining:
            raise ValueError(
                f"Possible circular reference in aliases: {', '.join(set(remaining))}"
            )
        
        return text
    
    def add_alias(self, name: str, value: str):
        """
        Add or update an alias
        
        Args:
            name: Alias name
            value: Alias value
        """
        self.aliases[name] = value
    
    def get_unresolved_aliases(self, text: str) -> list:
        """
        Get list of aliases referenced but not defined
        
        Args:
            text: Text to check
            
        Returns:
            List of undefined alias names
        """
        pattern = r'\$\(([^)]+)\)'
        referenced = set(re.findall(pattern, text))
        defined = set(self.aliases.keys())
        
        return list(referenced - defined)
