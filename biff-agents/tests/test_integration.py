"""
Integration Tests for Collector Discovery System

Tests complete workflows combining discovery, search, templates, and validation.
"""

import unittest
import tempfile
from pathlib import Path
from biff_agents_core.utils.collector_discovery import CollectorDiscovery


class TestEndToEndWorkflows(unittest.TestCase):
    """Test complete user workflows from discovery to template generation"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
    
    def test_discover_search_generate_workflow(self):
        """Test: Discover collectors, search for specific one, generate template"""
        # Step 1: List all collectors
        all_collectors = self.discovery.list_collectors()
        self.assertGreater(len(all_collectors), 0, "Should discover collectors")
        
        # Step 2: Search for system-related collectors
        results = self.discovery.full_text_search('cpu system', max_results=5)
        self.assertGreater(len(results), 0, "Should find CPU collectors")
        
        # Step 3: Pick first result and generate template
        collector, score = results[0]
        if collector.functions:
            xml = self.discovery.generate_collector_xml(
                collector.name,
                collector.functions[0].name
            )
            
            # Step 4: Validate generated template
            valid, errors = self.discovery.validate_collector_config(f'<root>{xml}</root>')
            self.assertTrue(valid, f"Template should be valid: {errors}")
    
    def test_filter_validate_customize_workflow(self):
        """Test: Filter collectors, validate requirements, customize template"""
        # Step 1: Filter by category and function count
        collectors = self.discovery.search_collectors(
            by_category='system',
            min_functions=3
        )
        self.assertGreater(len(collectors), 0, "Should find system collectors")
        
        # Step 2: Check dependencies for first collector
        collector = collectors[0]
        missing = self.discovery.get_missing_dependencies(collector.name)
        
        # Step 3: Generate template
        if collector.functions:
            xml = self.discovery.generate_collector_xml(
                collector.name,
                collector.functions[0].name,
                frequency=2000
            )
            
            # Step 4: Customize template
            custom_xml = self.discovery.customize_template(
                xml,
                new_id='custom.test.id',
                new_frequency=5000
            )
            
            self.assertIn('custom.test.id', custom_xml)
            self.assertIn('5000', custom_xml)
    
    def test_namespace_generation_workflow(self):
        """Test: Create complete namespace configuration with multiple collectors"""
        # Step 1: Search for collectors in different categories
        system_collectors = self.discovery.get_by_category('system')
        testing_collectors = self.discovery.get_by_category('testing')
        
        # Step 2: Select a few collectors
        selected = []
        if system_collectors and system_collectors[0].functions:
            selected.append((system_collectors[0].name, system_collectors[0].functions[0].name))
        if testing_collectors and testing_collectors[0].functions:
            selected.append((testing_collectors[0].name, testing_collectors[0].functions[0].name))
        
        if selected:
            # Step 3: Generate namespace config
            config = self.discovery.generate_namespace_config(
                'IntegrationTest',
                selected,
                target_ip='192.168.1.100',
                target_port=5100
            )
            
            # Step 4: Verify structure
            self.assertIn('<Namespace>', config)
            self.assertIn('IntegrationTest', config)
            self.assertIn('192.168.1.100', config)
            self.assertIn('</Namespace>', config)
    
    def test_regex_to_template_workflow(self):
        """Test: Use regex search to find collectors, generate templates"""
        # Step 1: Find collectors matching pattern
        results = self.discovery.regex_search(r'Random|Timer', search_in='name')
        self.assertGreater(len(results), 0, "Should find Random or Timer collectors")
        
        # Step 2: Generate templates for all results
        templates = []
        for collector in results[:3]:  # Limit to 3
            if collector.functions:
                try:
                    xml = self.discovery.generate_collector_xml(
                        collector.name,
                        collector.functions[0].name
                    )
                    templates.append(xml)
                except ValueError:
                    pass  # Skip if error
        
        self.assertGreater(len(templates), 0, "Should generate at least one template")
        
        # Step 3: Validate all templates
        for xml in templates:
            valid, errors = self.discovery.validate_collector_config(f'<root>{xml}</root>')
            self.assertTrue(valid, f"All templates should be valid: {errors}")


class TestCLIIntegration(unittest.TestCase):
    """Test CLI commands work correctly"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
        cls.temp_dir = tempfile.mkdtemp()
    
    def test_template_to_file_workflow(self):
        """Test generating template to file"""
        # Generate template
        xml = self.discovery.generate_collector_xml('RandomVal')
        
        # Write to file
        output_file = Path(self.temp_dir) / 'test_template.xml'
        output_file.write_text(xml, encoding='utf-8')
        
        # Read back and validate
        content = output_file.read_text(encoding='utf-8')
        self.assertEqual(content, xml)
        
        valid, errors = self.discovery.validate_collector_config(f'<root>{content}</root>')
        self.assertTrue(valid, "Saved template should be valid")
    
    def test_namespace_to_file_workflow(self):
        """Test generating namespace config to file"""
        config = self.discovery.generate_namespace_config(
            'TestNamespace',
            [('RandomVal', 'GetBoundedRandomValue')],
            target_ip='localhost',
            target_port=5100
        )
        
        # Write to file
        output_file = Path(self.temp_dir) / 'test_namespace.xml'
        output_file.write_text(config, encoding='utf-8')
        
        # Read back
        content = output_file.read_text(encoding='utf-8')
        self.assertIn('<Namespace>', content)
        self.assertIn('TestNamespace', content)


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test error handling in integrated workflows"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
    
    def test_invalid_collector_in_namespace(self):
        """Test namespace generation with mix of valid and invalid collectors"""
        config = self.discovery.generate_namespace_config(
            'MixedNamespace',
            [
                ('RandomVal', 'GetBoundedRandomValue'),  # Valid
                ('InvalidCollector', 'GetValue'),  # Invalid
            ]
        )
        
        # Should contain valid collector
        self.assertIn('RandomVal', config)
        # Should contain error comment for invalid
        self.assertIn('<!-- Error:', config)
    
    def test_search_with_no_results_then_fallback(self):
        """Test searching with no results, then trying broader search"""
        # Try specific search that returns nothing
        results = self.discovery.full_text_search('xyznonexistent123')
        self.assertEqual(len(results), 0)
        
        # Fallback to broader search
        results = self.discovery.full_text_search('system')
        self.assertGreater(len(results), 0, "Broader search should find results")
    
    def test_template_validation_error_recovery(self):
        """Test generating template, breaking it, detecting error"""
        # Generate valid template
        xml = self.discovery.generate_collector_xml('RandomVal')
        valid, errors = self.discovery.validate_collector_config(f'<root>{xml}</root>')
        self.assertTrue(valid)
        
        # Break the template
        broken_xml = xml.replace('Frequency="1000"', '')
        valid, errors = self.discovery.validate_collector_config(f'<root>{broken_xml}</root>')
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)


