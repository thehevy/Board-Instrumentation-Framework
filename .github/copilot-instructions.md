# Board Instrumentation Framework (BIFF) - AI Coding Guide

## Architecture Overview

BIFF is a **3-tier instrumentation and visualization framework**:
- **Minion** (Python): Data collection agents that gather metrics via pluggable collectors
- **Oscar** (Python): Data broker/recorder acting as UDP message router and session recorder
- **Marvin** (JavaFX 10+): Highly configurable UI displaying data through XML-configured widgets

**Data Flow**: `Minion collectors → UDP → Oscar (port 1100) → UDP → Marvin (ports 52001+)`

Communication uses XML packets over UDP. Minion namespaces organize collectors; Oscar routes by namespace/ID; Marvin widgets bind to data via `<MinionSrc Namespace="..." ID="..."/>`.

## Build & Run Commands

### Marvin (Java/Gradle)
```powershell
# Full build sequence (required for first build)
cd Marvin\Dependencies\Enzo
.\gradlew build
cd ..\..
.\gradlew copyEnzoJar
.\gradlew build

# Quick rebuild (if Enzo already built)
.\gradlew build

# Output: build\libs\BIFF.Marvin.jar
# Deployment: Copy JAR + Widget\ directory together
```

**Version Management**: Build updates `src/main/resources/kutch/biff/marvin/version/Marvin.version.properties` automatically. Use `-PupdateReleaseInfo` to increment build number.

### Minion (Python)
```powershell
python Minion\Minion.py -c <config.xml>
# Config defaults to MinionConfig.xml
```

### Oscar (Python)
```powershell
python Oscar\Oscar.py -c OscarConfig.xml
```

**No automated tests exist** - testing relies on demonstration configs in `*/Demonstration/` directories.

## Project Structure & Key Files

### Marvin (Java)
- `src/main/java/kutch/biff/marvin/`
  - `Marvin.java` - JavaFX Application entry point
  - `widget/BaseWidget.java` - Base class for all widgets (40+ widget types)
  - `widget/widgetbuilder/` - XML-to-widget factories (one per widget type)
  - `datamanager/DataManager.java` - Singleton managing all data bindings via namespace:ID keys
  - `task/` - Task framework for interactivity (38 task types including Minion remote execution)
  - `configuration/Configuration.java` - XML application config parser
  - `network/Client.java` - UDP sender for Oscar communication

**Widget Pattern**: Widgets extend `BaseWidget`, implement `HandleIncomingSteppedData()`, bind to data sources via `<MinionSrc>`, and support CSS styling via `.css` files in `Widget/<type>/` directories.

### Minion (Python)
- `Minion.py` - Entry point with CLI arg parsing
- `Helpers/Configuration.py` - XML config parser organizing Namespaces → Collectors/Actors/Groups
- `Helpers/Collector.py` - Core collector runner with scheduling, normalization, delta-detection
- `Helpers/Namespace.py` - Container grouping collectors by namespace with threading model control
- `Collectors/` - 30+ built-in collectors (RandomVal, CPU, Docker, Prometheus, etc.)
  - Convention: Collectors print to stdout; Minion captures and transmits
  - Support external executables or Python plugins via `<Executable>` tag

**Threading Model**: `SingleThreading="true"` in `<Minion>` uses one thread per namespace (default: thread-per-collector).

### Oscar (Python)
- `Oscar.py` - Entry point with playback/record CLI
- `Helpers/Configuration.py` - Defines upstream (Minion) and downstream (Marvin) connections
- `Helpers/MarvinDataHandler.py` - Parses incoming Marvin task requests (remote Minion task execution)
- `Data/ConnectionPoint.py` - UDP socket abstraction

## Configuration Patterns

### XML is Central
All three components use XML for configuration. **Alias system** (`<AliasList>`) enables variable substitution throughout configs using `$(ALIAS_NAME)` syntax.

**Minion Config Structure**:
```xml
<Minion SingleThreading="true|false">
  <AliasList>...</AliasList>
  <Namespace>
    <Name>MyNamespace</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="5100"/>
    <Collector ID="cpu.usage" Frequency="500">
      <Executable>Collectors\CPU.py</Executable>
      <Param>GetUsage</Param>
    </Collector>
    <Actor ID="restart_service">...</Actor>
  </Namespace>
</Minion>
```

**Oscar Config**: Maps incoming Minion port (1100) to multiple Marvin target ports.

**Marvin Config**: Defines grids/tabs containing widgets. Widgets reference data via `<MinionSrc Namespace="X" ID="Y"/>`.

### Widget Definition Pattern
Widgets can be defined inline or in reusable XML files (`Widget/<type>/*.xml`). Use `<AliasList>` with `<DefinitionFile File="Widget/Gauge/MyGauge.xml">` to parameterize widgets.

