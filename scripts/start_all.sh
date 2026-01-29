#!/bin/bash
###############################################################################
# BIFF Quick Start Launcher - Linux/Mac
# Launches Oscar, Minion, and Marvin in sequence
###############################################################################

set -e  # Exit on error

echo ""
echo "============================================================"
echo "  BIFF Quick Start Launcher"
echo "============================================================"
echo ""

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python not found. Please install Python 3.7+"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BIFF_AGENTS_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if config directory exists
CONFIG_DIR="$BIFF_AGENTS_ROOT/quickstart_configs"
if [ ! -d "$CONFIG_DIR" ]; then
    echo "[ERROR] Config directory not found: $CONFIG_DIR"
    echo ""
    echo "Please run '$PYTHON_CMD -m biff_cli quickstart' first to generate configs."
    echo ""
    exit 1
fi

# Configuration paths
MINION_CONFIG="$CONFIG_DIR/MinionConfig.xml"
OSCAR_CONFIG="$CONFIG_DIR/OscarConfig.xml"
MARVIN_CONFIG="$CONFIG_DIR/Application.xml"

# Check if configs exist
if [ ! -f "$MINION_CONFIG" ]; then
    echo "[ERROR] Minion config not found: $MINION_CONFIG"
    exit 1
fi

if [ ! -f "$OSCAR_CONFIG" ]; then
    echo "[ERROR] Oscar config not found: $OSCAR_CONFIG"
    exit 1
fi

if [ ! -f "$MARVIN_CONFIG" ]; then
    echo "[ERROR] Marvin config not found: $MARVIN_CONFIG"
    exit 1
fi

# Detect BIFF installation
BIFF_ROOT=""
if [ -f "$BIFF_AGENTS_ROOT/../../Oscar/Oscar.py" ]; then
    BIFF_ROOT="$(cd "$BIFF_AGENTS_ROOT/../.." && pwd)"
    echo "[INFO] Using existing BIFF installation at: $BIFF_ROOT"
elif [ -f "$BIFF_AGENTS_ROOT/../Oscar/Oscar.py" ]; then
    BIFF_ROOT="$(cd "$BIFF_AGENTS_ROOT/.." && pwd)"
    echo "[INFO] Using existing BIFF installation at: $BIFF_ROOT"
else
    echo "[WARNING] BIFF installation not detected"
    echo "[INFO] Assuming standalone mode"
    echo ""
    echo "[ERROR] Standalone mode requires Oscar/Minion/Marvin directories"
    echo "Please run 'biff quickstart' with existing BIFF installation"
    exit 1
fi

echo ""
echo "[INFO] Starting BIFF components..."
echo ""

# Create log directory
LOG_DIR="$BIFF_AGENTS_ROOT/logs"
mkdir -p "$LOG_DIR"

# Start Oscar (data broker)
echo "[1/3] Starting Oscar (data broker)..."
cd "$BIFF_ROOT/Oscar"
nohup $PYTHON_CMD Oscar.py -c "$OSCAR_CONFIG" > "$LOG_DIR/oscar.log" 2>&1 &
OSCAR_PID=$!
echo "      [OK] Oscar started (PID: $OSCAR_PID, log: $LOG_DIR/oscar.log)"
sleep 3

# Start Minion (data collector)
echo "[2/3] Starting Minion (data collector)..."
cd "$BIFF_ROOT/Minion"
nohup $PYTHON_CMD Minion.py -c "$MINION_CONFIG" > "$LOG_DIR/minion.log" 2>&1 &
MINION_PID=$!
echo "      [OK] Minion started (PID: $MINION_PID, log: $LOG_DIR/minion.log)"
sleep 2

# Build Marvin if needed
echo "[3/3] Starting Marvin (GUI)..."
cd "$BIFF_ROOT/Marvin"

if [ ! -f "build/libs/BIFF.Marvin.jar" ]; then
    echo "      [INFO] Building Marvin (first-time setup)..."
    ./gradlew build -q
    if [ $? -ne 0 ]; then
        echo "      [ERROR] Marvin build failed"
        echo ""
        echo "Check that Java and Gradle are installed:"
        echo "  java -version"
        echo "  gradle --version"
        echo ""
        exit 1
    fi
    echo "      [OK] Marvin built successfully"
fi

# Start Marvin
echo "      [INFO] Launching Marvin GUI..."
nohup java -jar build/libs/BIFF.Marvin.jar -a "$MARVIN_CONFIG" > "$LOG_DIR/marvin.log" 2>&1 &
MARVIN_PID=$!

cd "$BIFF_AGENTS_ROOT"

sleep 2

echo ""
echo "============================================================"
echo "  All BIFF components started!"
echo "============================================================"
echo ""
echo "Process IDs:"
echo "  - Oscar:  $OSCAR_PID"
echo "  - Minion: $MINION_PID"
echo "  - Marvin: $MARVIN_PID"
echo ""
echo "Logs:"
echo "  - $LOG_DIR/oscar.log"
echo "  - $LOG_DIR/minion.log"
echo "  - $LOG_DIR/marvin.log"
echo ""
echo "To stop all components:"
echo "  kill $OSCAR_PID $MINION_PID $MARVIN_PID"
echo ""
echo "Dashboard should appear in a few seconds..."
echo ""

# Save PIDs to file for easy cleanup
echo "$OSCAR_PID" > "$LOG_DIR/oscar.pid"
echo "$MINION_PID" > "$LOG_DIR/minion.pid"
echo "$MARVIN_PID" > "$LOG_DIR/marvin.pid"

echo "PID files saved to $LOG_DIR/*.pid"
echo ""
