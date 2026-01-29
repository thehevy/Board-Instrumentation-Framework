# Marvin GUI Composer Agent - Detailed Specification

## Executive Summary

The Marvin GUI Composer Agent democratizes BIFF's powerful visualization capabilities by transforming the complex task of creating XML-based dashboards into an intuitive guided experience. It bridges the gap between having data collectors running and actually seeing meaningful visualizations, making Marvin's 40+ widget types accessible to users unfamiliar with XML configuration.

**Target Time Savings**: 75% reduction in dashboard creation time (15 min vs 60 min)
**Primary Value**: Production-ready dashboards without deep XML knowledge

---

## User Personas

### Primary: First-Time Dashboard Creator

- **Background**: Has working Minion/Oscar, wants to visualize data
- **Pain Points**:
  - Overwhelmed by 40+ widget types
  - Doesn't understand Grid positioning (row/column/span)
  - Unsure how to bind widgets to collectors (MinionSrc)
  - XML syntax unfamiliar
  - Tab/Grid hierarchy confusing
- **Success Metric**: Working dashboard with 5+ widgets in 15 minutes

### Secondary: Dashboard Designer

- **Background**: Creating custom dashboards for specific use cases
- **Goal**: Professional-looking layouts with proper styling
- **Pain Points**:
  - CSS styling is trial-and-error
  - Widget sizing and alignment tricky
  - Alias system powerful but confusing
  - Reusable components need DefinitionFiles
- **Success Metric**: Beautiful, maintainable dashboard with parameterized widgets

### Tertiary: Enterprise Dashboard Architect

- **Background**: Building dashboard templates for teams
- **Goal**: Standardized dashboards that can be replicated
- **Pain Points**:
  - Need conditional widgets based on data availability
  - Multi-namespace dashboards complex
  - Dynamic grids for auto-discovered metrics
  - Performance optimization (too many widgets)
- **Success Metric**: Scalable dashboard architecture deployed across organization

---

## Marvin GUI Architecture Context

### Application Structure

```
Marvin Application
├── Application Settings (title, size, Oscar connection)
├── TabPane (container for tabs)
│   ├── Tab 1 (e.g., "System Overview")
│   │   └── Grid (layout container)
│   │       ├── GridPos row="0" column="0" → Widget A
│   │       ├── GridPos row="0" column="1" → Widget B
│   │       └── GridPos row="1" column="0" columnspan="2" → Widget C
│   ├── Tab 2 (e.g., "Network Stats")
│   │   └── Grid (different layout)
│   └── Tab 3...
└── AliasList (shared variables)
```

### Widget Binding Model

```xml
<!-- Widget must bind to collector via MinionSrc -->
<Gauge>
    <Title>CPU Usage</Title>
    <MinionSrc Namespace="SystemMetrics" ID="cpu.usage"/>
    <!-- ↑ Must match collector in MinionConfig.xml:
         <Namespace><Name>SystemMetrics</Name>
         <Collector ID="cpu.usage">... -->
</Gauge>
```

### Grid Positioning System

```
Grid with 3 columns:
┌─────────────┬─────────────┬─────────────┐
│ row=0 col=0 │ row=0 col=1 │ row=0 col=2 │
│  Widget A   │  Widget B   │  Widget C   │
├─────────────┴─────────────┼─────────────┤
│ row=1 col=0 columnspan=2  │ row=1 col=2 │
│      Wide Widget D         │  Widget E   │
└───────────────────────────┴─────────────┘
```

---

## Agent Capabilities

### 0. Advanced Widget Creators

#### Remote Control Button Creator

