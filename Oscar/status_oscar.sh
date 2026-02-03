#!/bin/bash
# ==============================================================================
# BIFF Oscar - Status Check Script for Linux/Unix
# ==============================================================================
# Purpose: Display runtime status and diagnostics for Oscar
# Usage:   ./status_oscar.sh
# ==============================================================================

# Format bytes to human-readable
format_bytes() {
    local bytes=$1
    if [ $bytes -lt 1024 ]; then
        echo "${bytes} B"
    elif [ $bytes -lt 1048576 ]; then
        echo "$(awk "BEGIN {printf \"%.2f\", $bytes/1024}") KB"
    elif [ $bytes -lt 1073741824 ]; then
        echo "$(awk "BEGIN {printf \"%.2f\", $bytes/1048576}") MB"
    else
        echo "$(awk "BEGIN {printf \"%.2f\", $bytes/1073741824}") GB"
    fi
}

# Format duration
format_duration() {
    local seconds=$1
    local days=$((seconds / 86400))
    local hours=$(((seconds % 86400) / 3600))
    local minutes=$(((seconds % 3600) / 60))
    local secs=$((seconds % 60))
    
    if [ $days -gt 0 ]; then
        echo "${days}d ${hours}h ${minutes}m ${secs}s"
    elif [ $hours -gt 0 ]; then
        echo "${hours}h ${minutes}m ${secs}s"
    elif [ $minutes -gt 0 ]; then
        echo "${minutes}m ${secs}s"
    else
        echo "${secs}s"
    fi
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Banner
echo ""
echo "============================================================"
echo "  BIFF Oscar - Status Check"
echo "============================================================"
echo ""

PID_FILE="$SCRIPT_DIR/.oscar.pid"
LOG_FILE="$SCRIPT_DIR/OscarLog.txt"
OSCAR_PID=""

# Try to find Oscar by PID file
if [ -f "$PID_FILE" ]; then
    SAVED_PID=$(cat "$PID_FILE" 2>/dev/null)
    if [ -n "$SAVED_PID" ] && ps -p $SAVED_PID > /dev/null 2>&1; then
        OSCAR_PID=$SAVED_PID
    else
        echo "[WARNING] PID file exists but process not found"
        rm -f "$PID_FILE"
    fi
fi

# Fallback: Find Oscar by process search
if [ -z "$OSCAR_PID" ]; then
    OSCAR_PID=$(ps aux | grep -E "python.*Oscar\.py" | grep -v grep | awk '{print $2}' | head -1)
fi

# Display status
if [ -n "$OSCAR_PID" ]; then
    echo "STATUS: 🟢 RUNNING"
    echo ""
    echo "PROCESS INFORMATION:"
    echo "  PID:          $OSCAR_PID"
    
    # Get process info
    if command -v ps &> /dev/null; then
        # CPU and Memory
        CPU_MEM=$(ps -p $OSCAR_PID -o %cpu,%mem --no-headers 2>/dev/null)
        if [ -n "$CPU_MEM" ]; then
            CPU=$(echo $CPU_MEM | awk '{print $1}')
            MEM=$(echo $CPU_MEM | awk '{print $2}')
            echo "  CPU Usage:    ${CPU}%"
            echo "  Memory:       ${MEM}%"
        fi
        
        # Start time and uptime
        if [ "$(uname)" = "Linux" ]; then
            START_TIME=$(ps -p $OSCAR_PID -o lstart --no-headers 2>/dev/null)
            ELAPSED=$(ps -p $OSCAR_PID -o etimes --no-headers 2>/dev/null | tr -d ' ')
            if [ -n "$START_TIME" ]; then
                echo "  Started:      $START_TIME"
            fi
            if [ -n "$ELAPSED" ]; then
                echo "  Uptime:       $(format_duration $ELAPSED)"
            fi
        elif [ "$(uname)" = "Darwin" ]; then
            START_TIME=$(ps -p $OSCAR_PID -o lstart 2>/dev/null | tail -1)
            if [ -n "$START_TIME" ]; then
                echo "  Started:      $START_TIME"
            fi
        fi
        
        # Command line
        CMDLINE=$(ps -p $OSCAR_PID -o command --no-headers 2>/dev/null)
        if [ -n "$CMDLINE" ]; then
            echo "  Command:      $CMDLINE"
        fi
    fi
    
    # Log file info
    echo ""
    echo "LOG FILE:"
    if [ -f "$LOG_FILE" ]; then
        LOG_SIZE=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null)
        if [ -n "$LOG_SIZE" ]; then
            echo "  Path:         $LOG_FILE"
            echo "  Size:         $(format_bytes $LOG_SIZE)"
            
            # Recent log lines
            echo ""
            echo "RECENT LOG ENTRIES (last 10 lines):"
            echo "------------------------------------------------------------"
            tail -n 10 "$LOG_FILE" 2>/dev/null || echo "  [Unable to read log file]"
            echo "------------------------------------------------------------"
        fi
    else
        echo "  Path:         $LOG_FILE (not found)"
    fi
    
    echo ""
    echo "MANAGEMENT:"
    echo "  Stop:         ./stop_oscar.sh"
    echo "  View Logs:    tail -f $LOG_FILE"
    
else
    echo "STATUS: 🔴 NOT RUNNING"
    echo ""
    
    # Check for log file
    if [ -f "$LOG_FILE" ]; then
        LOG_SIZE=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null)
        echo "LOG FILE:"
        echo "  Path:         $LOG_FILE"
        if [ -n "$LOG_SIZE" ]; then
            echo "  Size:         $(format_bytes $LOG_SIZE)"
        fi
        
        # Recent log lines
        echo ""
        echo "RECENT LOG ENTRIES (last 10 lines):"
        echo "------------------------------------------------------------"
        tail -n 10 "$LOG_FILE" 2>/dev/null || echo "  [Unable to read log file]"
        echo "------------------------------------------------------------"
    else
        echo "LOG FILE: Not found ($LOG_FILE)"
    fi
    
    echo ""
    echo "MANAGEMENT:"
    echo "  Start:        ./start_oscar.sh"
fi

echo ""
echo "============================================================"
echo ""
