"""
Test configuration for pytest
"""

import sys
from pathlib import Path

# Add package to path
package_dir = Path(__file__).parent.parent
sys.path.insert(0, str(package_dir))