```python
class RemoteControlCreator:
    """Create buttons that trigger remote Minion Actors"""
    
    def create_remote_control_button(self):
        print("\n🎛️ Remote Control Button Creator")
        print("Create button that executes commands on remote systems\n")
        
        button_title = input("Button title: ")
        actor_namespace = input("Target Minion namespace: ")
        actor_id = input("Actor ID to execute: ")
        
        # Parameters?
        use_params = input("\nDoes actor need parameters? [y/N]: ")
        
        param_widgets = ""
        param_refs = ""
        
        if use_params.lower() == 'y':
            params = []
            print("\nDefine parameters:")
            while True:
                param_name = input(f"  Parameter {len(params) + 1} (or Enter to finish): ")
                if not param_name:
                    break
                params.append(param_name)
            
            # Generate input widgets for parameters
            param_widgets = "\n".join([
                f'''<Widget File="Widget/Text.xml" row="{i}" column="0">
    <Title>{param}:</Title>
</Widget>
<Widget File="Widget/TextInput.xml" row="{i}" column="1">
    <MinionSrc Namespace="ControlPanel" ID="{param}" />
</Widget>'''
                for i, param in enumerate(params)
            ])
            
            # Generate parameter references for task
            param_refs = "\n".join([
                f'        <Param>%(ControlPanel,{param})</Param>'
                for param in params
            ])
        
        # Generate complete control panel
        control_panel_xml = f"""<Grid>
    <Title>{button_title} Control</Title>
    
{param_widgets}
    
    <Widget File="Button.xml" Task="Execute_{actor_id}">
        <Title>{button_title}</Title>
    </Widget>
</Grid>

<TaskList ID="Execute_{actor_id}">
    <TaskItem Type="Minion">
        <Actor Namespace="{actor_namespace}" ID="{actor_id}" />
{param_refs}
    </TaskItem>
</TaskList>"""
        
        print(f"\n✓ Created remote control button")
        print(control_panel_xml)
        
        return control_panel_xml
```

#### Multi-Deployment Tab Generator

```python
class MultiDeploymentComposer:
    """Create dashboards comparing multiple deployments side-by-side"""
    
    def create_comparison_dashboard(self):
        print("\n🏗️ Multi-Deployment Dashboard Creator")
        print("Compare multiple environments in one view\n")
        
        # Collect deployment info
        deployments = []
        print("Define deployments to compare:")
        while True:
            name = input(f"\nDeployment {len(deployments) + 1} name (or Enter to finish): ")
            if not name:
                break
            namespace = input(f"  Namespace: ")
            description = input(f"  Description: ")
            deployments.append({
                "name": name,
                "namespace": namespace,
                "description": description
            })
        
        # Generate tab definitions
        tabs_xml = "\n".join([
            f'        <Tab ID="Tab.{dep["name"]}" />'
            for dep in deployments
        ])
        
        tab_defs_xml = "\n".join([
            f'''    <Tab ID="Tab.{dep["name"]}" TabTitle="{dep["description"]}" 
         File="$(AppDir)/Tab.Deployment.xml" 
         Namespace="{dep["namespace"]}" 
         Deployment="{dep["name"]}"/>'''
            for dep in deployments
        ])
        
        marvin_config = f"""<Marvin>
    <Application Scale="auto" mode="debug">
        <CreationSize Width="1920" Height="1080" />
        <Title>Multi-Deployment Comparison</Title>
        
        <Tabs>
{tabs_xml}
        </Tabs>
    </Application>
    
{tab_defs_xml}
    
    <AliasList>
        <Alias AppDir="Demo" />
    </AliasList>
</Marvin>"""
        
        print(f"\n✓ Created multi-deployment dashboard with {len(deployments)} environments")
        print(marvin_config)
        
        # Generate reusable Tab.Deployment.xml template
        tab_template = """<MarvinExternalFile>
    <!-- Parameterized via Namespace and Deployment aliases -->
    <Grid>
        <!-- Add widgets that bind to $(Namespace) here -->
        <GridPos row="0" column="0">
            <Text>
                <Title>Deployment: $(Deployment)</Title>
            </Text>
        </GridPos>
    </Grid>
</MarvinExternalFile>"""
        
        print("\n📄 Tab.Deployment.xml (reusable template):")
        print(tab_template)
        
        return {"marvin_config": marvin_config, "tab_template": tab_template}
```

---

### 1. Dashboard Design Wizard

#### Layout Selection

```python
class DashboardWizard:
    TEMPLATES = {
        "monitoring_wall": {
            "description": "Full-screen dashboard with large widgets",
            "use_case": "NOC displays, server monitoring",
            "layout": "3x2 grid of large gauges/charts",
            "tabs": 1,
            "widget_count": 6
        },
        "system_overview": {
            "description": "Multi-tab dashboard for different metrics",
            "use_case": "Comprehensive system monitoring",
            "layout": "Tabs for CPU, Memory, Network, Disk",
            "tabs": 4,
            "widget_count": 16
        },
        "application_dashboard": {
            "description": "Application-specific metrics",
            "use_case": "Application performance monitoring",
            "layout": "Tabs for different services/components",
            "tabs": 3,
            "widget_count": 12
        },
        "executive_summary": {
            "description": "High-level KPIs and status",
            "use_case": "Management overview",
            "layout": "Large KPI numbers with trend charts",
            "tabs": 1,
            "widget_count": 8
        },
        "blank_canvas": {
            "description": "Start from scratch",
            "use_case": "Custom dashboard",
            "layout": "You design the layout",
            "tabs": 1,
            "widget_count": 0
        }
    }
    
    def start_wizard(self):
        """Interactive dashboard creation"""
        
        # Step 1: Choose template
        template = self.select_template()
        
        # Step 2: Discover available collectors
        collectors = self.discover_collectors()
        
        # Step 3: Map collectors to widgets
        widget_mappings = self.map_collectors_to_widgets(collectors)
        
        # Step 4: Customize layout
        layout = self.customize_layout(template, widget_mappings)
        
        # Step 5: Generate files
        return self.generate_dashboard(layout)
```

