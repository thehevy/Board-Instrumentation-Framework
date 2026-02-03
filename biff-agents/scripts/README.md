# BIFF Quick Start Launcher Scripts

These scripts automate the startup of all BIFF components (Oscar, Minion, and Marvin) for quick testing and development.

## Prerequisites

1. **Generate configs first**:
   ```bash
   cd biff-agents
   python -m biff_cli quickstart
   ```
   This creates `quickstart_configs/` with all necessary XML files.

2. **Existing BIFF installation**: Scripts expect to find Oscar/Minion/Marvin directories in the parent directory structure.

## Usage

### Windows

```cmd
cd biff-agents\scripts
start_all.bat
```

This will:
- Detect your BIFF installation location
- Launch Oscar in a new window (data broker)
- Launch Minion in a new window (data collector)
- Build Marvin if needed (first-time only)
- Launch Marvin GUI in a new window

To stop: Close each window or press Ctrl+C in each terminal.

### Linux/Mac

```bash
cd biff-agents/scripts
chmod +x start_all.sh stop_all.sh  # First time only
./start_all.sh
```

This will:
- Detect your BIFF installation location
- Start Oscar in the background
- Start Minion in the background
- Build Marvin if needed (first-time only)
- Launch Marvin GUI

Logs are saved to `biff-agents/logs/`:
- `oscar.log` - Oscar output
- `minion.log` - Minion output
- `marvin.log` - Marvin output

To stop:
```bash
./stop_all.sh
```

Or manually:
```bash
kill $(cat ../logs/oscar.pid) $(cat ../logs/minion.pid) $(cat ../logs/marvin.pid)
```

## What the Scripts Do

### start_all.bat / start_all.sh

1. **Validation**:
   - Check if `quickstart_configs/` directory exists
   - Verify MinionConfig.xml, OscarConfig.xml, Application.xml are present
   - Detect BIFF installation path

2. **Oscar Launch** (Port 1100):
   - Routes data from Minion to Marvin
   - Must start first (it's the broker)
   - Wait 3 seconds for initialization

3. **Minion Launch** (Port 5100):
   - Starts collecting metrics (RandomVal, Timer, CPU, etc.)
   - Sends data to Oscar every 1-2 seconds
   - Wait 2 seconds for initialization

4. **Marvin Build** (first-time only):
   - Check if `build/libs/BIFF.Marvin.jar` exists
   - If not, run `gradlew build`
   - Requires Java 11+ and Gradle

5. **Marvin Launch** (Port 52001):
   - Displays dashboard with 6 widgets
   - Receives data from Oscar
   - GUI should appear in 2-3 seconds

### stop_all.sh (Linux/Mac only)

- Reads PID files from `logs/` directory
- Gracefully stops all processes
- Cleans up PID files

## Troubleshooting

### "Config directory not found"

**Solution**: Run `python -m biff_cli quickstart` first to generate configs.

### "BIFF installation not detected"

**Solution**: Make sure you're running from `biff-agents/scripts/` and that Oscar/Minion/Marvin directories exist in the parent path:
```
Board-Instrumentation-Framework/
├── Oscar/
├── Minion/
├── Marvin/
└── biff-agents/
    └── scripts/  ← You are here
```

### "Marvin build failed"

**Solution**: Check Java and Gradle installation:
```bash
java -version    # Should be 11+
gradle --version # Should be 6.0+
```

### Marvin GUI doesn't appear

**Solution**: Check logs for errors:
- Windows: Look at the Marvin terminal window
- Linux: `cat ../logs/marvin.log`

Common issues:
- Java not installed: `sudo apt install openjdk-11-jdk` (Linux)
- Display issue on Linux: `export DISPLAY=:0`
- Port 52001 in use: Change in Application.xml

### No data in Marvin widgets

**Checklist**:
1. Oscar running? Check terminal/log for "listening on port 1100"
2. Minion running? Check terminal/log for "connected to Oscar"
3. Ports correct? Minion → Oscar (1100), Oscar → Marvin (52001)
4. Firewall blocking UDP? Temporarily disable to test

**Debug mode**:
```bash
# Check Minion output
tail -f logs/minion.log  # Should see "Sent data: <Namespace>QuickStart</Namespace>"

# Check Oscar routing
tail -f logs/oscar.log   # Should see "Forwarding data to Marvin"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Minion (Port 5100)                                         │
│  ├─ RandomVal collector → sends data every 1s              │
│  ├─ Timer collector → sends data every 2s                  │
│  └─ CPU collector → sends data every 1s                    │
│                                                             │
│              │                                              │
│              │ UDP packets with <Namespace>QuickStart       │
│              ▼                                              │
│                                                             │
│  Oscar (Port 1100)                                          │
│  ├─ Receives from Minion                                   │
│  ├─ Routes by namespace                                    │
│  └─ Forwards to Marvin                                     │
│                                                             │
│              │                                              │
│              │ UDP packets to port 52001                    │
│              ▼                                              │
│                                                             │
│  Marvin (Port 52001)                                        │
│  ├─ Receives data from Oscar                               │
│  ├─ Updates widgets via <MinionSrc> bindings               │
│  └─ Displays dashboard                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Advanced Usage

### Custom Config Directory

Edit the scripts to point to a different config directory:

**Windows (start_all.bat)**:
```batch
set "CONFIG_DIR=my_custom_configs"
```

**Linux (start_all.sh)**:
```bash
CONFIG_DIR="$BIFF_AGENTS_ROOT/my_custom_configs"
```

### Running Components Individually

**Oscar**:
```bash
cd Oscar
python Oscar.py -c ../biff-agents/quickstart_configs/OscarConfig.xml
```

**Minion**:
```bash
cd Minion
python Minion.py -c ../biff-agents/quickstart_configs/MinionConfig.xml
```

**Marvin**:
```bash
cd Marvin
./gradlew build  # First time only
java -jar build/libs/BIFF.Marvin.jar -a ../biff-agents/quickstart_configs/Application.xml
```

### Multiple Instances

To run multiple BIFF setups simultaneously:

1. Generate configs with different namespaces:
   ```bash
   python -m biff_cli quickstart  # Namespace: QuickStart
   # Edit configs to use different ports
   ```

2. Copy launcher script and update ports in configs

3. Run each launcher

## See Also

- [Day 5 Summary](../docs/Day5_Summary.md) - Implementation details
- [QUICKSTART.md](../QUICKSTART.md) - Full quick start guide
- [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) - Development roadmap
