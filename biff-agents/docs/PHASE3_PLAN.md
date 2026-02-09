# Phase 3: Marvin GUI Composer - Complete Plan

**Start Date**: February 9, 2026  
**Duration**: 2-3 weeks (Weeks 8-10)  
**Goal**: Automate Marvin dashboard configuration with interactive wizards  
**Status**: 🎯 PLANNING

---

## Overview

Phase 3 completes the 3-tier BIFF stack automation by providing tools to generate Marvin GUI configurations. While Phase 2 automated **data collection** (Minion), Phase 3 automates **data visualization** (Marvin).

### Why Marvin Automation Matters

**Current Challenges**:
- 40+ widget types with different XML schemas
- Complex grid layouts (rows, columns, spans)
- Data binding requires namespace/ID knowledge
- Styling via CSS and inline overrides
- Alias system for reusable configurations
- No validation until runtime

**After Phase 3**:
- Interactive widget configuration wizards
- Automatic grid layout generation
- Data source discovery from Minion configs
- Style templates and themes
- Pre-flight validation
- Dashboard templates for common scenarios

---

## Architecture Analysis

### Marvin Configuration Structure

```
App.Config.xml (Root)
├── <Application>
│   ├── CreationSize, Network, Title
│   ├── StyleSheet, Tasks, MainMenu
│   └── <Tabs>
│       └── <Tab ID="..."/> references
├── <Tab> definitions
│   ├── Title, Align
│   └── File="path/to/tab.xml"
├── <AliasList>
│   ├── <Alias> definitions
│   └── <Import> external alias files
└── External Tab Files
    └── <Grid> with <Widget> elements
```

### Widget Patterns (from Intel Vision Demo)

**40+ Widget Types in 13 Categories**:
1. **Data Display** (20 types)
   - Text, LED, Gauge (8 variants), LCD, Indicator
2. **Charts** (5 types)
   - LineChart, BarChart, PieChart, StackedAreaChart, etc.
3. **Media** (3 types)
   - Image, AudioPlayer, VideoPlayer
4. **System** (4 types)
   - CPU, Memory, Storage, Networking
5. **Controls** (3 types)
   - Button, FlipPanel, Web
6. **Layout** (2 types)
   - Spacer, PDF
7. **Specialty** (3 types)
   - LCARS, SVG, Quick

### Data Binding Pattern

```xml
<Widget File="Gauge/Gauge.xml" row="1" column="1">
    <Title>CPU Usage</Title>
    <UnitText>%</UnitText>
    <MinionSrc Namespace="system" ID="cpu.usage"/>
    <MaxValue>100</MaxValue>
    <MinValue>0</MinValue>
</Widget>
```

**Key Elements**:
- `<MinionSrc Namespace="..." ID="..."/>` - Data binding
- Widget file reference (reusable templates)
- Grid positioning (row, column)
- Configuration overrides (Title, UnitText, etc.)

### Grid Layout Pattern

```xml
<Grid row="1" column="1">
    <StyleOverride>...</StyleOverride>
    <Widget ... row="1" column="1" />
    <Widget ... row="1" column="2" />
    <Widget ... row="2" column="1" columnSpan="2"/>
</Grid>
```

**Layout Features**:
- Row/column grid system
- Column/row spanning
- Alignment (N, S, E, W, NW, etc.)
- Style overrides per widget

---

## Production Pattern Analysis

### Intel Vision Demo Widgets

**From BIFF_FINDINGS/Marvin_Complex_Example/ExperienceKit**:

**Widget Distribution**:
- **Text widgets**: 45+ (titles, labels, metrics)
- **Gauge widgets**: 12 (CPU, network, latency)
- **Chart widgets**: 8 (performance graphs)
- **LED indicators**: 15 (status lights)
- **Image widgets**: 10 (logos, diagrams)
- **Button widgets**: 6 (interactions)
- **FlipPanel widgets**: 4 (multi-view displays)

**Total**: ~100 widgets across 5 tabs

**Common Patterns**:
1. **Dashboard Header** - Logo + Title + Status
2. **Metric Panel** - Gauge + Value + Units
3. **Status Row** - Multiple LED indicators
4. **Performance Chart** - LineChart with legend
5. **Info Panel** - Text with dynamic updates

---

## Phase 3 Breakdown

### Week 8: Core Widget Builders (5 days)

#### Day 1: Widget Builder Foundation (4 hours)
- Create base `WidgetBuilder` class
- XML generation framework
- Data source discovery from MinionConfig.xml
- Grid positioning logic