#### Conversation Flow

```
Agent: Let's create your Marvin dashboard! First, I need to understand what you're monitoring.

Looking at your Minion configuration...
Found collectors in namespace "SystemMetrics":
  - cpu.usage
  - memory.used_percent
  - disk.root.usage
  - network.eth0.rx_bytes
  - network.eth0.tx_bytes

What type of dashboard would you like?

1) Monitoring Wall - Large widgets for NOC display
2) System Overview - Tabbed dashboard with organized metrics
3) Application Dashboard - Focus on application performance
4) Executive Summary - High-level KPIs
5) Custom - Build from scratch

User: 2

Agent: Great! System Overview dashboard. I'll suggest tabs based on your metrics:

Suggested tabs:
  Tab 1: "System Resources" (CPU, Memory, Disk)
  Tab 2: "Network" (Bandwidth, Packets)
  
Does this work, or would you like different organization?

User: that works

Agent: Perfect! Now let's choose widgets for each metric.

Tab 1: System Resources
--------------------
For "cpu.usage" (0-100%), I recommend:
  1) Gauge - Classic circular gauge
  2) Bar Gauge - Horizontal bar
  3) LCD Display - Digital readout
  4) Line Chart - Historical trend

User: 1

Agent: Gauge selected for CPU.

For "memory.used_percent" (0-100%), I recommend:
  [same options...]

User: 1

Agent: For "disk.root.usage" (0-100%):
  [same options...]

User: 2

Agent: Tab 2: Network
--------------------
For "network.eth0.rx_bytes" (continuously increasing):
  1) Text Display - Current value
  2) Line Chart - Historical trend
  3) Area Chart - Filled trend
  4) LED - On/off indicator (not suitable for this metric)

User: 2

[continues for all metrics...]

Agent: Excellent! Generating your dashboard...

✓ Created: Marvin/MyDashboard.xml (application config)
✓ Created: Marvin/Grid_SystemResources.xml
✓ Created: Marvin/Grid_Network.xml

Dashboard configured for:
  - Window size: 1920x1080
  - Oscar connection: localhost:52001
  - 2 tabs with 5 widgets total

To launch:
  cd Marvin
  java -jar BIFF.Marvin.jar -a MyDashboard.xml

Would you like to customize styles or add more widgets?
```

---

### 2. Widget Recommendation Engine

#### Smart Widget Selection

```python
class WidgetRecommender:
    def recommend_widget_type(self, collector_spec):
        """Recommend widget based on metric characteristics"""
        
        metric_type = self.analyze_metric_type(collector_spec)
        
        recommendations = {
            "percentage": {
                "primary": ["Gauge", "BarGauge"],
                "secondary": ["LCD", "LED"],
                "explanation": "Percentage metrics (0-100) work well with gauges"
            },
            "absolute_bounded": {
                "primary": ["Gauge", "BarGauge"],
                "secondary": ["Text", "LCD"],
                "explanation": "Bounded values (min/max known) suit gauges"
            },
            "absolute_unbounded": {
                "primary": ["Text", "LineChart"],
                "secondary": ["LCD"],
                "explanation": "Unbounded values best displayed as text or trends"
            },
            "counter": {
                "primary": ["LineChart", "AreaChart"],
                "secondary": ["Text"],
                "explanation": "Counters should show trends, not current value"
            },
            "rate": {
                "primary": ["LineChart", "AreaChart", "BarChart"],
                "secondary": ["Gauge"],
                "explanation": "Rates (per second) best shown as trends"
            },
            "boolean": {
                "primary": ["LED", "Indicator"],
                "secondary": ["Text"],
                "explanation": "Binary states suit LED or indicator widgets"
            },
            "text": {
                "primary": ["Text"],
                "secondary": [],
                "explanation": "Text data requires Text widget"
            }
        }
        
        return recommendations[metric_type]
    
    def analyze_metric_type(self, collector_spec):
        """Determine metric characteristics from collector"""
        
        # Check collector ID for hints
        id_lower = collector_spec["id"].lower()
        
        if "percent" in id_lower or "usage" in id_lower:
            return "percentage"
        elif "bytes" in id_lower or "packets" in id_lower:
            return "counter"
        elif "rate" in id_lower or "per_sec" in id_lower:
            return "rate"
        elif "status" in id_lower or "state" in id_lower:
            return "boolean"
        else:
            # Check if collector has min/max defined
            if "min_value" in collector_spec and "max_value" in collector_spec:
                return "absolute_bounded"
            else:
                return "absolute_unbounded"
```

