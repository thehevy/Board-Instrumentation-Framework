# What's Next - Phase 3 Week 8 Day 4

**Current Status**: Day 3 Complete (60% Week 8)  
**Next Sprint**: Day 4 - Additional Widgets + Performance Composer  
**Estimated Time**: 3 hours

---

## 🎯 Day 4 Objectives

### 1. MemoryWidgetBuilder (200 LOC, 45 min)

**Purpose**: Memory bar charts with zones

**Implementation**:
```python
# File: biff_agents_marvin/builders/memory_widget_builder.py

class MemoryWidgetBuilder(WidgetBuilder):
    def build_widget(self):
        # Interactive wizard:
        # 1. Select memory data source
        # 2. Set range (auto: 0-100%)
        # 3. Configure zones (Green 0-70%, Yellow 70-90%, Red 90-100%)
        # 4. Set position (4-column grid)
        # 5. Choose display format (bar chart, radial, text)
        
        # Generate XML:
        # - <Widget Type="MemoryWidget">
        # - <MinionSrc Namespace="..." ID="..."/>
        # - <Zones> with color ranges
        # - Grid position attributes
```

**Test**:
```python
def test_memory_widget_builder():
    # Create builder
    # Test with memory.percent source
    # Verify XML structure
    # Check zone defaults
```

---

### 2. NetworkWidgetBuilder (180 LOC, 40 min)

**Purpose**: Network throughput displays

**Implementation**:
```python
# File: biff_agents_marvin/builders/network_widget_builder.py

class NetworkWidgetBuilder(WidgetBuilder):
    def build_widget(self):
        # Interactive wizard:
        # 1. Select network data source
        # 2. Set units (auto: Mbps)
        # 3. Configure history size (default: 100)
        # 4. Set position
        # 5. Choose display (line chart, bar, text)
        
        # Generate XML:
        # - <Widget Type="LineChart"> (for throughput)
        # - <MinionSrc Namespace="..." ID="..."/>
        # - Auto-scale enabled
        # - ShowLegend="true"
```

**Test**:
```python
def test_network_widget_builder():
    # Create builder
    # Test with network.throughput source
    # Verify chart XML
    # Check unit detection (Mbps)
```

---

### 3. SystemWidgetBuilder (150 LOC, 30 min)

**Purpose**: System info panels (multi-line text)

**Implementation**:
```python
# File: biff_agents_marvin/builders/system_widget_builder.py

class SystemWidgetBuilder(WidgetBuilder):
    def build_widget(self):
        # Interactive wizard:
        # 1. Select system data sources (can select multiple)
        # 2. Configure layout (vertical stack)
        # 3. Set font size
        # 4. Set position
        
        # Generate XML:
        # - <Widget Type="Text"> with multiple <MinionSrc>
        # - Multi-line layout
        # - System info formatting
```

**Test**:
```python
def test_system_widget_builder():
    # Create builder
    # Test with system.info source
    # Verify multi-line text XML
```

---

### 4. PerformanceDashboardComposer (220 LOC, 55 min)

**Purpose**: Performance-focused 2-tab layout

**Implementation**:
```python
# File: biff_agents_marvin/composers/performance_composer.py

class PerformanceDashboardComposer(DashboardComposer):
    def generate_dashboard(self, output_dir):
        # Tab 1: System Overview
        #   - CPU gauges (2x2 each)
        #   - Memory bar charts
        #   - System info panel (4x2)
        
        # Tab 2: Network Performance
        #   - Network throughput charts (4x2 each)
        #   - Status LEDs for interfaces
        
        # Generate:
        #   - App.Config.xml (2 tabs)
        #   - Tab.System.xml
        #   - Tab.Network.xml
```

**Layout Algorithm**:
```
Tab 1 (System Overview):
Row 0: [CPU Gauge 2x2] [Memory Bar 2x2]
Row 2: [System Info Panel 4x2      ]

Tab 2 (Network Performance):
Row 0: [Network Chart 4x2           ]
Row 2: [Network Chart 4x2           ]
Row 4: [LED] [LED] [LED] [LED]
```

**Test**:
```python
def test_performance_dashboard_composer():
    # Create composer
    # Generate dashboard
    # Verify 3 files (App.Config + 2 tabs)
    # Check widget types per tab
    # Verify layout correctness
```

---

### 5. CLI Integration (10 min)

**Update**: `biff_agents_marvin/cli.py`

```python
# Add imports
from .builders.memory_widget_builder import MemoryWidgetBuilder
from .builders.network_widget_builder import NetworkWidgetBuilder
from .builders.system_widget_builder import SystemWidgetBuilder
from .composers.performance_composer import PerformanceDashboardComposer

# Register in widget_builders dict
widget_builders = {
    'text': TextWidgetBuilder,
    'led': LEDWidgetBuilder,
    'gauge': GaugeWidgetBuilder,
    'chart': ChartWidgetBuilder,
    'memory': MemoryWidgetBuilder,      # NEW
    'network': NetworkWidgetBuilder,    # NEW
    'system': SystemWidgetBuilder       # NEW
}

# Register in composers dict
composers = {
    'quickstart': QuickstartDashboardComposer,
    'monitoring': MonitoringDashboardComposer,
    'performance': PerformanceDashboardComposer  # NEW
}
```

