#!/bin/bash
###############################################################################
# Quickstart - Start Oscar with Generated Configuration
# Runs Oscar broker using quickstart test configuration
###############################################################################

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BIFF_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
OSCAR_CONFIG="$SCRIPT_DIR/biff-quickstart-test/OscarConfig.xml"
OSCAR_SCRIPT="$BIFF_ROOT/Oscar/Oscar.py"
OSCAR_DIR="$BIFF_ROOT/Oscar"

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python not found. Please install Python 3.7+"
    exit 1
fi

# Check if config exists
if [ ! -f "$OSCAR_CONFIG" ]; then
    echo "[ERROR] Oscar config not found: $OSCAR_CONFIG"
    echo "Run: python biff_cli/biff_cli.py configure quickstart"
    exit 1
fi

# Check if Oscar.py exists
if [ ! -f "$OSCAR_SCRIPT" ]; then
    echo "[ERROR] Oscar.py not found: $OSCAR_SCRIPT"
    exit 1
fi

echo "============================================================"
echo "  Starting Quickstart Oscar"
echo "============================================================"
echo ""
echo "Config: $OSCAR_CONFIG"
echo "Python: $PYTHON_CMD"
echo "Working Directory: $OSCAR_DIR"
echo ""

# Change to Oscar directory and launch
cd "$OSCAR_DIR"
exec "$PYTHON_CMD" "$OSCAR_SCRIPT" -i "$OSCAR_CONFIG" -vvvv