#### Widget Configuration Builder

```python
class WidgetConfigBuilder:
    def build_gauge_config(self, collector, position):
        """Generate Gauge widget configuration"""
        
        config = {
            "type": "Gauge",
            "title": self.generate_title(collector["id"]),
            "position": position,
            "minion_src": {
                "namespace": collector["namespace"],
                "id": collector["id"]
            },
            "min_value": collector.get("min_value", 0),
            "max_value": collector.get("max_value", 100),
            "unit": collector.get("unit", ""),
            "decimals": collector.get("decimals", 1),
            "thresholds": self.generate_thresholds(collector)
        }
        
        return config
    
    def generate_title(self, metric_id):
        """Convert metric ID to friendly title"""
        # "cpu.core0.usage" → "CPU Core 0 Usage"
        parts = metric_id.split(".")
        return " ".join(word.capitalize() for word in parts)
    
    def generate_thresholds(self, collector):
        """Smart threshold generation based on metric type"""
        
        if "usage" in collector["id"] or "percent" in collector["id"]:
            return [
                {"value": 80, "color": "yellow", "label": "Warning"},
                {"value": 90, "color": "red", "label": "Critical"}
            ]
        else:
            return []
```

---

### 3. Layout Manager

#### Grid Builder

```python
class GridLayoutBuilder:
    def build_grid(self, widgets, layout_style="balanced"):
        """Arrange widgets in grid layout"""
        
        if layout_style == "balanced":
            return self.balanced_layout(widgets)
        elif layout_style == "priority":
            return self.priority_layout(widgets)
        elif layout_style == "compact":
            return self.compact_layout(widgets)
    
    def balanced_layout(self, widgets):
        """Equal-sized widgets in rows"""
        
        # Determine grid dimensions
        widget_count = len(widgets)
        columns = min(3, widget_count)  # Max 3 columns
        rows = (widget_count + columns - 1) // columns
        
        positions = []
        for idx, widget in enumerate(widgets):
            row = idx // columns
            col = idx % columns
            
            positions.append({
                "widget": widget,
                "row": row,
                "column": col,
                "rowspan": 1,
                "columnspan": 1
            })
        
        return GridLayout(positions, rows, columns)
    
    def priority_layout(self, widgets):
        """Primary widgets larger, secondary smaller"""
        
        # First widget gets top full width
        # Remaining widgets in 2-column grid below
        
        positions = []
        
        # Primary widget (row 0, full width)
        positions.append({
            "widget": widgets[0],
            "row": 0,
            "column": 0,
            "rowspan": 1,
            "columnspan": 2
        })
        
        # Secondary widgets (2 columns)
        for idx, widget in enumerate(widgets[1:], 1):
            row = 1 + (idx - 1) // 2
            col = (idx - 1) % 2
            
            positions.append({
                "widget": widget,
                "row": row,
                "column": col,
                "rowspan": 1,
                "columnspan": 1
            })
        
        return GridLayout(positions, rows=1 + len(widgets[1:])//2, columns=2)
```

#### XML Generation