---

### 6. Test Suite Updates (120 LOC, 30 min)

**Update**: `tests/test_marvin_composer.py`

Add 3 new tests:
```python
def test_memory_widget_builder():
    # Test memory widget generation
    pass

def test_network_widget_builder():
    # Test network widget generation
    pass

def test_system_widget_builder():
    # Test system info widget generation
    pass

def test_performance_dashboard_composer():
    # Test performance dashboard generation
    # Verify 3 files, 2 tabs, correct widget types
    pass
```

Update main():
```python
def main():
    # ... existing tests ...
    test_memory_widget_builder()
    test_network_widget_builder()
    test_system_widget_builder()
    test_performance_dashboard_composer()
    # Expected: 13/13 tests passing
```

---

## 📊 Expected Outcomes

### Code Volume
```
MemoryWidgetBuilder:           200 LOC
NetworkWidgetBuilder:          180 LOC
SystemWidgetBuilder:           150 LOC
PerformanceDashboardComposer:  220 LOC
Tests:                         120 LOC
CLI Updates:                    30 LOC
------------------------------------------
Total:                         900 LOC
```

### Test Results
```
Previous: 9/9 tests passing
New tests: +4
Expected: 13/13 tests passing (100%)
```

### Features Added
```
Widget Types:   7 total (was 4)
  - Text ✅
  - LED ✅
  - Gauge ✅
  - Chart ✅
  - Memory 🆕
  - Network 🆕
  - System 🆕

Dashboard Templates:  3 total (was 2)
  - Quickstart ✅
  - Monitoring ✅
  - Performance 🆕
```

---

## 🚀 Testing Plan

### Unit Tests
```bash
# Run test suite
python tests/test_marvin_composer.py

# Expected output:
# ✅ PASS Data Source Discovery
# ✅ PASS Text Widget Builder
# ✅ PASS LED Widget Builder
# ✅ PASS Gauge Widget Builder
# ✅ PASS Chart Widget Builder
# ✅ PASS Memory Widget Builder (NEW)
# ✅ PASS Network Widget Builder (NEW)
# ✅ PASS System Widget Builder (NEW)
# ✅ PASS Quickstart Dashboard
# ✅ PASS Monitoring Dashboard
# ✅ PASS Performance Dashboard (NEW)
# ✅ PASS Smart Unit Detection
# ✅ PASS Smart Range Detection
# 
# Results: 13/13 tests passed (100%)
```

### Integration Tests
```bash
# Test CLI commands
python -m biff_agents_marvin widget memory -c quickstart_configs/MinionConfig.xml
python -m biff_agents_marvin widget network -c quickstart_configs/MinionConfig.xml
python -m biff_agents_marvin widget system -c quickstart_configs/MinionConfig.xml
python -m biff_agents_marvin dashboard performance -c quickstart_configs/MinionConfig.xml

# Expected: All commands work, generate valid XML
```

---

## 📝 Documentation Updates

### Update Files
1. **README.md**
   - Update widget count: 4 → 7
   - Update dashboard count: 2 → 3
   - Update Phase 3 progress: 60% → 80% (Week 8)

2. **PHASE3_WEEK8_DAY4_COMPLETE.md** (NEW)
   - Day 4 completion report
   - Implementation details
   - Test results
   - Examples

3. **PROJECT_STATUS.md**
   - Update progress metrics
   - Update code volume
   - Update next steps

---

## ⏱️ Time Breakdown

```
Task                              Estimated    Priority
----------------------------------------------------------
MemoryWidgetBuilder                  45 min    HIGH
NetworkWidgetBuilder                 40 min    HIGH
SystemWidgetBuilder                  30 min    MEDIUM
PerformanceDashboardComposer         55 min    HIGH
CLI Integration                      10 min    HIGH
Test Suite Updates                   30 min    HIGH
Documentation                        30 min    MEDIUM
----------------------------------------------------------
Total:                              3h 30min
```

---

## ✅ Success Criteria

### Must Have
- ✅ MemoryWidgetBuilder implemented and tested
- ✅ NetworkWidgetBuilder implemented and tested
- ✅ SystemWidgetBuilder implemented and tested
- ✅ PerformanceDashboardComposer implemented and tested
- ✅ 13/13 tests passing (100%)
- ✅ CLI integration complete
- ✅ Zero bugs

### Nice to Have
- ⭐ Additional widget styles
- ⭐ More layout options
- ⭐ Extended smart defaults

---

## 🎯 After Day 4

### Completion Status
- **Week 8**: 80% complete (4/5 days)
- **Phase 3**: 19.5% complete (10.5/52.5 hours)

### Next Steps (Day 5)
1. Widget styling system (CSS generation)
2. Theme support (dark, light, corporate)
3. Color palette configuration
4. Font customization
5. Week 8 completion document
6. Total tests: 15 (target)

---

**Ready to Start**: Day 4 implementation  
**Estimated Completion**: 3 hours  
**Expected Outcome**: 7 widget types, 3 dashboard templates, 13/13 tests passing
