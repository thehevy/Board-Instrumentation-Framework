"""
BIFF Agents Core Library

Shared utilities for all BIFF AI agents.
"""

__version__ = "0.1.0"
__author__ = "BIFF Development Team"

from .config.xml_parser import BIFFXMLParser
from .validators.config_validator import ConfigValidator
from .generators.base_generator import BaseGenerator

__all__ = [
    "BIFFXMLParser",
    "ConfigValidator", 
    "BaseGenerator",
]