```python
class GridXMLGenerator:
    def generate_grid_xml(self, layout, namespace_aliases):
        """Convert layout to Grid XML"""
        
        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_parts.append('<MarvinExternalFile>')
        
        # Add aliases
        if namespace_aliases:
            xml_parts.append('    <AliasList>')
            for alias, value in namespace_aliases.items():
                xml_parts.append(f'        <Alias {alias}="{value}"/>')
            xml_parts.append('    </AliasList>')
        
        # Add grid container
        xml_parts.append('    <Grid Align="Center" hgap="10" vgap="10">')
        
        # Add widgets
        for position in layout.positions:
            widget = position["widget"]
            
            # GridPos
            gridpos_attrs = [
                f'row="{position["row"]}"',
                f'column="{position["column"]}"'
            ]
            if position["rowspan"] > 1:
                gridpos_attrs.append(f'rowspan="{position["rowspan"]}"')
            if position["columnspan"] > 1:
                gridpos_attrs.append(f'columnspan="{position["columnspan"]}"')
            
            xml_parts.append(f'        <GridPos {" ".join(gridpos_attrs)}>')
            
            # Widget
            widget_xml = self.generate_widget_xml(widget)
            for line in widget_xml.split('\n'):
                xml_parts.append('            ' + line)
            
            xml_parts.append('        </GridPos>')
        
        xml_parts.append('    </Grid>')
        xml_parts.append('</MarvinExternalFile>')
        
        return '\n'.join(xml_parts)
    
    def generate_widget_xml(self, widget_config):
        """Generate XML for specific widget type"""
        
        if widget_config["type"] == "Gauge":
            return self.generate_gauge_xml(widget_config)
        elif widget_config["type"] == "LineChart":
            return self.generate_linechart_xml(widget_config)
        # ... other widget types
```

---

### 4. Widget Gallery & Examples

#### Interactive Widget Browser

```python
class WidgetGallery:
    WIDGETS = {
        "Gauge": {
            "description": "Circular gauge with needle, ranges 0-100 or custom",
            "best_for": ["Percentages", "Bounded metrics", "Temperature", "Pressure"],
            "variations": ["Gauge", "GaugeRadial", "GaugeRadialSteel", "GaugeSimple"],
            "example_screenshot": "Widget/Gauge/Gauge.png",
            "example_xml": "Widget/Gauge/Gauge.xml",
            "complexity": "Low"
        },
        "BarGauge": {
            "description": "Horizontal or vertical bar gauge",
            "best_for": ["Percentages", "Progress indicators", "Capacity"],
            "variations": ["GaugeBar", "GaugeDoubleBar"],
            "example_xml": "Widget/Gauge/GaugeBar.xml",
            "complexity": "Low"
        },
        "LineChart": {
            "description": "Time-series line chart, shows historical data",
            "best_for": ["Trends", "Rates", "Counters", "Performance over time"],
            "variations": ["LineChart", "AreaChart", "StackedAreaChart"],
            "example_xml": "Widget/Chart/LineChart.xml",
            "complexity": "Medium"
        },
        "Text": {
            "description": "Simple text display with formatting",
            "best_for": ["Exact values", "Labels", "Status messages"],
            "variations": ["Text", "DynamicText"],
            "example_xml": "Widget/Text/Text.xml",
            "complexity": "Low"
        },
        "LED": {
            "description": "On/off indicator light",
            "best_for": ["Binary status", "Alerts", "Connection status"],
            "variations": ["LED", "Indicator"],
            "example_xml": "Widget/LED/LED.xml",
            "complexity": "Low"
        }
    }
    
    def browse_widgets(self, filter_by_use_case=None):
        """Interactive widget browsing"""
        
        if filter_by_use_case:
            filtered = {
                name: info 
                for name, info in self.WIDGETS.items()
                if filter_by_use_case.lower() in " ".join(info["best_for"]).lower()
            }
            return filtered
        
        return self.WIDGETS
    
    def show_widget_example(self, widget_type):
        """Display example configuration and preview"""
        
        widget_info = self.WIDGETS[widget_type]
        
        # Read example XML
        example_path = os.path.join(workspace_root, widget_info["example_xml"])
        with open(example_path) as f:
            example_xml = f.read()
        
        return {
            "description": widget_info["description"],
            "example_xml": example_xml,
            "screenshot": widget_info.get("example_screenshot"),
            "customization_hints": self.get_customization_hints(widget_type)
        }
```

---

### 5. Collector Discovery & Binding

#### Minion Config Parser

