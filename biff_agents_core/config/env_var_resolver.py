"""
Environment Variable Resolution for BIFF Configurations

Resolves $(ENV_VAR) references from system environment.
"""

import os
import re
from typing import Dict, List, Optional


class EnvVarResolver:
    """Resolve environment variable references"""
    
    def resolve(self, text: str, env: Optional[Dict[str, str]] = None) -> str:
        """
        Resolve environment variable references in text
        
        Args:
            text: Text containing $(VAR) references
            env: Optional environment dict (uses os.environ if None)
            
        Returns:
            Text with environment variables resolved
            
        Raises:
            KeyError: If required environment variable not set
        """
        if env is None:
            env = dict(os.environ)
        
        # Find all $(VAR_NAME) patterns
        pattern = r'\$\(([A-Z_][A-Z0-9_]*)\)'
        
        def replacer(match):
            var_name = match.group(1)
            if var_name in env:
                return env[var_name]
            else:
                raise KeyError(
                    f"Environment variable not set: {var_name}"
                )
        
        return re.sub(pattern, replacer, text)
    
    def extract_env_vars(self, text: str) -> List[str]:
        """
        Extract all environment variable references
        
        Args:
            text: Text to analyze
            
        Returns:
            List of environment variable names
        """
        pattern = r'\$\(([A-Z_][A-Z0-9_]*)\)'
        return list(set(re.findall(pattern, text)))
    
    def check_env_vars(self, text: str, env: Optional[Dict[str, str]] = None) -> Dict[str, bool]:
        """
        Check which environment variables are set
        
        Args:
            text: Text containing $(VAR) references
            env: Optional environment dict (uses os.environ if None)
            
        Returns:
            Dictionary mapping variable names to whether they're set
        """
        if env is None:
            env = dict(os.environ)
        
        var_names = self.extract_env_vars(text)
        
        return {
            var_name: var_name in env
            for var_name in var_names
        }
    
    def get_missing_env_vars(self, text: str, env: Optional[Dict[str, str]] = None) -> List[str]:
        """
        Get list of environment variables that are referenced but not set
        
        Args:
            text: Text to check
            env: Optional environment dict (uses os.environ if None)
            
        Returns:
            List of missing variable names
        """
        status = self.check_env_vars(text, env)
        return [name for name, is_set in status.items() if not is_set]
