# Board-Instrumentation-Framework
This project allows you to instrument and graphically display pretty much anything you want in a flexible way. 
It consists of 3 parts, the data collector (Minion) written in Python, which sends data over a UDP socket to the data broker and recorder called Oscar, also written in Python.  The last part is a Java FX application called Marvin, which receives data from Oscar and displays it via a library of highly configurable 'widgets'.

Here are a couple of my YouTube videos that make use of this framework:
https://www.youtube.com/watch?v=6UUFWZs-Sck
https://www.youtube.com/watch?v=NYI8BDv17Lw

Marvin is now a Java 10+ application.  If you need Java 8, checkout the JAVA_8 branch.

## Quick Start - Windows

### Oscar (Data Broker)
```powershell
cd Oscar
.\start_oscar.bat         # Start in background
.\status_oscar.bat        # Check status
.\stop_oscar.bat          # Stop gracefully
```

See [Oscar/SCRIPTS_README.md](Oscar/SCRIPTS_README.md) for advanced usage.

### Minion (Data Collector)
```powershell
cd Minion
python Minion.py -c MinionConfig.xml
```

### Marvin (GUI)

**Prerequisites:** Java 10+ must be in PATH

```powershell
# If Java not in PATH, configure environment:
.\setup_java.ps1          # PowerShell
# OR
setup_java.bat            # Command Prompt

# Then build and run:
cd Marvin
.\gradlew build
java -jar build\libs\BIFF.Marvin.jar
```

**Note:** If you encounter "JAVA_HOME is not set" error, use the setup scripts above.

## Deployment & Packaging

Create standalone deployment packages with all components:

```powershell
# Build complete package with configurations
python biff-agents\build_package.py --config-source biff-agents\biff-quickstart-test

# Or use wrapper scripts
.\build_package.bat
.\build_package.ps1
```

Generates `BIFF-Package-<version>-<date>/` with Marvin, Oscar, Minion, configs, startup scripts, and documentation. See [PACKAGING.md](PACKAGING.md) for details.

---




Take a look at the 200+ page BIFF Instrumenation Framework User Guide.pdf file for details: https://github.com/intel/Board-Instrumentation-Framework/blob/master/BIFF%20Instrumentation%20Framework%20User%20Guide.pdf.