```python
class CollectorDiscovery:
    def discover_collectors(self, minion_config_path):
        """Extract all collectors from MinionConfig.xml"""
        
        tree = ET.parse(minion_config_path)
        root = tree.getroot()
        
        collectors = []
        
        for namespace in root.findall('.//Namespace'):
            ns_name = namespace.find('Name').text
            
            for collector in namespace.findall('.//Collector'):
                collector_id = collector.get('ID')
                frequency = collector.get('Frequency', '1000')
                
                collectors.append({
                    "namespace": ns_name,
                    "id": collector_id,
                    "frequency": frequency,
                    "full_id": f"{ns_name}:{collector_id}"
                })
        
        return collectors
    
    def suggest_bindings(self, collectors):
        """Suggest logical groupings for dashboard tabs"""
        
        # Group by namespace
        by_namespace = {}
        for collector in collectors:
            ns = collector["namespace"]
            if ns not in by_namespace:
                by_namespace[ns] = []
            by_namespace[ns].append(collector)
        
        # Group by metric category (from ID)
        by_category = {
            "cpu": [],
            "memory": [],
            "disk": [],
            "network": [],
            "application": [],
            "other": []
        }
        
        for collector in collectors:
            id_lower = collector["id"].lower()
            
            categorized = False
            for category in by_category.keys():
                if category in id_lower:
                    by_category[category].append(collector)
                    categorized = True
                    break
            
            if not categorized:
                by_category["other"].append(collector)
        
        return {
            "by_namespace": by_namespace,
            "by_category": by_category
        }
```

#### Automatic Binding Generation

```python
class BindingGenerator:
    def create_widget_binding(self, collector, widget_type):
        """Generate MinionSrc binding for widget"""
        
        binding = {
            "namespace": collector["namespace"],
            "id": collector["id"]
        }
        
        # Add widget-specific configurations
        if widget_type in ["Gauge", "BarGauge"]:
            binding.update(self.infer_gauge_params(collector))
        elif widget_type in ["LineChart", "AreaChart"]:
            binding.update(self.infer_chart_params(collector))
        
        return binding
    
    def infer_gauge_params(self, collector):
        """Infer min/max values from collector ID"""
        
        id_lower = collector["id"].lower()
        
        if "percent" in id_lower or "usage" in id_lower:
            return {"min_value": 0, "max_value": 100, "unit": "%"}
        elif "temperature" in id_lower:
            return {"min_value": 0, "max_value": 100, "unit": "°C"}
        else:
            return {"min_value": 0, "max_value": 100}
```

---

### 6. Style & Theme Customization

#### CSS Template Library

```python
class StyleManager:
    THEMES = {
        "default": {
            "description": "Clean, professional look",
            "css_file": "Widget/Modena-BIFF.css",
            "colors": {
                "background": "#2b2b2b",
                "text": "#ffffff",
                "accent": "#0096c9"
            }
        },
        "dark": {
            "description": "Dark theme for NOC displays",
            "css": """
                .root {
                    -fx-background-color: #1a1a1a;
                }
                .gauge {
                    -fx-needle-color: #00ff00;
                    -fx-bar-color: #00ff00;
                }
            """
        },
        "light": {
            "description": "Light, minimal theme",
            "css": """
                .root {
                    -fx-background-color: #f5f5f5;
                }
                .text {
                    -fx-text-fill: #333333;
                }
            """
        }
    }
    
    def apply_theme(self, theme_name, dashboard_config):
        """Apply CSS theme to dashboard"""
        
        theme = self.THEMES[theme_name]
        
        if "css_file" in theme:
            dashboard_config["css_file"] = theme["css_file"]
        elif "css" in theme:
            # Generate custom CSS file
            css_path = self.write_custom_css(theme["css"])
            dashboard_config["css_file"] = css_path
        
        return dashboard_config
```

#### Widget Size & Positioning Helper

```python
class LayoutHelper:
    STANDARD_SIZES = {
        "small": {"width": 200, "height": 200},
        "medium": {"width": 300, "height": 300},
        "large": {"width": 400, "height": 400},
        "wide": {"width": 600, "height": 300},
        "tall": {"width": 300, "height": 600}
    }
    
    def calculate_responsive_size(self, window_width, window_height, grid_layout):
        """Calculate widget sizes based on window and grid"""
        
        available_width = window_width - 40  # margins
        available_height = window_height - 100  # margins + title bar
        
        cell_width = available_width / grid_layout.columns
        cell_height = available_height / grid_layout.rows
        
        return {
            "cell_width": cell_width,
            "cell_height": cell_height
        }
```

---

### 7. Advanced Features

#### Alias System Integration

