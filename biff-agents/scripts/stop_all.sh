#!/bin/bash
###############################################################################
# BIFF Quick Start - Stop All Components
# Stops Oscar, Minion, and Marvin processes
###############################################################################

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BIFF_AGENTS_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$BIFF_AGENTS_ROOT/logs"

echo ""
echo "============================================================"
echo "  Stopping BIFF Components"
echo "============================================================"
echo ""

# Check if PID files exist
if [ ! -d "$LOG_DIR" ]; then
    echo "[WARNING] Log directory not found: $LOG_DIR"
    echo "[INFO] Components may not be running"
    exit 0
fi

# Stop Oscar
if [ -f "$LOG_DIR/oscar.pid" ]; then
    OSCAR_PID=$(cat "$LOG_DIR/oscar.pid")
    if kill -0 "$OSCAR_PID" 2>/dev/null; then
        echo "[INFO] Stopping Oscar (PID: $OSCAR_PID)..."
        kill "$OSCAR_PID"
        echo "      [OK] Oscar stopped"
    else
        echo "[INFO] Oscar not running"
    fi
    rm -f "$LOG_DIR/oscar.pid"
fi

# Stop Minion
if [ -f "$LOG_DIR/minion.pid" ]; then
    MINION_PID=$(cat "$LOG_DIR/minion.pid")
    if kill -0 "$MINION_PID" 2>/dev/null; then
        echo "[INFO] Stopping Minion (PID: $MINION_PID)..."
        kill "$MINION_PID"
        echo "      [OK] Minion stopped"
    else
        echo "[INFO] Minion not running"
    fi
    rm -f "$LOG_DIR/minion.pid"
fi

# Stop Marvin
if [ -f "$LOG_DIR/marvin.pid" ]; then
    MARVIN_PID=$(cat "$LOG_DIR/marvin.pid")
    if kill -0 "$MARVIN_PID" 2>/dev/null; then
        echo "[INFO] Stopping Marvin (PID: $MARVIN_PID)..."
        kill "$MARVIN_PID"
        echo "      [OK] Marvin stopped"
    else
        echo "[INFO] Marvin not running"
    fi
    rm -f "$LOG_DIR/marvin.pid"
fi

echo ""
echo "[OK] All BIFF components stopped"
echo ""