**Deliverables**:
- `biff_agents_marvin/builders/widget_builder.py` (~300 LOC)
- `biff_agents_marvin/utils/minion_discovery.py` (~150 LOC)

#### Day 2: Text & LED Widgets (3 hours)
- Text widget builder (most common)
- LED indicator builder
- Label widget builder

**Deliverables**:
- `text_widget_builder.py` (~200 LOC)
- `led_widget_builder.py` (~150 LOC)
- CLI: `biff-marvin widget text`, `biff-marvin widget led`

#### Day 3: Gauge Widgets (4 hours)
- Gauge builder with 8 variants
- Auto-scale from data source
- Unit detection and formatting

**Deliverables**:
- `gauge_widget_builder.py` (~300 LOC)
- CLI: `biff-marvin widget gauge`
- Support: Radial, Bar, Simple, OneEighty, etc.

#### Day 4: Chart Widgets (4 hours)
- LineChart builder
- BarChart builder
- PieChart builder

**Deliverables**:
- `chart_widget_builder.py` (~350 LOC)
- CLI: `biff-marvin widget chart`
- Multi-series support

#### Day 5: Testing & Integration (3 hours)
- Widget builder tests
- XML validation
- Integration with Phase 2 (Minion configs)

**Deliverables**:
- Test suite for widget builders
- End-to-end workflow test

---

### Week 9: Layout & Dashboard Composers (5 days)

#### Day 1: Grid Layout Builder (4 hours)
- Interactive grid designer
- Auto-layout algorithms
- Column/row span handling

**Deliverables**:
- `grid_builder.py` (~350 LOC)
- CLI: `biff-marvin layout grid`
- ASCII preview of layout

#### Day 2: Tab Builder (3 hours)
- Tab configuration wizard
- External file management
- Tab title and metadata

**Deliverables**:
- `tab_builder.py` (~250 LOC)
- CLI: `biff-marvin tab create`

#### Day 3: Application Config Builder (4 hours)
- Root config generation
- Network settings
- StyleSheet management
- Tab integration

**Deliverables**:
- `app_config_builder.py` (~300 LOC)
- CLI: `biff-marvin app create`

#### Day 4: Dashboard Templates (4 hours)
- Pre-built dashboard patterns
- CPU monitoring dashboard
- Network monitoring dashboard
- System overview dashboard

**Deliverables**:
- `dashboard_templates.py` (~400 LOC)
- CLI: `biff-marvin dashboard create`
- 5+ templates

#### Day 5: Integration Testing (3 hours)
- Complete workflow tests
- Production pattern validation
- Performance benchmarks

---

### Week 10: Polish & Advanced Features (5 days)

#### Day 1: Style System (3 hours)
- CSS template management
- Color themes
- Font scaling

**Deliverables**:
- `style_builder.py` (~200 LOC)
- CLI: `biff-marvin style create`

#### Day 2: Alias System Integration (3 hours)
- Alias generation
- Design system patterns
- Parameterized dashboards

**Deliverables**:
- `alias_builder.py` (~250 LOC)
- Integration with widget builders

#### Day 3: Validation & Preview (4 hours)
- Pre-flight XML validation
- Widget compatibility checks
- Layout preview (ASCII art)

**Deliverables**:
- `validator.py` (~200 LOC)
- CLI: `biff-marvin validate`

#### Day 4: Documentation (4 hours)
- User guide for Marvin Composer
- Template catalog
- Best practices

**Deliverables**:
- `MARVIN_COMPOSER_GUIDE.md`
- Widget reference docs
- Example dashboards

#### Day 5: Phase 3 Completion (4 hours)
- Final testing
- Bug fixes
- Phase 3 metrics
- Release preparation

---

## Technical Design

### Base Widget Builder

```python
class WidgetBuilder:
    """Base class for all widget builders"""
    
    def __init__(self, minion_config_path: Optional[Path] = None):
        self.minion_config = minion_config_path
        self.data_sources = self._discover_data_sources()
    
    def _discover_data_sources(self) -> List[DataSource]:
        """Parse MinionConfig.xml to find available data sources"""
        # Returns list of (namespace, id, description)
    
    def build_widget(self) -> str:
        """Interactive wizard to build widget XML"""
        # Returns XML string
    
    def validate_widget(self, xml: str) -> Tuple[bool, List[str]]:
        """Validate widget XML against Marvin schema"""
        # Returns (valid, errors)
```

### Widget XML Generation

