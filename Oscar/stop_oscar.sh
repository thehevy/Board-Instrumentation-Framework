#!/bin/bash
# ==============================================================================
# BIFF Oscar - Stop Script for Linux/Unix
# ==============================================================================
# Purpose: Gracefully stop running Oscar instance(s)
# Usage:   ./stop_oscar.sh
# ==============================================================================

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Banner
echo ""
echo "============================================================"
echo "  BIFF Oscar - Stopping Data Broker"
echo "============================================================"
echo ""

PID_FILE="$SCRIPT_DIR/.oscar.pid"
STOPPED_ANY=false

# Try to stop Oscar using PID file
if [ -f "$PID_FILE" ]; then
    SAVED_PID=$(cat "$PID_FILE" 2>/dev/null)
    if [ -n "$SAVED_PID" ]; then
        if ps -p $SAVED_PID > /dev/null 2>&1; then
            echo "[INFO] Stopping Oscar (PID: $SAVED_PID)..."
            kill $SAVED_PID 2>/dev/null
            
            # Wait up to 5 seconds for graceful shutdown
            for i in {1..10}; do
                if ! ps -p $SAVED_PID > /dev/null 2>&1; then
                    echo "[SUCCESS] Oscar stopped (PID: $SAVED_PID)"
                    STOPPED_ANY=true
                    break
                fi
                sleep 0.5
            done
            
            # Force kill if still running
            if ps -p $SAVED_PID > /dev/null 2>&1; then
                echo "[INFO] Force stopping Oscar (PID: $SAVED_PID)..."
                kill -9 $SAVED_PID 2>/dev/null
                echo "[SUCCESS] Oscar force stopped (PID: $SAVED_PID)"
                STOPPED_ANY=true
            fi
        else
            echo "[WARNING] PID file exists but process not found (PID: $SAVED_PID)"
        fi
    fi
    rm -f "$PID_FILE"
fi

# Fallback: Find Oscar by process name
OSCAR_PIDS=$(ps aux | grep -E "python.*Oscar\.py" | grep -v grep | awk '{print $2}')

if [ -n "$OSCAR_PIDS" ]; then
    echo "[INFO] Found Oscar process(es) by name, stopping..."
    for PID in $OSCAR_PIDS; do
        echo "[INFO] Stopping Oscar (PID: $PID)..."
        kill $PID 2>/dev/null
        
        # Wait for graceful shutdown
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                echo "[SUCCESS] Oscar stopped (PID: $PID)"
                STOPPED_ANY=true
                break
            fi
            sleep 0.5
        done
        
        # Force kill if needed
        if ps -p $PID > /dev/null 2>&1; then
            echo "[INFO] Force stopping Oscar (PID: $PID)..."
            kill -9 $PID 2>/dev/null
            echo "[SUCCESS] Oscar force stopped (PID: $PID)"
            STOPPED_ANY=true
        fi
    done
fi

# Summary
echo ""
if [ "$STOPPED_ANY" = true ]; then
    echo "============================================================"
    echo "  Oscar Stopped Successfully"
    echo "============================================================"
else
    echo "============================================================"
    echo "  No Running Oscar Instances Found"
    echo "============================================================"
fi
echo ""
