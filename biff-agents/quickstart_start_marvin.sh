#!/bin/bash
###############################################################################
# Quickstart - Start Marvin with Generated Configuration
# Runs Marvin GUI using quickstart test configuration
###############################################################################

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BIFF_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
MARVIN_CONFIG="$SCRIPT_DIR/biff-quickstart-test/ApplicationConfig.xml"
MARVIN_JAR="$BIFF_ROOT/Marvin/build/libs/BIFF.Marvin.jar"
MARVIN_DIR="$BIFF_ROOT/Marvin"

# Check if config exists
if [ ! -f "$MARVIN_CONFIG" ]; then
    echo "[ERROR] Marvin config not found: $MARVIN_CONFIG"
    echo "Run: python biff_cli/biff_cli.py configure quickstart"
    exit 1
fi

# Check if JAR exists
if [ ! -f "$MARVIN_JAR" ]; then
    echo "[ERROR] Marvin JAR not found: $MARVIN_JAR"
    echo "Build Marvin first with: cd Marvin && ./gradlew build"
    exit 1
fi

# Check Java
if ! command -v java &> /dev/null; then
    echo "[ERROR] Java not found. Please install Java 10+"
    exit 1
fi

echo "============================================================"
echo "  Starting Quickstart Marvin GUI"
echo "============================================================"
echo ""
echo "Config: $MARVIN_CONFIG"
echo "JAR: $MARVIN_JAR"
echo ""

# Change to Marvin directory and launch
cd "$MARVIN_DIR"
exec java -jar "$MARVIN_JAR" -a "$MARVIN_CONFIG" -vvvv
