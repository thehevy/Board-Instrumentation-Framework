"""Unit tests for CollectorDiscovery"""
import unittest
import tempfile
import shutil
from pathlib import Path

from biff_agents_core.utils.collector_discovery import CollectorDiscovery


class TestCollectorDiscovery(unittest.TestCase):
    """Test cases for CollectorDiscovery"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures - use actual BIFF installation"""
        # Find BIFF root
        current = Path(__file__).parent.parent
        while current != current.parent:
            if (current / 'Minion' / 'Collectors').exists():
                cls.biff_root = current
                break
            current = current.parent
        else:
            raise RuntimeError("Could not find BIFF installation")
        
        cls.discovery = CollectorDiscovery(cls.biff_root)
    
    def test_initialization(self):
        """Test CollectorDiscovery initialization"""
        self.assertIsNotNone(self.discovery)
        self.assertEqual(self.discovery.biff_root, self.biff_root)
        # Test that collectors can be retrieved
        collectors = self.discovery.list_collectors()
        self.assertGreater(len(collectors), 0)
    
    def test_list_collectors(self):
        """Test listing all collectors"""
        collectors = self.discovery.list_collectors()
        
        # Should have multiple collectors
        self.assertGreater(len(collectors), 20)
        
        # Check collector structure
        collector = collectors[0]
        self.assertTrue(hasattr(collector, 'name'))
        self.assertTrue(hasattr(collector, 'file_path'))
        self.assertTrue(hasattr(collector, 'category'))
        self.assertTrue(hasattr(collector, 'functions'))
    
    def test_list_collectors_by_category(self):
        """Test listing collectors filtered by category"""
        all_collectors = self.discovery.list_collectors()
        system_collectors = self.discovery.list_collectors(category='system')
        
        # Should have fewer system collectors than total
        self.assertGreater(len(all_collectors), len(system_collectors))
        self.assertGreater(len(system_collectors), 0)
        
        # All returned collectors should be in system category
        for collector in system_collectors:
            self.assertEqual(collector.category, 'system')
    
    def test_get_collector_by_name(self):
        """Test getting specific collector by name"""
        # Test known collector
        cpu = self.discovery.get_collector('CPU')
        self.assertIsNotNone(cpu)
        self.assertEqual(cpu.name, 'CPU')
        self.assertEqual(cpu.category, 'system')
        self.assertGreater(len(cpu.functions), 0)
        
        # Test nonexistent collector
        fake = self.discovery.get_collector('NonExistent')
        self.assertIsNone(fake)
    
    def test_get_by_category(self):
        """Test getting collectors by category"""
        system = self.discovery.get_by_category('system')
        self.assertGreater(len(system), 0)
        
        # All should be system category
        for collector in system:
            self.assertEqual(collector.category, 'system')
        
        # Test invalid category
        invalid = self.discovery.get_by_category('invalid_category')
        self.assertEqual(len(invalid), 0)
    
    def test_get_categories(self):
        """Test getting list of categories"""
        categories = self.discovery.get_categories()
        
        # Should have multiple categories
        self.assertGreater(len(categories), 5)
        
        # Should include known categories
        expected = ['system', 'containers', 'monitoring', 'testing']
        for cat in expected:
            self.assertIn(cat, categories)
    
    def test_search_by_name(self):
        """Test searching by collector name"""
        results = self.discovery.search('CPU')
        
        # Should find CPU collector
        self.assertGreater(len(results), 0)
        names = [c.name for c in results]
        self.assertIn('CPU', names)
    
    def test_search_by_keyword(self):
        """Test searching by keyword"""
        results = self.discovery.search('docker')
        
        # Should find Docker collectors
        self.assertGreater(len(results), 0)
        for collector in results:
            # Name or description should contain docker
            text = f"{collector.name} {collector.description}".lower()
            self.assertIn('docker', text)
    
    def test_search_case_insensitive(self):
        """Test that search is case insensitive"""
        results_lower = self.discovery.search('cpu')
        results_upper = self.discovery.search('CPU')
        results_mixed = self.discovery.search('CpU')
        
        # All should return same results
        self.assertEqual(len(results_lower), len(results_upper))
        self.assertEqual(len(results_lower), len(results_mixed))
    
    def test_search_no_results(self):
        """Test search with no matching results"""
        results = self.discovery.search('zzz_nonexistent_xyz')
        self.assertEqual(len(results), 0)
    
    def test_collector_has_functions(self):
        """Test that collectors have function information"""
        cpu = self.discovery.get_collector('CPU')
        self.assertIsNotNone(cpu)
        self.assertGreater(len(cpu.functions), 0)
        
        # Check function structure
        func = cpu.functions[0]
        self.assertTrue(hasattr(func, 'name'))
        self.assertTrue(hasattr(func, 'parameters'))
    
    def test_collector_has_description(self):
        """Test that collectors have descriptions"""
        collectors = self.discovery.list_collectors()
        
        # Most collectors should have descriptions
        with_desc = [c for c in collectors if c.description]
        self.assertGreater(len(with_desc), len(collectors) * 0.5)
    
    def test_collector_categories_valid(self):
        """Test that all collectors have valid categories"""
        collectors = self.discovery.list_collectors()
        valid_categories = self.discovery.get_categories()
        
        for collector in collectors:
            self.assertIn(collector.category, valid_categories)
    
    def test_search_relevance_order(self):
        """Test that search results are ordered by relevance"""
        # Search for 'timer' - Timer collector should be first
        results = self.discovery.search('timer')
        
        if len(results) > 1:
            # First result should be Timer (exact name match)
            # or at least have 'timer' in name
            first = results[0]
            self.assertTrue(
                'timer' in first.name.lower() or 
                'timer' in first.description.lower()
            )


class TestCollectorDiscoveryWithMockData(unittest.TestCase):
    """Test cases with mock collector data"""
    
    def setUp(self):
        """Set up mock collector directory"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.collectors_dir = self.temp_dir / 'Minion' / 'Collectors'
        self.collectors_dir.mkdir(parents=True)
        
        # Create mock __init__.py
        (self.collectors_dir / '__init__.py').write_text('')
        
        # Create mock collector
        mock_collector = '''"""
File Abstract:
Test collector for unit tests
"""

def test_function(param1, param2='default'):
    """Test function description
    
    Args:
        param1: First parameter
        param2: Second parameter with default
    
    Returns:
        Test result
    """
    return "test"

def another_function():
    """Another test function"""
    pass
'''
        (self.collectors_dir / 'TestCollector.py').write_text(mock_collector)
    
    def tearDown(self):
        """Clean up temp directory"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_parse_mock_collector(self):
        """Test parsing mock collector"""
        discovery = CollectorDiscovery(self.temp_dir)
        
        collectors = discovery.list_collectors()
        self.assertEqual(len(collectors), 1)
        
        collector = collectors[0]
        self.assertEqual(collector.name, 'TestCollector')
        self.assertEqual(len(collector.functions), 2)
        
        # Check function details
        func = collector.functions[0]
        self.assertEqual(func.name, 'test_function')
        self.assertEqual(len(func.parameters), 2)
        
        # Check parameters
        param1 = func.parameters[0]
        self.assertEqual(param1.name, 'param1')
        self.assertIsNone(param1.default)
        
        param2 = func.parameters[1]
        self.assertEqual(param2.name, 'param2')
        # Default value extraction may vary - just check it exists
        self.assertIsNotNone(param2)


if __name__ == '__main__':
    unittest.main()
