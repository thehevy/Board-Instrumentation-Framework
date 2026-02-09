#!/bin/bash
# BIFF Marvin Configuration Validator - Unix/Linux Launcher
# Pre-flight validation for Marvin XML configurations

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.7 or later."
    exit 1
fi

# Check if config file argument provided
if [ $# -eq 0 ]; then
    echo "Usage: validate_config.sh <config.xml> [options]"
    echo ""
    echo "Options:"
    echo "  -v, --verbose         Show detailed information"
    echo "  -a, --alias-cascade   Analyze alias cascading"
    echo ""
    echo "Examples:"
    echo "  ./validate_config.sh Application.xml"
    echo "  ./validate_config.sh -v App.Config.xml"
    echo "  ./validate_config.sh -a --verbose ExperienceKit/App.Config.xml"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run validator
python3 "$SCRIPT_DIR/validate_config.py" "$@"
exit $?
