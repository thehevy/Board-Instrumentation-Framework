#!/bin/bash
# Start BIFF Minion with intelligent instance management
# Only stops instances using the SAME configuration file

# Default configuration
CONFIG_FILE="MinionConfig.xml"
VERBOSE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [-i CONFIG_FILE] [-v]"
            echo ""
            echo "Options:"
            echo "  -i, --config FILE   Configuration file (default: MinionConfig.xml)"
            echo "  -v, --verbose       Enable verbose logging"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
        *)
            CONFIG_FILE="$1"
            shift
            ;;
    esac
done

# Convert to absolute path for comparison
if [[ "$CONFIG_FILE" = /* ]]; then
    ABS_CONFIG="$CONFIG_FILE"
else
    ABS_CONFIG="$(cd "$(dirname "$CONFIG_FILE")" 2>/dev/null && pwd)/$(basename "$CONFIG_FILE")"
fi

echo "============================================================"
echo "  BIFF Minion Startup"
echo "============================================================"
echo "Configuration: $CONFIG_FILE"
echo ""

# Check if configuration file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# Check for existing Minion instances with same config
echo "Checking for existing Minion instances with this configuration..."

# Find Python processes running Minion.py
PIDS=$(ps aux | grep -E "python.*Minion\.py.*-i.*$CONFIG_FILE|python.*Minion\.py.*$CONFIG_FILE" | grep -v grep | awk '{print $2}')

if [ -n "$PIDS" ]; then
    echo "Found existing Minion instance(s) with config: $CONFIG_FILE"
    echo "PIDs: $PIDS"
    echo ""
    read -p "Stop existing instance(s) and start new one? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for PID in $PIDS; do
            echo "Stopping Minion (PID: $PID)..."
            kill $PID 2>/dev/null
            
            # Wait for process to stop
            for i in {1..10}; do
                if ! ps -p $PID > /dev/null 2>&1; then
                    break
                fi
                sleep 0.5
            done
            
            # Force kill if still running
            if ps -p $PID > /dev/null 2>&1; then
                echo "Force stopping Minion (PID: $PID)..."
                kill -9 $PID 2>/dev/null
            fi
        done
        echo "Existing instance(s) stopped."
    else
        echo "Startup cancelled."
        exit 0
    fi
fi

# Start Minion
echo ""
echo "Starting Minion..."
echo "Command: python Minion.py -i $CONFIG_FILE $VERBOSE"
echo ""
echo "============================================================"

# Check if Python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found in PATH"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

# Start Minion
exec $PYTHON_CMD Minion.py -i "$CONFIG_FILE" $VERBOSE