```python
def generate_gauge_widget(
    title: str,
    namespace: str,
    metric_id: str,
    min_value: float = 0,
    max_value: float = 100,
    unit: str = "",
    row: int = 1,
    column: int = 1
) -> str:
    """Generate gauge widget XML"""
    return f"""
<Widget File="Gauge/Gauge.xml" row="{row}" column="{column}">
    <Title>{title}</Title>
    <UnitText>{unit}</UnitText>
    <MinionSrc Namespace="{namespace}" ID="{metric_id}"/>
    <MaxValue>{max_value}</MaxValue>
    <MinValue>{min_value}</MinValue>
</Widget>
"""
```

### Grid Layout Algorithm

```python
def auto_layout_widgets(
    widgets: List[Widget],
    grid_width: int = 12,
    grid_height: int = 8
) -> GridLayout:
    """Automatically layout widgets in grid"""
    # Algorithm:
    # 1. Sort widgets by priority/size
    # 2. Place largest widgets first
    # 3. Fill remaining space with smaller widgets
    # 4. Return grid with (row, col, span) for each widget
```

---

## CLI Commands

### Widget Commands

```bash
# Create individual widgets
biff-marvin widget text --title "CPU Usage" --source system:cpu.usage
biff-marvin widget gauge --type radial --source system:cpu.temp --max 100
biff-marvin widget chart --type line --sources "net:tx_bytes,net:rx_bytes"
biff-marvin widget led --source system:status --on-value 1

# List available widget types
biff-marvin widget list

# Show widget details
biff-marvin widget info gauge
```

### Layout Commands

```bash
# Create grid layout
biff-marvin layout grid --rows 3 --cols 4 --widgets widget1.xml,widget2.xml

# Auto-layout widgets
biff-marvin layout auto --widgets *.xml --optimize compact

# Preview layout
biff-marvin layout preview grid.xml
```

### Dashboard Commands

```bash
# Create from template
biff-marvin dashboard create --template cpu_monitoring

# Create custom dashboard
biff-marvin dashboard create --name "My Dashboard" --tabs 2

# List available templates
biff-marvin dashboard list-templates
```

### Application Commands

```bash
# Create complete Marvin app
biff-marvin app create --name "System Monitor" --port 52115

# Add tab to existing app
biff-marvin app add-tab --app App.Config.xml --tab monitoring

# Validate app config
biff-marvin app validate App.Config.xml
```

---

## Dashboard Templates

### 1. CPU Monitoring Dashboard

**Widgets**:
- Header: Title + Logo
- Row 1: 4 gauges (usage, temp, freq, load)
- Row 2: LineChart (usage history)
- Row 3: Text display (stats)

**Data Sources**: `system:cpu.*`

### 2. Network Monitoring Dashboard

**Widgets**:
- Header: Title + Status LEDs
- Row 1: 2 gauges (tx, rx throughput)
- Row 2: 2 BarCharts (packets, errors)
- Row 3: Text table (interface stats)

**Data Sources**: `network:eth0.*`

### 3. System Overview Dashboard

**Widgets**:
- Grid 2x2: CPU, Memory, Disk, Network gauges
- Row 2: System info text
- Row 3: Alert panel (LEDs + messages)

**Data Sources**: `system:*`

### 4. Docker Monitoring Dashboard

**Widgets**:
- Header: Container count
- Dynamic grid: One gauge per container
- Row 2: Container status (LEDs)
- Row 3: Resource usage chart

**Data Sources**: `docker:*` (dynamic)

### 5. Custom Dashboard

**Interactive Wizard**:
- Choose layout (1x1, 2x2, 3x3, etc.)
- Select widgets for each position
- Bind to data sources
- Customize colors/theme

---

## Data Source Discovery

### MinionConfig.xml Parser

```python
class MinionDataSourceDiscovery:
    """Discover available data sources from Minion config"""
    
    def discover_sources(self, config_path: Path) -> List[DataSource]:
        """
        Parse MinionConfig.xml and return available sources.
        
        Returns:
            List of DataSource(namespace, id, description, type)
        """
        # Examples:
        # - DataSource("system", "cpu.usage", "CPU Usage %", "float")
        # - DataSource("network", "eth0.tx_bytes", "TX Bytes", "int")
```

### Data Source Matching

When user creates gauge for CPU:
1. Scan MinionConfig.xml for "cpu" collectors
2. Show matching sources: cpu.usage, cpu.temp, cpu.freq
3. Let user select or search
4. Auto-configure widget (units, range, etc.)

---

## Success Criteria

### Functional Requirements

- ✅ Generate valid Marvin XML configs
- ✅ Support 10+ most common widget types
- ✅ Auto-discover data sources from Minion
- ✅ Grid layout with auto-positioning
- ✅ Dashboard templates for common scenarios
- ✅ XML validation before generation

