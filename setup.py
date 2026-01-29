"""
Setup configuration for biff-agents package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="biff-agents",
    version="0.1.0",
    description="AI-powered configuration tools for BIFF Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="BIFF Development Team",
    url="https://github.com/thehevy/biff-agents",
    project_urls={
        "Bug Reports": "https://github.com/thehevy/biff-agents/issues",
        "Source": "https://github.com/thehevy/biff-agents",
        "Original BIFF": "https://github.com/intel/Board-Instrumentation-Framework",
    },
    python_requires=">=3.9",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        # Core library uses only stdlib - no runtime dependencies
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "biff=biff_cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