```python
class AliasManager:
    def generate_namespace_aliases(self, collectors):
        """Create aliases for repeated namespace names"""
        
        namespaces = set(c["namespace"] for c in collectors)
        
        aliases = {}
        for ns in namespaces:
            alias_name = f"NS_{ns.upper().replace('-', '_')}"
            aliases[alias_name] = ns
        
        return aliases
    
    def parameterize_widget_definition(self, widget_config):
        """Create reusable widget definition with alias parameters"""
        
        # Example: Create gauge definition file that takes parameters
        definition = {
            "file": f"Widget/Custom/{widget_config['title']}.xml",
            "aliases": {
                "NAMESPACE": widget_config["minion_src"]["namespace"],
                "METRIC_ID": widget_config["minion_src"]["id"],
                "TITLE": widget_config["title"]
            }
        }
        
        return definition
```

#### Multi-Source Widgets

```python
class MultiSourceWidgetBuilder:
    def build_multi_source_chart(self, collectors, chart_type="LineChart"):
        """Create chart with multiple data series"""
        
        chart_config = {
            "type": chart_type,
            "title": "Combined Metrics",
            "series": []
        }
        
        for collector in collectors:
            series = {
                "name": self.generate_series_name(collector["id"]),
                "namespace": collector["namespace"],
                "id": collector["id"]
            }
            chart_config["series"].append(series)
        
        return chart_config
    
    def generate_series_name(self, collector_id):
        """Convert collector ID to series label"""
        # "network.eth0.rx_bytes" → "eth0 RX"
        parts = collector_id.split(".")
        if len(parts) >= 2:
            return f"{parts[1]} {parts[2][:2].upper()}"
        return collector_id
```

---

## Example Generated Dashboard

### Application.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by Marvin GUI Composer Agent -->
<!-- Created: 2026-01-28 15:00:00 -->
<Marvin>
    <AliasList>
        <Alias NS_SYSTEM="SystemMetrics"/>
        <Alias NS_NETWORK="NetworkStats"/>
    </AliasList>
    
    <Application>
        <Title>System Monitoring Dashboard</Title>
        <Width>1920</Width>
        <Height>1080</Height>
        <OscarConnection IP="localhost" Port="52001"/>
    </Application>
    
    <TabPane side="top">
        <Tab Name="System Resources">
            <Grid File="Grid_SystemResources.xml"/>
        </Tab>
        
        <Tab Name="Network">
            <Grid File="Grid_Network.xml"/>
        </Tab>
    </TabPane>
</Marvin>
```

### Grid_SystemResources.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MarvinExternalFile>
    <AliasList>
        <Alias NS="SystemMetrics"/>
    </AliasList>
    
    <Grid Align="Center" hgap="10" vgap="10">
        <!-- Row 0: Title -->
        <GridPos row="0" column="0" columnspan="3">
            <Text>
                <Title>System Resources</Title>
                <FontSize>32</FontSize>
            </Text>
        </GridPos>
        
        <!-- Row 1: CPU, Memory, Disk -->
        <GridPos row="1" column="0">
            <Gauge>
                <Title>CPU Usage</Title>
                <Width>300</Width>
                <Height>300</Height>
                <MinionSrc Namespace="$(NS)" ID="cpu.usage"/>
                <MinValue>0</MinValue>
                <MaxValue>100</MaxValue>
                <Unit>%</Unit>
                <Decimals>1</Decimals>
            </Gauge>
        </GridPos>
        
        <GridPos row="1" column="1">
            <Gauge>
                <Title>Memory Usage</Title>
                <Width>300</Width>
                <Height>300</Height>
                <MinionSrc Namespace="$(NS)" ID="memory.used_percent"/>
                <MinValue>0</MinValue>
                <MaxValue>100</MaxValue>
                <Unit>%</Unit>
            </Gauge>
        </GridPos>
        
        <GridPos row="1" column="2">
            <GaugeBar>
                <Title>Disk Usage (/)</Title>
                <Width>300</Width>
                <Height>300</Height>
                <MinionSrc Namespace="$(NS)" ID="disk.root.usage"/>
                <MinValue>0</MinValue>
                <MaxValue>100</MaxValue>
                <Unit>%</Unit>
            </GaugeBar>
        </GridPos>
        
        <!-- Row 2: Trend chart spanning full width -->
        <GridPos row="2" column="0" columnspan="3">
            <LineChart>
                <Title>CPU & Memory Trends</Title>
                <Width>980</Width>
                <Height>300</Height>
                <MinionSrc Namespace="$(NS)" ID="cpu.usage"/>
                <MinionSrc Namespace="$(NS)" ID="memory.used_percent"/>
            </LineChart>
        </GridPos>
    </Grid>
</MarvinExternalFile>
```

---

## Interactive Workflow Example

```
Agent: I'll help you create a Marvin dashboard. Let me check your Minion configuration...

Found MinionConfig.xml with:
  Namespace "SystemMetrics":
    - cpu.usage
    - memory.used_percent
    - disk.root.usage
  Namespace "NetworkStats":
    - network.eth0.rx_bytes
    - network.eth0.tx_bytes
    - network.eth0.rx_packets

I can create a dashboard for these metrics. What layout style?

1) Monitoring Wall - All metrics on one screen
2) Organized Tabs - Separate tabs for System and Network
3) Custom - You decide

User: 2

Agent: Organized tabs selected. I'll create:
  - Tab 1: "System Resources" (CPU, Memory, Disk)
  - Tab 2: "Network" (Bandwidth, Packets)

For CPU usage (0-100%), which widget?
  → Gauge (recommended for percentages)
  → Bar Gauge
  → LCD Display

User: Gauge

Agent: For Memory usage (0-100%):
  → Gauge
  → Bar Gauge (recommended for capacity metrics)

User: Bar Gauge

Agent: For Disk usage (0-100%):
  → Gauge
  → Bar Gauge (recommended for capacity metrics)

User: Bar Gauge

Agent: Great! System tab widgets selected.

For network bandwidth (rx_bytes, tx_bytes), these are counters. Best visualized as:
  → Line Chart (recommended - shows trends)
  → Area Chart
  → Text (just shows current value)

User: Line Chart

Agent: Perfect! I'll create a combined chart showing both RX and TX.

Generating dashboard...

✓ Created: Marvin/MyDashboard.xml
✓ Created: Marvin/Grid_SystemResources.xml
✓ Created: Marvin/Grid_Network.xml

Dashboard summary:
  - Window: 1920x1080
  - Oscar: localhost:52001
  - Tabs: 2
  - Widgets: 6 total (3 system, 3 network)

To test:
  cd Marvin
  java -jar BIFF.Marvin.jar -a MyDashboard.xml

Would you like to:
  1) Customize colors/styling
  2) Add more widgets
  3) Adjust layout
  4) Preview widget examples
```

---

## Success Metrics

### Quantitative

- **Dashboard Creation Time**: < 15 minutes (vs. 60 minutes manual)
- **Widget Binding Accuracy**: 100% (namespace:ID validated against Minion config)
- **Layout Correctness**: No overlapping widgets, proper grid structure
- **Configuration Validity**: 100% valid XML on first generation

### Qualitative

- **User Confidence**: Non-XML users can create dashboards
- **Professional Quality**: Generated dashboards look polished
- **Maintainability**: Code is readable with comments and aliases
- **Reusability**: Can easily modify generated dashboards

---

## Implementation Phases

### Phase 1: Core Generation (Week 1)

- Collector discovery from Minion config
- Basic widget recommendation
- Simple grid layouts (balanced)
- Application.xml and Grid.xml generation

**Deliverable**: Can generate basic working dashboards with 5-10 widgets

### Phase 2: Enhanced Features (Week 2)

- Widget gallery browser
- Multiple layout styles
- Theme/CSS support
- Multi-tab dashboards
- Alias integration

**Deliverable**: Professional dashboards with custom styling

### Phase 3: Advanced Capabilities (Week 3)

- Multi-source charts
- Dynamic grids
- Widget definition files (reusable components)
- Conditional widgets
- Performance optimization

**Deliverable**: Enterprise-ready dashboard templates

---

## Integration Points

### With Quick Start Orchestrator

- Quick Start offers to create matching dashboard after setup

### With Collector Builder

- After creating collector, offer to add widget for it

### With Debugging Agent

- When validating namespace:ID, Debugging Agent uses GUI Composer's parser

---

## Example Success Story

> **Before GUI Composer Agent**:
> User spends 60 minutes studying Widget examples, copying XML, manually setting row/column positions, fixing syntax errors, adjusting sizing, and finally getting a basic 3-widget dashboard.

> **With GUI Composer Agent**:
>
> ```
> User: "Create dashboard for my collectors"
> Agent: [discovers 8 collectors]
> Agent: [asks 5 questions about layout preference]
> Agent: [generates complete dashboard in 2 minutes]
> User: [runs Marvin, sees professional dashboard]
> Total time: 8 minutes (including interaction)
> ```

**Result**: 85% time savings, production-quality output, user learns Marvin structure through generated examples.
