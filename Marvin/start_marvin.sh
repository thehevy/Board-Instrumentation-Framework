#!/bin/bash
# =============================================================================
# Start Marvin with automatic cleanup of existing instances
# =============================================================================
# Usage: ./start_marvin.sh -c <config.xml> [additional java args...]
# Example: ./start_marvin.sh -c App.Config.xml -vvvv
#
# This script:
# 1. Checks if Marvin is already running with the same config
# 2. Stops the existing instance if found
# 3. Launches new instance with specified config
# =============================================================================

# Parse arguments
CONFIG_FILE=""
JAVA_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -h|--help)
            cat << EOF
============================================================
  BIFF Marvin - Startup Script
============================================================

USAGE:
  ./start_marvin.sh -c <config.xml> [java_args...]

REQUIRED:
  -c, --config <file>   Configuration file (e.g., Application.xml)

OPTIONAL JAVA ARGS:
  -vvvv                 Enable verbose logging
  -log <file>           Output log to HTML file
  -nowebserver          Disable embedded web server

EXAMPLES:
  ./start_marvin.sh -c Application.xml
      Start with basic configuration

  ./start_marvin.sh -c Application.xml -vvvv
      Start with verbose logging

  ./start_marvin.sh -c Application.xml -log output.html
      Start and log to HTML file

MANAGEMENT:
  Stop: pkill -f "BIFF.Marvin.jar.*$CONFIG_FILE"

EOF
            exit 0
            ;;
        *)
            JAVA_ARGS+=("$1")
            shift
            ;;
    esac
done

# Validate config file
if [ -z "$CONFIG_FILE" ]; then
    echo "ERROR: Configuration file required"
    echo "Usage: ./start_marvin.sh -c <config.xml> [java_args...]"
    echo "Use -h or --help for more information"
    exit 1
fi

# Get absolute path to config file
if [[ "$CONFIG_FILE" = /* ]]; then
    CONFIG_PATH="$CONFIG_FILE"
else
    CONFIG_PATH="$(cd "$(dirname "$CONFIG_FILE")" 2>/dev/null && pwd)/$(basename "$CONFIG_FILE")"
fi

if [ ! -f "$CONFIG_PATH" ]; then
    echo "ERROR: Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# Check for Java
if ! command -v java &> /dev/null; then
    echo "ERROR: Java not found in PATH"
    echo "Install Java 10+ and ensure it's in your PATH"
    exit 1
fi

# Verify Java version (need 10+)
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | awk -F '"' '{print $2}' | awk -F '.' '{print $1}')
if [ "$JAVA_VERSION" -lt 10 ] 2>/dev/null; then
    echo "WARNING: Java 10+ recommended, found version: $(java -version 2>&1 | head -n 1)"
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for JAR file - support both development (build/libs/) and package (flat) structures
DEV_JAR_PATH="build/libs/BIFF.Marvin.jar"
PACKAGE_JAR_PATH="BIFF.Marvin.jar"

if [ -f "$DEV_JAR_PATH" ]; then
    JAR_PATH="$DEV_JAR_PATH"
    ENVIRONMENT="development"
elif [ -f "$PACKAGE_JAR_PATH" ]; then
    JAR_PATH="$PACKAGE_JAR_PATH"
    ENVIRONMENT="package"
else
    echo "ERROR: BIFF.Marvin.jar not found"
    echo "  Development: build/libs/BIFF.Marvin.jar"
    echo "  Package:     BIFF.Marvin.jar"
    echo "Run './gradlew build' first (if in development environment)"
    exit 1
fi

echo "Checking for existing Marvin instance with config: $CONFIG_PATH"

# Find and kill existing instance with same config
EXISTING_PIDS=$(ps aux | grep -E "java.*BIFF\.Marvin\.jar.*$CONFIG_PATH" | grep -v grep | awk '{print $2}')

if [ -n "$EXISTING_PIDS" ]; then
    echo "Stopping existing Marvin instance(s):"
    for PID in $EXISTING_PIDS; do
        echo "  PID: $PID"
        kill $PID 2>/dev/null
    done
    sleep 2
    
    # Force kill if still running
    STILL_RUNNING=$(ps aux | grep -E "java.*BIFF\.Marvin\.jar.*$CONFIG_PATH" | grep -v grep | awk '{print $2}')
    if [ -n "$STILL_RUNNING" ]; then
        echo "Force stopping remaining processes..."
        for PID in $STILL_RUNNING; do
            kill -9 $PID 2>/dev/null
        done
    fi
    echo "Existing instance(s) stopped"
else
    echo "No existing instance found"
fi

echo ""
echo "Starting Marvin with config: $CONFIG_PATH"
echo "Additional args: ${JAVA_ARGS[*]}"
echo "Environment: $ENVIRONMENT"
echo ""

# Launch Marvin
java -jar "$JAR_PATH" -c "$CONFIG_PATH" "${JAVA_ARGS[@]}" &
MARVIN_PID=$!

# Wait briefly and check if process started
sleep 1
if ps -p $MARVIN_PID > /dev/null 2>&1; then
    echo "============================================================"
    echo "  Marvin Started Successfully!"
    echo "============================================================"
    echo ""
    echo "  PID:    $MARVIN_PID"
    echo "  Config: $CONFIG_PATH"
    echo "  JAR:    $JAR_PATH"
    echo ""
    echo "MANAGEMENT:"
    echo "  Stop:   kill $MARVIN_PID"
    echo "  Status: ps -p $MARVIN_PID"
    echo ""
else
    echo "ERROR: Marvin failed to start"
    echo "Check console output above for errors"
    exit 1
fi
