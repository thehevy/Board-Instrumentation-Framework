"""Unit tests for Marvin application generator"""
import unittest
import tempfile
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET

from biff_agents_core.generators.marvin_generator import MarvinApplicationGenerator


class TestMarvinApplicationGenerator(unittest.TestCase):
    """Test cases for MarvinApplicationGenerator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = MarvinApplicationGenerator()
        self.test_config = {
            "minion_namespace": "TestNamespace",
            "collectors": ["RandomVal", "Timer", "CPU"],
            "marvin_port": 52001,
            "use_existing": False
        }
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up temp directory"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_generate_application(self):
        """Test generating Application.xml"""
        xml_string = self.generator.generate_application(self.test_config)
        
        # Parse XML to verify structure
        root = ET.fromstring(xml_string)
        
        # Check root element
        self.assertEqual(root.tag, "Marvin")
        
        # Check application
        app = root.find("Application")
        self.assertIsNotNone(app)
        self.assertEqual(app.get("Scale"), "auto")
        
        # Check creation size
        size = app.find("CreationSize")
        self.assertIsNotNone(size)
        self.assertEqual(size.get("Width"), "$(WindowWidth)")
        self.assertEqual(size.get("Height"), "$(WindowHeight)")
        
        # Check network port
        network = app.find("Network")
        self.assertIsNotNone(network)
        self.assertEqual(network.get("Port"), "$(MarvinPort)")
        
        # Check title
        title = app.find("Title")
        self.assertIn("$(MinionNamespace)", title.text)
        
        # Check tabs
        tabs = app.find("Tabs")
        self.assertIsNotNone(tabs)
        tab = tabs.find("Tab")
        self.assertEqual(tab.get("ID"), "Tab.QuickStart")
    
    def test_generate_tab(self):
        """Test generating Tab.QuickStart.xml"""
        xml_string = self.generator.generate_tab(self.test_config)
        
        # Parse XML
        root = ET.fromstring(xml_string)
        
        # Check root
        self.assertEqual(root.tag, "MarvinExternalFile")
        
        # Check tab
        tab = root.find("Tab")
        self.assertIsNotNone(tab)
        
        # Check title
        title = tab.find("Title")
        self.assertIn("$(MinionNamespace)", title.text)
        
        # Check grid reference
        grid = tab.find("Grid")
        self.assertIsNotNone(grid)
        self.assertEqual(grid.get("File"), "Grid.QuickStart.xml")
    
    def test_generate_grid(self):
        """Test generating Grid.QuickStart.xml"""
        xml_string = self.generator.generate_grid(self.test_config)
        
        # Parse XML
        root = ET.fromstring(xml_string)
        
        # Check root
        self.assertEqual(root.tag, "MarvinExternalFile")
        
        # Check grid
        grid = root.find("Grid")
        self.assertIsNotNone(grid)
        
        # Check widgets (3 collectors = 3 widgets)
        widgets = grid.findall("Widget")
        self.assertEqual(len(widgets), 3)
        
        # Verify widget structure
        for widget in widgets:
            self.assertIsNotNone(widget.get("row"))
            self.assertIsNotNone(widget.get("column"))
            self.assertIsNotNone(widget.get("File"))
            
            # Check MinionSrc
            minion_src = widget.find("MinionSrc")
            self.assertIsNotNone(minion_src)
            self.assertEqual(minion_src.get("Namespace"), "$(MinionNamespace)")
            self.assertIsNotNone(minion_src.get("ID"))
    
    def test_widget_layout(self):
        """Test widget grid layout (3 columns max)"""
        config = self.test_config.copy()
        config["collectors"] = ["RandomVal", "Timer", "CPU", "Memory", "Network"]
        
        xml_string = self.generator.generate_grid(config)
        root = ET.fromstring(xml_string)
        grid = root.find("Grid")
        widgets = grid.findall("Widget")
        
        # Should have 5 widgets
        self.assertEqual(len(widgets), 5)
        
        # Check positions (3 col layout)
        # Row 1: col 1,2,3
        # Row 2: col 1,2
        positions = [(w.get("row"), w.get("column")) for w in widgets]
        expected = [("1", "1"), ("1", "2"), ("1", "3"), ("2", "1"), ("2", "2")]
        self.assertEqual(positions, expected)
    
    def test_gauge_widget_properties(self):
        """Test gauge widgets reference the correct definition file

        Gauge properties (min/max/decimals/unit) now live in the widget
        definition files (Widget/Gauge/*.xml), not inline in the grid.
        """
        config = self.test_config.copy()
        config["collectors"] = ["CPU"]
        
        xml_string = self.generator.generate_grid(config)
        root = ET.fromstring(xml_string)
        
        widget = root.find(".//Widget")
        
        # CPU gauge references the radial gauge definition file
        self.assertEqual(widget.get("File"), "Gauge/GaugeRadial.xml")
        
        # Data source binds to the CPU collector
        minion_src = widget.find("MinionSrc")
        self.assertEqual(minion_src.get("ID"), "cpu.value")
        
        # Inline gauge properties are no longer emitted in the grid
        self.assertIsNone(widget.find("MinValue"))
        self.assertIsNone(widget.find("MaxValue"))
        self.assertIsNone(widget.find("Decimals"))
        self.assertIsNone(widget.find("UnitText"))
    
    def test_text_widget_properties(self):
        """Test text widgets have initial value"""
        config = self.test_config.copy()
        config["collectors"] = ["Memory"]
        
        xml_string = self.generator.generate_grid(config)
        root = ET.fromstring(xml_string)
        
        widget = root.find(".//Widget")
        
        # Text widget should have initial value
        initial = widget.find("InitialValue")
        self.assertEqual(initial.text, "Waiting for data...")
    
    def test_unknown_collector(self):
        """Test handling unknown collector"""
        config = self.test_config.copy()
        config["collectors"] = ["UnknownCollector"]
        
        xml_string = self.generator.generate_grid(config)
        
        # Should include comment about unknown collector
        self.assertIn("Unknown collector", xml_string)
    
    def test_generate_all_files(self):
        """Test generating all files at once"""
        files = self.generator.generate_all(self.test_config, self.temp_dir)
        
        # Should return dict with 4 files (aliases + application + tab + grid)
        self.assertEqual(len(files), 4)
        self.assertIn('aliases', files)
        self.assertIn('application', files)
        self.assertIn('tab', files)
        self.assertIn('grid', files)
        
        # All files should exist
        self.assertTrue(files['aliases'].exists())
        self.assertTrue(files['application'].exists())
        self.assertTrue(files['tab'].exists())
        self.assertTrue(files['grid'].exists())
        
        # Check filenames
        self.assertEqual(files['application'].name, "Application.xml")
        self.assertEqual(files['tab'].name, "Tab.QuickStart.xml")
        self.assertEqual(files['grid'].name, "Grid.QuickStart.xml")
    
    def test_application_custom_port(self):
        """Test custom Marvin port is captured in the alias definitions"""
        config = self.test_config.copy()
        config["marvin_port"] = 53001
        
        # Application references the port via an alias placeholder
        app_xml = self.generator.generate_application(config)
        app_root = ET.fromstring(app_xml)
        network = app_root.find(".//Network")
        self.assertEqual(network.get("Port"), "$(MarvinPort)")
        
        # The actual port value lives in the generated Aliases.xml
        aliases_xml = self.generator.generate_aliases(config)
        aliases_root = ET.fromstring(aliases_xml)
        aliases = {}
        for alias in aliases_root.findall("Alias"):
            aliases.update(alias.attrib)
        self.assertEqual(aliases.get("MarvinPort"), "53001")
    
    def test_collector_id_format(self):
        """Test collector IDs are lowercase with .value suffix"""
        xml_string = self.generator.generate_grid(self.test_config)
        root = ET.fromstring(xml_string)
        
        # Check MinionSrc IDs
        minion_srcs = root.findall(".//MinionSrc")
        ids = [src.get("ID") for src in minion_srcs]
        
        # Should be lowercase with .value suffix
        expected = ["randomval.value", "timer.value", "cpu.value"]
        self.assertEqual(ids, expected)
    
    def test_widget_file_references(self):
        """Test widget file paths are correct"""
        xml_string = self.generator.generate_grid(self.test_config)
        root = ET.fromstring(xml_string)
        
        widgets = root.findall(".//Widget")
        files = [w.get("File") for w in widgets]
        
        # Should reference correct widget files
        self.assertIn("Gauge/GaugeSimple.xml", files)
        self.assertIn("Gauge/GaugeRadial.xml", files)


if __name__ == '__main__':
    unittest.main()