## Coding Conventions

### Java (Marvin)
- Package: `kutch.biff.marvin.*`
- Singletons: `DataManager.getDataManager()`, `Configuration.getConfiguration()`
- Widget lifecycle: `Create()` → register listeners → `HandleIncomingSteppedData(value)`
- **No unit tests** - verify changes by running with demo configs
- JavaFX UI thread: Use `Platform.runLater()` for widget updates from network threads
- Logging: `Logger.getLogger(MarvinLogger.class.getName())`

### Python (Minion/Oscar)
- Modules: `from Helpers import Configuration, Log, Alias`
- Singletons: `Configuration._Instance`, `MarvinDataHandler._instance`
- Collectors: External scripts print to stdout; internal use `return str(value)`
- Logging: `Log.getLogger()` (configured in main entry points)
- XML parsing: `xml.dom.minidom` with exception handling for `ExpatError`

## Common Development Tasks

**Adding a new widget**: 
1. Create `src/main/java/kutch/biff/marvin/widget/<Type>Widget.java` extending `BaseWidget`
2. Create `widget/widgetbuilder/<Type>Builder.java` with `Build(FrameworkNode)` method
3. Register in `WidgetBuilder.java` type map
4. Add example XML to `Widget/<Type>/` directory

**Adding a collector**: 
1. Create `Minion/Collectors/<Name>.py` with function printing value to stdout
2. Document parameters in function docstring
3. Add example to `Minion/Demonstration/DemoConfig.xml`

**Production patterns from Intel Vision Demo**:
- **Template collectors**: Use `<ExternalFile PORT_NUM="1">template.xml</ExternalFile>` to reuse collector configs with parameters
- **File watchers**: `<DynamicCollector><File>results.txt</File></DynamicCollector>` reads metrics from filesystem (zero-instrumentation)
- **Aggregate collectors**: Use `<Operator>Addition</Operator>` with `<Repeat Count="5">` to sum multiple metrics
- **GridMacro**: Define reusable widget templates with `<GridMacro Name="...">`, instantiate with parameter variations
- **Multi-level aliases**: Use `<Import>DefinitionFiles/aliases.xml</Import>` to organize design systems (colors, fonts, calculations)
- **Modifier normalization**: Add `<Modifier ID="..."><Normalize>0.00000782</Normalize></Modifier>` for unit conversions (bytes→MB)
- **DynamicGrid**: Create data-driven layouts that adapt widget count to collector values
- **Plugin entry points**: Use `<Plugin><EntryPoint>function_name</EntryPoint></Plugin>` to call specific functions in Python modules
- **Style themes**: Apply consistent branding with `<StyleOverride ID="ThemeName"/>` and alias-based color palettes
- **Environment variables**: Use `$(MinionNamespace)`, `$(OscarIP)` from shell exports for runtime configuration (Docker/K8s ready)
- **Actor pattern**: `<Actor ID="..."><Executable>script.sh</Executable></Actor>` enables remote command execution from Marvin GUI
- **Regex modifiers**: `<Modifier ID="P(.*)">` applies transformations to all matching metrics (P50, P90, P99, etc.)
- **Multi-deployment**: Single dashboard comparing multiple environments side-by-side via namespace separation
- **CPU affinity**: Pin Minion to dedicated core via `taskset -c $lastCore` to avoid performance interference
- **MarvinAutoConnect**: `AutoConnect="true"` enables automatic Oscar discovery without IP configuration

**Debugging data flow**:
- Enable verbose logging in Minion: `-v` flag
- Oscar GUI shows live data streams (no GUI: check `OscarLog.txt`)
- Marvin: Window → About shows connection status; logs to console

## Dependencies

**Marvin**: Enzo gauge library (custom build in `Dependencies/Enzo/`) - must build before Marvin.

**Python**: No `requirements.txt` - most collectors use stdlib. Optional: `psutil`, `docker`, `requests`, `prometheus_client` (install as needed per collector).

## Anti-Patterns

❌ Don't use JSON for configs (XML with Alias system is the standard)
❌ Don't create REST APIs (UDP is the protocol)
❌ Don't assume thread safety in widgets (use JavaFX thread via `Platform.runLater`)
❌ Don't hard-code IPs/ports (use Alias or config attributes)
❌ Don't add test frameworks without discussion (none exist currently)

## References

- 200+ page user guide: `BIFF Instrumentation Framework User Guide.pdf`
- Demo configs: `Minion/Demonstration/`, `Oscar/Demonstration/`
- Widget examples: `Widget/<type>/` directories (40+ types)
- Collector examples: `Minion/Collectors/` (30+ collectors)