class TestPerformanceIntegration(unittest.TestCase):
    """Test performance of integrated operations"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
    
    def test_list_all_collectors_performance(self):
        """Test listing all collectors is fast"""
        import time
        
        start = time.time()
        collectors = self.discovery.list_collectors()
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 2.0, "Should list collectors in under 2 seconds")
        self.assertGreater(len(collectors), 0)
    
    def test_search_performance(self):
        """Test full-text search performance"""
        import time
        
        start = time.time()
        results = self.discovery.full_text_search('cpu memory network')
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 1.0, "Search should complete in under 1 second")
    
    def test_template_generation_batch_performance(self):
        """Test generating multiple templates quickly"""
        import time
        
        collectors = self.discovery.list_collectors()[:10]  # First 10
        
        start = time.time()
        templates = []
        for collector in collectors:
            if collector.functions:
                try:
                    xml = self.discovery.generate_collector_xml(
                        collector.name,
                        collector.functions[0].name
                    )
                    templates.append(xml)
                except ValueError:
                    pass
        elapsed = time.time() - start
        
        self.assertLess(elapsed, 2.0, "Should generate 10 templates in under 2 seconds")
        self.assertGreater(len(templates), 0)


class TestDataIntegrity(unittest.TestCase):
    """Test data integrity across operations"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
    
    def test_collector_metadata_consistency(self):
        """Test collector metadata is consistent across operations"""
        # Get collector via list
        all_collectors = self.discovery.list_collectors()
        test_collector = next((c for c in all_collectors if c.name == 'RandomVal'), None)
        self.assertIsNotNone(test_collector)
        
        # Get same collector via get_collector
        same_collector = self.discovery.get_collector('RandomVal')
        self.assertIsNotNone(same_collector)
        
        # Verify consistency
        self.assertEqual(test_collector.name, same_collector.name)
        self.assertEqual(test_collector.category, same_collector.category)
        self.assertEqual(len(test_collector.functions), len(same_collector.functions))
    
    def test_template_customization_preserves_structure(self):
        """Test customizing template preserves valid XML structure"""
        # Generate template
        xml = self.discovery.generate_collector_xml('RandomVal', frequency=1000)
        
        # Validate original
        valid1, _ = self.discovery.validate_collector_config(f'<root>{xml}</root>')
        self.assertTrue(valid1)
        
        # Customize multiple times
        xml = self.discovery.customize_template(xml, new_frequency=2000)
        xml = self.discovery.customize_template(xml, new_id='test.id')
        
        # Validate after customization
        valid2, _ = self.discovery.validate_collector_config(f'<root>{xml}</root>')
        self.assertTrue(valid2, "Customization should preserve validity")
    
    def test_search_results_are_valid_collectors(self):
        """Test that all search results are valid, usable collectors"""
        results = self.discovery.full_text_search('random timer cpu', max_results=10)
        
        for collector, score in results:
            # Verify collector has required attributes
            self.assertIsNotNone(collector.name)
            self.assertIsNotNone(collector.category)
            self.assertIsNotNone(collector.file_path)
            
            # Verify can generate template
            if collector.functions:
                xml = self.discovery.generate_collector_xml(
                    collector.name,
                    collector.functions[0].name
                )
                valid, errors = self.discovery.validate_collector_config(f'<root>{xml}</root>')
                self.assertTrue(valid, f"{collector.name} should generate valid template")


if __name__ == '__main__':
    unittest.main()
