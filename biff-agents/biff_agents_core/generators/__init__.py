"""Template generators for BIFF configurations."""

from .base_generator import BaseGenerator
from .minion_generator import MinionConfigGenerator
from .oscar_generator import OscarConfigGenerator
from .marvin_generator import MarvinApplicationGenerator

__all__ = ["BaseGenerator", "MinionConfigGenerator", "OscarConfigGenerator", "MarvinApplicationGenerator"]
