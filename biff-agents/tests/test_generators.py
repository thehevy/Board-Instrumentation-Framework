"""Unit tests for Minion and Oscar config generators"""
import unittest
import tempfile
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET

from biff_agents_core.generators.minion_generator import MinionConfigGenerator
from biff_agents_core.generators.oscar_generator import OscarConfigGenerator


class TestMinionConfigGenerator(unittest.TestCase):
    """Test cases for MinionConfigGenerator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = MinionConfigGenerator()
        self.test_config = {
            "minion_namespace": "TestNamespace",
            "collectors": ["RandomVal", "Timer"],
            "oscar_ip": "localhost",
            "oscar_port": 1100,
            "use_existing": False
        }
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up temp directory"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_generate_basic_config(self):
        """Test generating basic Minion config"""
        xml_string = self.generator.generate(self.test_config)
        
        # Parse XML to verify structure
        root = ET.fromstring(xml_string)
        
        # Check root element
        self.assertEqual(root.tag, "Minion")
        
        # Check namespace
        namespace = root.find("Namespace")
        self.assertIsNotNone(namespace)
        
        # Check namespace name
        name = namespace.find("Name")
        self.assertEqual(name.text, "TestNamespace")
        
        # Check target connection
        target = namespace.find("TargetConnection")
        self.assertEqual(target.get("IP"), "localhost")
        self.assertEqual(target.get("PORT"), "1100")
        
        # Check collectors
        collectors = namespace.findall("Collector")
        self.assertEqual(len(collectors), 2)
    
    def test_generate_with_existing_biff(self):
        """Test generating config with existing BIFF installation"""
        config = self.test_config.copy()
        config["use_existing"] = True
        config["biff_root"] = "D:/github/Board-Instrumentation-Framework"
        
        xml_string = self.generator.generate(config)
        
        # Should include absolute paths to collectors
        self.assertIn("Board-Instrumentation-Framework", xml_string)
        self.assertIn("Minion", xml_string)
    
    def test_generate_file(self):
        """Test writing config to file"""
        file_path = self.generator.generate_file(self.test_config, self.temp_dir)
        
        # Check file exists
        self.assertTrue(file_path.exists())
        self.assertEqual(file_path.name, "MinionConfig.xml")
        
        # Parse and verify
        tree = ET.parse(file_path)
        root = tree.getroot()
        self.assertEqual(root.tag, "Minion")
    
    def test_unknown_collector(self):
        """Test handling unknown collector"""
        config = self.test_config.copy()
        config["collectors"] = ["UnknownCollector"]
        
        xml_string = self.generator.generate(config)
        
        # Should include comment about unknown collector
        self.assertIn("Unknown collector", xml_string)
    
    def test_get_available_collectors(self):
        """Test getting list of available collectors"""
        collectors = MinionConfigGenerator.get_available_collectors()
        
        self.assertIn("RandomVal", collectors)
        self.assertIn("Timer", collectors)
        self.assertIn("CPU", collectors)
        self.assertGreater(len(collectors), 3)
    
    def test_collector_description(self):
        """Test getting collector description"""
        desc = MinionConfigGenerator.get_collector_description("RandomVal")
        self.assertIn("Random value", desc)
        
        unknown = MinionConfigGenerator.get_collector_description("Unknown")
        self.assertEqual(unknown, "Unknown collector")


class TestOscarConfigGenerator(unittest.TestCase):
    """Test cases for OscarConfigGenerator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = OscarConfigGenerator()
        self.test_config = {
            "oscar_ip": "localhost",
            "oscar_port": 1100,
            "marvin_port": 52001,
            "minion_namespace": "TestNamespace"
        }
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up temp directory"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_generate_basic_config(self):
        """Test generating basic Oscar config"""
        xml_string = self.generator.generate(self.test_config)
        
        # Parse XML to verify structure
        root = ET.fromstring(xml_string)
        
        # Check root element
        self.assertEqual(root.tag, "Oscar")
        self.assertEqual(root.get("ID"), "QuickStart")
        
        # Check incoming Minion connection
        incoming = root.find("IncomingMinionConnection")
        self.assertIsNotNone(incoming)
        self.assertEqual(incoming.get("PORT"), "1100")
        
        # Check target connection (to Marvin)
        target = root.find("TargetConnection")
        self.assertIsNotNone(target)
        self.assertEqual(target.get("IP"), "localhost")
        self.assertEqual(target.get("PORT"), "52001")
    
    def test_generate_remote_config(self):
        """Test generating config for remote deployment"""
        config = self.test_config.copy()
        config["oscar_ip"] = "192.168.1.100"
        
        xml_string = self.generator.generate(config)
        
        # Should use specified IP
        self.assertIn("192.168.1.100", xml_string)
    
    def test_generate_file(self):
        """Test writing config to file"""
        file_path = self.generator.generate_file(self.test_config, self.temp_dir)
        
        # Check file exists
        self.assertTrue(file_path.exists())
        self.assertEqual(file_path.name, "OscarConfig.xml")
        
        # Parse and verify
        tree = ET.parse(file_path)
        root = tree.getroot()
        self.assertEqual(root.tag, "Oscar")
    
    def test_namespace_comment(self):
        """Test namespace routing comment"""
        config = self.test_config.copy()
        config["minion_namespace"] = "CustomNamespace"
        
        xml_string = self.generator.generate(config)
        
        # Should include comment about namespace
        self.assertIn("CustomNamespace", xml_string)


if __name__ == '__main__':
    unittest.main()