### Quality Requirements

- ✅ 90%+ pattern coverage from Intel Vision Demo
- ✅ <30 seconds per widget (faster than manual)
- ✅ 100% valid XML (no runtime errors)
- ✅ Comprehensive test coverage (15+ tests)

### User Experience Requirements

- ✅ Interactive wizards (not just CLI flags)
- ✅ Helpful defaults (auto-detect ranges, units)
- ✅ Preview before generation
- ✅ Clear error messages

---

## Risks & Mitigation

### Risk 1: Marvin XML Complexity

**Risk**: 40+ widget types with different schemas  
**Mitigation**: Start with 10 most common, expand iteratively  
**Status**: 🟢 Manageable

### Risk 2: Grid Layout Algorithm

**Risk**: Auto-layout might not match user expectations  
**Mitigation**: Provide both auto and manual modes  
**Status**: 🟡 Moderate

### Risk 3: Data Source Discovery

**Risk**: MinionConfig.xml might not have all info  
**Mitigation**: Allow manual override + smart defaults  
**Status**: 🟢 Low

### Risk 4: Validation Complexity

**Risk**: Hard to validate without running Marvin  
**Mitigation**: XML schema validation + basic checks  
**Status**: 🟡 Moderate

---

## Integration with Phase 2

### Workflow: Minion → Marvin

```bash
# Phase 2: Create Minion collectors
biff-cli collector create
# Output: MinionConfig.xml with collectors

# Phase 3: Discover data sources
biff-marvin discover-sources MinionConfig.xml
# Output: List of available metrics

# Phase 3: Create dashboard
biff-marvin dashboard create --template cpu_monitoring --source MinionConfig.xml
# Output: App.Config.xml + tab files + widget configs

# Run BIFF stack
./start_oscar.sh
./start_minion.sh -c MinionConfig.xml
./start_marvin.sh -c App.Config.xml
```

**Seamless Integration**: Data sources from Phase 2 automatically available in Phase 3

---

## Metrics & ROI

### Development Estimate

- **Week 8**: Widget builders (5 days × 3.5 hours = 17.5 hours)
- **Week 9**: Layout & dashboards (5 days × 3.5 hours = 17.5 hours)
- **Week 10**: Polish & docs (5 days × 3.5 hours = 17.5 hours)
- **Total**: 52.5 hours

### Expected Time Savings

**Intel Vision Demo** (100 widgets, 5 tabs):
- **Manual**: ~20 hours (widget config + layout + testing)
- **Automated**: ~2 hours (run wizards + customize)
- **Savings**: 18 hours (90% reduction)

**Break-Even**: ~3 deployments (similar to Phase 2)

---

## Deliverables Summary

### Code (estimated ~4,000 LOC)

1. Widget builders (8 types): ~1,800 LOC
2. Layout builders: ~900 LOC
3. Dashboard templates: ~600 LOC
4. Utilities (discovery, validation): ~400 LOC
5. Tests: ~800 LOC

### Documentation (~2,000 LOC)

1. Marvin Composer User Guide
2. Widget Reference
3. Dashboard Templates Guide
4. Phase 3 completion docs

### Templates

1. 5+ dashboard templates
2. 10+ widget presets
3. 3+ style themes

---

## Next Steps

### Immediate (Week 8 Day 1)

1. Create `biff_agents_marvin` package structure
2. Implement base `WidgetBuilder` class
3. Create `MinionDataSourceDiscovery` utility
4. Write first test

### Week 8 Plan

**Day 1**: Foundation + Text/LED builders  
**Day 2**: Gauge builders (8 variants)  
**Day 3**: Chart builders  
**Day 4**: Integration testing  
**Day 5**: Documentation + polish

---

## Questions to Resolve

1. **Widget Priority**: Which 10 widgets to implement first?
   - Recommendation: Text, LED, Gauge (3 variants), LineChart, BarChart, Button, Image

2. **Layout Strategy**: Auto-layout vs manual positioning?
   - Recommendation: Both - auto for quick start, manual for precision

3. **Style Management**: CSS files vs inline styles?
   - Recommendation: Both - templates use CSS, customization via inline

4. **Validation Depth**: Basic XML vs full Marvin validation?
   - Recommendation: Basic + common errors (missing data sources, invalid ranges)

---

## Status: 🎯 READY TO START

**Phase**: 3  
**Week**: 8  
**Day**: 1  
**Next**: Create base widget builder and discover data sources

Let's build the Marvin GUI Composer! 🚀
