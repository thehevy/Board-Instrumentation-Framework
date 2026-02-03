#!/bin/bash
###############################################################################
# Quickstart - Start Minion with Generated Configuration
# Runs Minion instance using quickstart test configuration
###############################################################################

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BIFF_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
MINION_CONFIG="$SCRIPT_DIR/biff-quickstart-test/MinionConfig.xml"
MINION_SCRIPT="$BIFF_ROOT/Minion/Minion.py"
MINION_DIR="$BIFF_ROOT/Minion"

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
if [ ! -f "$MINION_CONFIG" ]; then
    echo "[ERROR] Minion config not found: $MINION_CONFIG"
    echo "Run: python biff_cli/biff_cli.py configure quickstart"
    exit 1
fi

# Check if Minion.py exists
if [ ! -f "$MINION_SCRIPT" ]; then
    echo "[ERROR] Minion.py not found: $MINION_SCRIPT"
    exit 1
fi

echo "============================================================"
echo "  Starting Quickstart Minion"
echo "============================================================"
echo ""
echo "Config: $MINION_CONFIG"
echo "Python: $PYTHON_CMD"
echo "Working Directory: $MINION_DIR"
echo ""

# Change to Minion directory and launch
cd "$MINION_DIR"
exec "$PYTHON_CMD" "$MINION_SCRIPT" -c "$MINION_CONFIG" -vvvv
