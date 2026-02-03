#!/bin/bash
# ==============================================================================
# BIFF Oscar - Background Startup Script for Linux/Unix
# ==============================================================================
# Purpose: Start Oscar data broker in background with automatic Python detection
# Usage:   ./start_oscar.sh [-i CONFIG] [-v] [-n] [-h]
# ==============================================================================

# Default values
CONFIG_FILE="OscarConfig.xml"
VERBOSE=""
NO_GUI=""

# Display help
show_help() {
    cat << EOF
============================================================
  BIFF Oscar - Background Startup Script
============================================================

USAGE:
  ./start_oscar.sh [OPTIONS]

OPTIONS:
  -i, --config <path>   Configuration file (default: OscarConfig.xml)
  -v, --verbose         Enable verbose logging
  -n, --no-gui          Disable Oscar GUI
  -h, --help            Show this help message

EXAMPLES:
  ./start_oscar.sh
      Start with default configuration

  ./start_oscar.sh -i ../biff-agents/quickstart_configs/OscarConfig.xml
      Start with custom configuration

  ./start_oscar.sh -v
      Start with verbose logging enabled

  ./start_oscar.sh -n
      Start without GUI

MANAGEMENT:
  Status:   ./status_oscar.sh
  Stop:     ./stop_oscar.sh
  Logs:     tail -f OscarLog.txt

EOF
    exit 0
}

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
        -n|--no-gui)
            NO_GUI="--nogui"
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Banner
echo ""
echo "============================================================"
echo "  BIFF Oscar - Starting Data Broker"
echo "============================================================"
echo ""

# Check for Python
echo "[INFO] Searching for Python..."

PYTHON_CMD=""
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        PYTHON_CMD=$cmd
        VERSION=$($cmd --version 2>&1)
        echo "[SUCCESS] Found: $cmd ($VERSION)"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "[ERROR] Python not found in PATH"
    echo "        Install Python 3.7+ and try again"
    exit 1
fi

# Verify Oscar.py exists
if [ ! -f "Oscar.py" ]; then
    echo "[ERROR] Oscar.py not found in current directory"
    echo "        Script directory: $SCRIPT_DIR"
    exit 1
fi

# Check if Oscar is already running with this config
CONFIG_PATH="$CONFIG_FILE"
if [[ "$CONFIG_FILE" != /* ]]; then
    CONFIG_PATH="$SCRIPT_DIR/$CONFIG_FILE"
fi

PID_FILE="$SCRIPT_DIR/.oscar.pid"
LOG_FILE="$SCRIPT_DIR/OscarLog.txt"

# Check for existing instance
EXISTING_PIDS=$(ps aux | grep -E "$PYTHON_CMD.*Oscar\.py" | grep -v grep | awk '{print $2}')

if [ -n "$EXISTING_PIDS" ]; then
    echo "[WARNING] Oscar process(es) already running:"
    ps aux | grep -E "$PYTHON_CMD.*Oscar\.py" | grep -v grep
    echo ""
    read -p "Stop existing instance(s) and start new one? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "[INFO] Stopping existing Oscar instance(s)..."
        for PID in $EXISTING_PIDS; do
            kill $PID 2>/dev/null
            # Wait up to 5 seconds for graceful shutdown
            for i in {1..10}; do
                if ! ps -p $PID > /dev/null 2>&1; then
                    break
                fi
                sleep 0.5
            done
            # Force kill if still running
            if ps -p $PID > /dev/null 2>&1; then
                kill -9 $PID 2>/dev/null
            fi
        done
        echo "[SUCCESS] Existing instance(s) stopped"
        sleep 1
    else
        echo "[INFO] Keeping existing instance, exiting"
        exit 0
    fi
fi

# Build command
CMD_ARGS="-i $CONFIG_FILE"
if [ -n "$VERBOSE" ]; then
    CMD_ARGS="$CMD_ARGS $VERBOSE"
fi
if [ -n "$NO_GUI" ]; then
    CMD_ARGS="$CMD_ARGS $NO_GUI"
fi

# Start Oscar in background
echo ""
echo "[INFO] Starting Oscar in background..."
echo "       Config: $CONFIG_FILE"
echo "       Log:    $LOG_FILE"
echo ""

nohup $PYTHON_CMD Oscar.py $CMD_ARGS > "$LOG_FILE" 2>&1 &
OSCAR_PID=$!

# Save PID
echo $OSCAR_PID > "$PID_FILE"

# Wait briefly and check if process started
sleep 1
if ps -p $OSCAR_PID > /dev/null 2>&1; then
    echo "============================================================"
    echo "  Oscar Started Successfully!"
    echo "============================================================"
    echo ""
    echo "  PID:    $OSCAR_PID"
    echo "  Config: $CONFIG_FILE"
    echo "  Log:    $LOG_FILE"
    echo ""
    echo "MANAGEMENT:"
    echo "  Status: ./status_oscar.sh"
    echo "  Stop:   ./stop_oscar.sh"
    echo "  Logs:   tail -f $LOG_FILE"
    echo ""
else
    echo "[ERROR] Oscar failed to start"
    echo "        Check log file: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi
