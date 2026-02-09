"""
Tests for Marvin GUI Composer - Phase 3 Week 8 Day 1

Validates:
- Data source discovery
- Widget builders (Text, LED)
- CLI integration
"""

import sys
from pathlib import Path
from io import StringIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from biff_agents_marvin.utils.minion_discovery import MinionDataSourceDiscovery, DataSource
from biff_agents_marvin.builders.text_widget_builder import TextWidgetBuilder
from biff_agents_marvin.builders.led_widget_builder import LEDWidgetBuilder
from biff_agents_marvin.builders.button_widget_builder import ButtonWidgetBuilder
from biff_agents_marvin.builders.gauge_widget_builder import GaugeWidgetBuilder
from biff_agents_marvin.builders.chart_widget_builder import ChartWidgetBuilder
from biff_agents_marvin.builders.memory_widget_builder import MemoryWidgetBuilder
from biff_agents_marvin.builders.network_widget_builder import NetworkWidgetBuilder
from biff_agents_marvin.builders.system_widget_builder import SystemWidgetBuilder
from biff_agents_marvin.composers.quickstart_composer import QuickstartDashboardComposer
from biff_agents_marvin.composers.monitoring_composer import MonitoringDashboardComposer
from biff_agents_marvin.composers.performance_composer import PerformanceDashboardComposer


def test_data_source_discovery():
    """Test data source discovery from MinionConfig.xml"""
    print("\n" + "=" * 70)
    print("TEST 1: Data Source Discovery")
    print("=" * 70)
    
    config_path = Path("quickstart_configs/MinionConfig.xml")
    if not config_path.exists():
        print(f"❌ SKIP: Config not found at {config_path}")
        return False
    
    try:
        discovery = MinionDataSourceDiscovery(config_path)
        sources = discovery.discover()
        
        print(f"✅ Discovered {len(sources)} data sources")
        
        # Validate sources
        if len(sources) < 2:
            print(f"❌ FAIL: Expected at least 2 sources, got {len(sources)}")
            return False
        
        # Check source properties
        for source in sources:
            print(f"   • {source.namespace}:{source.collector_id}")
            if source.suggested_unit:
                print(f"     Unit: {source.suggested_unit}")
            
            # Validate DataSource attributes
            assert isinstance(source, DataSource)
            assert source.namespace
            assert source.collector_id
            assert source.source_type in ['collector', 'plugin', 'dynamic']
        
        # Test search
        search_results = discovery.search("cpu")
        print(f"✅ Search 'cpu': {len(search_results)} results")
        
        print("✅ PASS: Data source discovery working")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_text_widget_builder():
    """Test text widget builder XML generation"""
    print("\n" + "=" * 70)
    print("TEST 2: Text Widget Builder")
    print("=" * 70)
    
    config_path = Path("quickstart_configs/MinionConfig.xml")
    if not config_path.exists():
        print(f"❌ SKIP: Config not found at {config_path}")
        return False
    
    try:
        builder = TextWidgetBuilder(config_path)
        
        # Mock user input by setting attributes directly
        # This simulates the wizard flow without interactive prompts
        test_config = {
            'title': 'Test Display',
            'source': builder.discovery.discover()[0],  # First source
            'units': '%',
            'font_size': '1.5em',
            'alignment': 'Center',
            'row': 1,
            'column': 1,
            'col_span': 1,
            'row_span': 1
        }
        
        # Generate XML directly
        xml = builder._generate_xml(test_config)
        
        # Validate XML structure
        assert '<Widget File="Text/Text.xml"' in xml
        assert '<Title>Test Display</Title>' in xml
        assert '<MinionSrc' in xml
        assert 'Namespace=' in xml
        assert 'ID=' in xml
        assert '<Suffix> %</Suffix>' in xml
        
        print("✅ Generated valid text widget XML")
        print(f"   Lines: {len(xml.splitlines())}")
        
        # Check for proper XML structure
        if xml.startswith('<?xml version='):
            print("✅ XML declaration present")
        if '<!--' in xml:
            print("✅ XML comment present")
        
        print("✅ PASS: Text widget builder working")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_led_widget_builder():
    """Test LED widget builder XML generation"""
    print("\n" + "=" * 70)
    print("TEST 3: LED Widget Builder")
    print("=" * 70)
    
    config_path = Path("quickstart_configs/MinionConfig.xml")
    if not config_path.exists():
        print(f"❌ SKIP: Config not found at {config_path}")
        return False
    
    try:
        builder = LEDWidgetBuilder(config_path)
        
        # Mock configuration
        test_config = {
            'title': 'Status LED',
            'source': builder.discovery.discover()[0],
            'condition_type': '>',
            'condition_value': '50',
            'color': 'Green',
            'size': '24',
            'row': 1,
            'column': 1
        }
        
        # Generate XML
        xml = builder._generate_xml(test_config)
        
        # Validate structure
        assert '<Widget File="LED/LED.xml"' in xml
        assert '<Title>Status LED</Title>' in xml
        assert '<OnCondition>&gt;50</OnCondition>' in xml
        assert '<Color>Green</Color>' in xml
        assert '<Height>24</Height>' in xml
        assert '<Width>24</Width>' in xml
        
        print("✅ Generated valid LED widget XML")
        print(f"   Lines: {len(xml.splitlines())}")
        print("✅ Condition properly escaped (&gt; for >)")
        
        print("✅ PASS: LED widget builder working")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_button_widget_builder():
    """Test button widget builder XML generation"""
    print("\n" + "=" * 70)
    print("TEST 4: Button Widget Builder")
    print("=" * 70)
    
    config_path = Path("quickstart_configs/MinionConfig.xml")
    if not config_path.exists():
        print(f"❌ SKIP: Config not found at {config_path}")
        return False
    
    try:
        builder = ButtonWidgetBuilder(str(config_path))
        
        # Simulate user input: label, style=1 (standard), action=1 (minion task), 
        # custom actor, params, no custom colors, width/height, position
        # Button label, style, action, namespace, actor_id, params, width, height, colors, row, col
        inputs = "Restart\n1\n1\nMyNamespace\nrestart\nforce=true\n2\n1\nn\n0\n0\n"
        sys.stdin = StringIO(inputs)
        
        xml = builder.build_widget()
        sys.stdin = sys.__stdin__
        
        if not xml:
            print("❌ FAIL: No XML generated")
            return False
        
        print(f"✅ Generated valid button widget XML")
        print(f"   Lines: {len(xml.splitlines())}")
        
        # Validate XML structure
        if '<Widget File="Button/' not in xml:
            print("❌ FAIL: Missing Widget element")
            return False
        
        if '<Title>Restart</Title>' not in xml:
            print("❌ FAIL: Missing title")
            return False
        
        if '<Task Type="MinionTaskLauncher"' not in xml:
            print("❌ FAIL: Missing task element")
            return False
        
        if '<Namespace>MyNamespace</Namespace>' not in xml:
            print("❌ FAIL: Missing namespace")
            return False
        
        print("✅ Task configuration present")
        print("✅ PASS: Button widget builder working")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gauge_widget_builder():
    """Test gauge widget builder XML generation"""
    print("\n" + "=" * 70)
    print("TEST 6: Gauge Widget Builder")
    print("=" * 70)
    
    config_path = Path("quickstart_configs/MinionConfig.xml")
    if not config_path.exists():
        print(f"❌ SKIP: Config not found at {config_path}")
        return False
    
    try:
        builder = GaugeWidgetBuilder(config_path)
        
        # Mock configuration
        test_config = {
            'title': 'CPU Gauge',
            'source': builder.discovery.discover()[0],
            'min_value': '0',
            'max_value': '100',
            'units': '%',
            'major_ticks': '10',
            'zones': [
                {'start': 0.0, 'end': 70.0, 'color': 'rgb(0, 255, 0)'},
                {'start': 70.0, 'end': 90.0, 'color': 'rgb(255, 255, 0)'},
                {'start': 90.0, 'end': 100.0, 'color': 'rgb(255, 0, 0)'}
            ],
            'gauge_file': 'Gauge/Radial1Horizontal.xml',
            'row': 1,
            'column': 1,
            'col_span': 2,
            'row_span': 2
        }
        
        # Generate XML
        xml = builder._generate_xml(test_config)
        
        # Validate structure
        assert '<Widget File="Gauge/Radial1Horizontal.xml"' in xml
        assert '<Title>CPU Gauge</Title>' in xml
        assert '<MinValue>0</MinValue>' in xml
        assert '<MaxValue>100</MaxValue>' in xml
        assert '<UnitsOverride>%</UnitsOverride>' in xml
        assert '<MajorTicks>10</MajorTicks>' in xml
        assert '<Zones>' in xml
        assert '<Zone>' in xml
        assert 'rgb(0, 255, 0)' in xml  # Green zone
        assert 'rgb(255, 255, 0)' in xml  # Yellow zone
        assert 'rgb(255, 0, 0)' in xml  # Red zone
        
        print("✅ Generated valid gauge widget XML")
        print(f"   Lines: {len(xml.splitlines())}")
        print("✅ Color zones present (3 zones)")
        print("✅ Range and units configured")
        
        print("✅ PASS: Gauge widget builder working")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chart_widget_builder():
    """Test chart widget builder XML generation"""
    print("\n" + "=" * 70)
    print("TEST 7: Chart Widget Builder")
    print("=" * 70)
    
    config_path = Path("quickstart_configs/MinionConfig.xml")
    if not config_path.exists():
        print(f"❌ SKIP: Config not found at {config_path}")
        return False
    
    try:
        builder = ChartWidgetBuilder(config_path)
        
        # Mock configuration
        sources = builder.discovery.discover()
        test_config = {
            'title': 'System Metrics',
            'chart_file': 'Chart/LineChart.xml',
            'chart_type': 'Line Chart',
            'series': [
                {
                    'source': sources[0],
                    'label': 'CPU',
                    'color': '#0000FF'
                },
                {
                    'source': sources[1],
                    'label': 'Memory',
                    'color': '#00FF00'
                }
            ],
            'history_seconds': '60',
            'auto_scale': True,
            'show_legend': True,
            'row': 2,
            'column': 1,
            'col_span': 4,
            'row_span': 2
        }
        
        # Generate XML
        xml = builder._generate_xml(test_config)
        
        # Validate structure
        assert '<Widget File="Chart/LineChart.xml"' in xml
        assert '<Title>System Metrics</Title>' in xml
        assert '<xAxisLabel>Time</xAxisLabel>' in xml
        assert '<HistorySize>60</HistorySize>' in xml
        assert '<ShowLegend>true</ShowLegend>' in xml
        assert '<Series>' in xml
        assert '<SeriesSet>' in xml
        assert '<Title>CPU</Title>' in xml
        assert '<Title>Memory</Title>' in xml
        assert '<Color>#0000FF</Color>' in xml
        assert '<Color>#00FF00</Color>' in xml
        
        print("✅ Generated valid chart widget XML")
        print(f"   Lines: {len(xml.splitlines())}")
        print("✅ Multiple series (2 series)")
        print("✅ Legend and time axis configured")
        
        print("✅ PASS: Chart widget builder working")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quickstart_dashboard_composer():
    """Test quickstart dashboard composer"""
    print("\n" + "=" * 70)
    print("TEST 8: Quickstart Dashboard Composer")
    print("=" * 70)
    
    config_path = Path("quickstart_configs/MinionConfig.xml")
    if not config_path.exists():
        print(f"❌ SKIP: Config not found at {config_path}")
        return False
    
    try:
        composer = QuickstartDashboardComposer(config_path)
        
        # Generate dashboard
        output_dir = Path("test_output_quickstart")
        files = composer.generate_dashboard(output_dir)
        
        # Validate files
        assert 'App.Config.xml' in files
        assert 'Tab.Overview.xml' in files
        
        # Check App.Config.xml structure
        app_config = files['App.Config.xml']
        assert '<Application>' in app_config
        assert '<Title>BIFF Quickstart Dashboard</Title>' in app_config
        assert '<OscarConnection' in app_config
        assert '<Tab File="Tab.Overview.xml">' in app_config
        
        # Check Tab.Overview.xml structure
        tab_content = files['Tab.Overview.xml']
        assert '<Tab>' in tab_content
        assert '<Grid columns="4">' in tab_content
        assert '<Widget' in tab_content
        assert 'Gauge/Radial1Horizontal.xml' in tab_content
        assert '<MinionSrc' in tab_content
        
        print(f"✅ Generated {len(files)} files")
        print("✅ App.Config.xml structure valid")
        print("✅ Tab.Overview.xml with gauges")
        
        # Clean up
        import shutil
        if output_dir.exists():
            shutil.rmtree(output_dir)
        
        print("✅ PASS: Quickstart dashboard composer working")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_monitoring_dashboard_composer():
    """Test monitoring dashboard composer"""
    print("\n" + "=" * 70)
    print("TEST 9: Monitoring Dashboard Composer")
    print("=" * 70)
    
    config_path = Path("quickstart_configs/MinionConfig.xml")
    if not config_path.exists():
        print(f"❌ SKIP: Config not found at {config_path}")
        return False
    
    try:
        composer = MonitoringDashboardComposer(config_path)
        
        # Generate dashboard
        output_dir = Path("test_output_monitoring")
        files = composer.generate_dashboard(output_dir)
        
        # Validate files
        assert 'App.Config.xml' in files
        assert 'Tab.Overview.xml' in files
        assert 'Tab.Details.xml' in files
        assert 'Tab.Status.xml' in files
        
        # Check App.Config.xml has 3 tabs
        app_config = files['App.Config.xml']
        assert '<Title>BIFF Monitoring Dashboard</Title>' in app_config
        assert app_config.count('<Tab File=') == 3
        assert 'Tab.Overview.xml' in app_config
        assert 'Tab.Details.xml' in app_config
        assert 'Tab.Status.xml' in app_config
        
        # Check Overview tab has gauges
        overview = files['Tab.Overview.xml']
        assert 'Gauge/Radial1Horizontal.xml' in overview
        
        # Check Details tab has charts
        details = files['Tab.Details.xml']
        assert 'Chart/LineChart.xml' in details
        assert '<Series>' in details
        
        # Check Status tab has LEDs
        status = files['Tab.Status.xml']
        assert 'LED/LED.xml' in status
        assert '<OnCondition>' in status
        
        print(f"✅ Generated {len(files)} files (3 tabs + config)")
        print("✅ Overview tab with gauges")
        print("✅ Details tab with charts")
        print("✅ Status tab with LEDs")
        
        # Clean up
        import shutil
        if output_dir.exists():
            shutil.rmtree(output_dir)
        
        print("✅ PASS: Monitoring dashboard composer working")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_smart_unit_detection():
    """Test smart unit detection in DataSource"""
    print("\n" + "=" * 70)
    print("TEST 4: Smart Unit Detection")
    print("=" * 70)
    
    test_cases = [
        ('cpu.usage', '%'),
        ('temp.value', '°C'),
        ('memory.bytes', 'MB'),
        ('network.speed', 'Mbps'),
        ('cpu.freq', 'MHz'),
        ('unknown.metric', ''),  # No suggestion
    ]
    
    passed = 0
    failed = 0
    
    for collector_id, expected_unit in test_cases:
        source = DataSource(
            namespace='Test',
            collector_id=collector_id,
            description='Test source',
            source_type='collector'
        )
        
        actual_unit = source.suggested_unit
        
        if actual_unit == expected_unit:
            print(f"✅ {collector_id:20s} → {actual_unit or '(none)':10s}")
            passed += 1
        else:
            print(f"❌ {collector_id:20s} → Expected '{expected_unit}', got '{actual_unit}'")
            failed += 1
    
    if failed == 0:
        print(f"✅ PASS: All {passed} unit detection tests passed")
        return True
    else:
        print(f"❌ FAIL: {failed} tests failed, {passed} passed")
        return False


def test_range_detection():
    """Test smart range detection in DataSource"""
    print("\n" + "=" * 70)
    print("TEST 5: Smart Range Detection")
    print("=" * 70)
    
    test_cases = [
        ('cpu.usage', (0, 100)),
        ('temp.value', (0, 120)),
        ('memory.percent', (0, 100)),
        ('cpu.freq', (800, 5000)),
        ('unknown', (None, None)),  # No suggestion
    ]
    
    passed = 0
    failed = 0
    
    for collector_id, expected_range in test_cases:
        source = DataSource(
            namespace='Test',
            collector_id=collector_id,
            description='Test source',
            source_type='collector'
        )
        
        actual_range = source.suggested_min_max
        
        if actual_range == expected_range:
            if expected_range[0] is not None:
                print(f"✅ {collector_id:20s} → {expected_range[0]:.0f} - {expected_range[1]:.0f}")
            else:
                print(f"✅ {collector_id:20s} → (no suggestion)")
            passed += 1
        else:
            print(f"❌ {collector_id:20s} → Expected {expected_range}, got {actual_range}")
            failed += 1
    
    if failed == 0:
        print(f"✅ PASS: All {passed} range detection tests passed")
        return True
    else:
        print(f"❌ FAIL: {failed} tests failed, {passed} passed")
        return False


def test_memory_widget_builder():
    """Test memory widget builder"""
    print("\n" + "=" * 70)
    print("TEST 10: Memory Widget Builder")
    print("=" * 70)
    
    config_path = Path("quickstart_configs/MinionConfig.xml")
    if not config_path.exists():
        print(f"❌ SKIP: Config not found")
        return False
    
    try:
        builder = MemoryWidgetBuilder(str(config_path))
        
        # Simulate user input: select first source, bar style, defaults for range (no suggestion), unit, position
        # Inputs: source=1, style=1 (bar), min=Enter (0), max=Enter (100), units=MB, row=0, col=0, width=4, height=1
        inputs = "1\n1\n\n\nMB\nY\n0\n0\n4\n1\n"
        sys.stdin = StringIO(inputs)
        
        xml = builder.build_widget()
        sys.stdin = sys.__stdin__
        
        if not xml:
            print("❌ FAIL: No XML generated")
            return False
        
        print(f"✅ Generated valid memory widget XML")
        print(f"   Lines: {len(xml.splitlines())}")
        
        # Validate XML structure
        if 'Widget Type="ProgressBar"' not in xml and 'Widget Type="Gauge"' not in xml:
            print("❌ FAIL: Missing Widget element")
            return False
        
        if '<MinionSrc' not in xml:
            print("❌ FAIL: Missing MinionSrc element")
            return False
        
        print("✅ PASS: Memory widget builder working")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_network_widget_builder():
    """Test network widget builder"""
    print("\n" + "=" * 70)
    print("TEST 11: Network Widget Builder")
    print("=" * 70)
    
    config_path = Path("quickstart_configs/MinionConfig.xml")
    if not config_path.exists():
        print(f"❌ SKIP: Config not found")
        return False
    
    try:
        builder = NetworkWidgetBuilder(str(config_path))
        
        # Simulate user input: select first source, chart style, units=Mbps, history=Enter, auto-scale=Y, position defaults
        inputs = "1\n1\nMbps\n\nY\n0\n0\n4\n2\n"
        sys.stdin = StringIO(inputs)
        
        xml = builder.build_widget()
        sys.stdin = sys.__stdin__
        
        if not xml:
            print("❌ FAIL: No XML generated")
            return False
        
        print(f"✅ Generated valid network widget XML")
        print(f"   Lines: {len(xml.splitlines())}")
        
        # Validate XML structure
        if '<Widget Type="LineChart"' not in xml and '<Widget Type="Gauge"' not in xml:
            print("❌ FAIL: Missing Widget element")
            return False
        
        if '<MinionSrc' not in xml:
            print("❌ FAIL: Missing MinionSrc element")
            return False
        
        print("✅ PASS: Network widget builder working")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_system_widget_builder():
    """Test system widget builder"""
    print("\n" + "=" * 70)
    print("TEST 12: System Widget Builder")
    print("=" * 70)
    
    config_path = Path("quickstart_configs/MinionConfig.xml")
    if not config_path.exists():
        print(f"❌ SKIP: Config not found")
        return False
    
    try:
        builder = SystemWidgetBuilder(str(config_path))
        
        # Simulate user input: select first 2 sources (default), default title, medium font, default position
        inputs = "\n\n2\n0\n0\n4\n2\n"
        sys.stdin = StringIO(inputs)
        
        xml = builder.build_widget()
        sys.stdin = sys.__stdin__
        
        if not xml:
            print("❌ FAIL: No XML generated")
            return False
        
        print(f"✅ Generated valid system widget XML")
        print(f"   Lines: {len(xml.splitlines())}")
        
        # Validate XML structure
        if '<Widget Type="Text"' not in xml:
            print("❌ FAIL: Missing Text widget element")
            return False
        
        if '<MinionSrc' not in xml:
            print("❌ FAIL: Missing MinionSrc element")
            return False
        
        if '<MultiLine>true</MultiLine>' not in xml:
            print("❌ FAIL: Missing MultiLine element")
            return False
        
        print("✅ PASS: System widget builder working")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance_dashboard_composer():
    """Test performance dashboard composer"""
    print("\n" + "=" * 70)
    print("TEST 13: Performance Dashboard Composer")
    print("=" * 70)
    
    config_path = Path("quickstart_configs/MinionConfig.xml")
    if not config_path.exists():
        print(f"❌ SKIP: Config not found")
        return False
    
    import shutil
    output_dir = Path("test_performance_dashboard")
    
    try:
        # Clean up from previous test
        if output_dir.exists():
            shutil.rmtree(output_dir)
        
        composer = PerformanceDashboardComposer(str(config_path))
        result = composer.generate_dashboard(str(output_dir))
        
        if not result:
            print("❌ FAIL: No dashboard generated")
            return False
        
        # Check files exist
        app_config = output_dir / 'App.Config.xml'
        tab_system = output_dir / 'Tab.System.xml'
        
        if not app_config.exists():
            print("❌ FAIL: App.Config.xml not found")
            return False
        
        if not tab_system.exists():
            print("❌ FAIL: Tab.System.xml not found")
            return False
        
        print(f"✅ Generated {len(result.get('tabs', [])) + 1} files")
        
        # Validate App.Config.xml structure
        app_xml = app_config.read_text(encoding='utf-8')
        if '<Application' not in app_xml:
            print("❌ FAIL: Missing Application element")
            return False
        
        if '<Tab File="Tab.System.xml"' not in app_xml:
            print("❌ FAIL: Missing System tab reference")
            return False
        
        print("✅ App.Config.xml structure valid")
        
        # Validate Tab.System.xml
        tab_xml = tab_system.read_text(encoding='utf-8')
        if not ('<Tab ' in tab_xml or '<Tab>' in tab_xml):
            print("❌ FAIL: Missing Tab element in System tab")
            return False
        
        # Should have gauges or bars or text widgets
        has_widgets = ('<Widget Type="Gauge"' in tab_xml or 
                      '<Widget Type="ProgressBar"' in tab_xml or
                      '<Widget Type="Text"' in tab_xml)
        if not has_widgets:
            print("❌ FAIL: No widgets in System tab")
            return False
        
        print("✅ Tab.System.xml with widgets")
        print("✅ PASS: Performance dashboard composer working")
        
        # Clean up
        shutil.rmtree(output_dir)
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        if output_dir.exists():
            shutil.rmtree(output_dir)
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("BIFF Agents - Marvin GUI Composer Test Suite")
    print("Phase 3 Week 8 Day 5")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Data Source Discovery", test_data_source_discovery()))
    results.append(("Text Widget Builder", test_text_widget_builder()))
    results.append(("LED Widget Builder", test_led_widget_builder()))
    results.append(("Button Widget Builder", test_button_widget_builder()))
    results.append(("Gauge Widget Builder", test_gauge_widget_builder()))
    results.append(("Chart Widget Builder", test_chart_widget_builder()))
    results.append(("Memory Widget Builder", test_memory_widget_builder()))
    results.append(("Network Widget Builder", test_network_widget_builder()))
    results.append(("System Widget Builder", test_system_widget_builder()))
    results.append(("Quickstart Dashboard", test_quickstart_dashboard_composer()))
    results.append(("Monitoring Dashboard", test_monitoring_dashboard_composer()))
    results.append(("Performance Dashboard", test_performance_dashboard_composer()))
    results.append(("Smart Unit Detection", test_smart_unit_detection()))
    results.append(("Smart Range Detection", test_range_detection()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10s} {test_name}")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 70)
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
