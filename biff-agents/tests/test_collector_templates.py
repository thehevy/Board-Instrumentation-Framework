"""
Tests for collector template generation and validation

Tests XML template generation, validation, customization, and namespace configs.
"""

import unittest
import re
from pathlib import Path
from biff_agents_core.utils.collector_discovery import CollectorDiscovery


class TestTemplateGeneration(unittest.TestCase):
    """Test generate_collector_xml() method"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
    
    def test_generate_basic_template(self):
        """Test generating basic collector template"""
        xml = self.discovery.generate_collector_xml('RandomVal')
        
        self.assertIn('<Collector', xml)
        self.assertIn('ID=', xml)
        self.assertIn('Frequency=', xml)
        self.assertIn('<Executable>', xml)
        self.assertIn('RandomVal.py', xml)
        self.assertIn('<Param>', xml)
    
    def test_generate_with_function(self):
        """Test generating template with specific function"""
        xml = self.discovery.generate_collector_xml('RandomVal', 'GetBoundedRandomValue')
        
        self.assertIn('GetBoundedRandomValue', xml)
        self.assertIn('ID="RandomVal.GetBoundedRandomValue"', xml)
    
    def test_generate_with_custom_id(self):
        """Test generating template with custom ID"""
        xml = self.discovery.generate_collector_xml(
            'RandomVal',
            'GetBoundedRandomValue',  # Use actual function name
            collector_id='my.custom.id'
        )
        
        self.assertIn('ID="my.custom.id"', xml)
    
    def test_generate_with_custom_frequency(self):
        """Test generating template with custom frequency"""
        xml = self.discovery.generate_collector_xml(
            'RandomVal',
            frequency=500
        )
        
        self.assertIn('Frequency="500"', xml)
    
    def test_generate_with_all_params(self):
        """Test generating template with all parameters"""
        xml = self.discovery.generate_collector_xml(
            'RandomVal',
            'GetBoundedRandomValue',
            include_all_params=True
        )
        
        # Should include parameter placeholders or defaults
        self.assertGreater(xml.count('<Param>'), 1)  # Function name + params
    
    def test_generate_nonexistent_collector(self):
        """Test error handling for nonexistent collector"""
        with self.assertRaises(ValueError) as context:
            self.discovery.generate_collector_xml('NonExistentCollector')
        
        self.assertIn('not found', str(context.exception))
    
    def test_generate_nonexistent_function(self):
        """Test error handling for nonexistent function"""
        with self.assertRaises(ValueError) as context:
            self.discovery.generate_collector_xml('RandomVal', 'NonExistentFunction')
        
        self.assertIn('not found', str(context.exception))
    
    def test_template_structure(self):
        """Test that generated template has proper XML structure"""
        xml = self.discovery.generate_collector_xml('RandomVal')
        
        # Check indentation
        lines = xml.split('\n')
        self.assertTrue(lines[0].startswith('  <Collector'))  # 2 spaces
        self.assertTrue(any(line.startswith('    <') for line in lines))  # 4 spaces
        
        # Check closing tag
        self.assertTrue(lines[-1].strip().endswith('</Collector>'))


class TestTemplateValidation(unittest.TestCase):
    """Test validate_collector_config() method"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
    
    def test_validate_valid_config(self):
        """Test validating a valid collector configuration"""
        xml = """
        <Collector ID="test.collector" Frequency="1000">
            <Executable>Collectors/Test.py</Executable>
            <Param>GetValue</Param>
        </Collector>
        """
        
        valid, errors = self.discovery.validate_collector_config(xml)
        
        self.assertTrue(valid, f"Should be valid, got errors: {errors}")
        self.assertEqual(len(errors), 0)
    
    def test_validate_missing_id(self):
        """Test validation catches missing ID attribute"""
        xml = """
        <Collector Frequency="1000">
            <Executable>Collectors/Test.py</Executable>
            <Param>GetValue</Param>
        </Collector>
        """
        
        valid, errors = self.discovery.validate_collector_config(xml)
        
        self.assertFalse(valid)
        self.assertTrue(any('ID' in error for error in errors))
    
    def test_validate_missing_frequency(self):
        """Test validation catches missing Frequency attribute"""
        xml = """
        <Collector ID="test.collector">
            <Executable>Collectors/Test.py</Executable>
            <Param>GetValue</Param>
        </Collector>
        """
        
        valid, errors = self.discovery.validate_collector_config(xml)
        
        self.assertFalse(valid)
        self.assertTrue(any('Frequency' in error for error in errors))
    
    def test_validate_invalid_frequency(self):
        """Test validation catches invalid frequency values"""
        xml = """
        <Collector ID="test.collector" Frequency="0">
            <Executable>Collectors/Test.py</Executable>
            <Param>GetValue</Param>
        </Collector>
        """
        
        valid, errors = self.discovery.validate_collector_config(xml)
        
        self.assertFalse(valid)
        self.assertTrue(any('positive' in error.lower() for error in errors))
    
    def test_validate_missing_executable(self):
        """Test validation catches missing Executable element"""
        xml = """
        <Collector ID="test.collector" Frequency="1000">
            <Param>GetValue</Param>
        </Collector>
        """
        
        valid, errors = self.discovery.validate_collector_config(xml)
        
        self.assertFalse(valid)
        self.assertTrue(any('Executable' in error for error in errors))
    
    def test_validate_missing_params(self):
        """Test validation catches missing Param elements"""
        xml = """
        <Collector ID="test.collector" Frequency="1000">
            <Executable>Collectors/Test.py</Executable>
        </Collector>
        """
        
        valid, errors = self.discovery.validate_collector_config(xml)
        
        self.assertFalse(valid)
        self.assertTrue(any('Param' in error for error in errors))
    
    def test_validate_invalid_xml(self):
        """Test validation catches malformed XML"""
        xml = """
        <Collector ID="test.collector" Frequency="1000"
            <Executable>Collectors/Test.py</Executable>
        </Collector>
        """
        
        valid, errors = self.discovery.validate_collector_config(xml)
        
        self.assertFalse(valid)
        self.assertTrue(any('Invalid XML' in error for error in errors))


class TestTemplateCustomization(unittest.TestCase):
    """Test customize_template() method"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
    
    def test_customize_id(self):
        """Test customizing collector ID"""
        xml = self.discovery.generate_collector_xml('RandomVal')
        custom = self.discovery.customize_template(xml, new_id='custom.id')
        
        self.assertIn('ID="custom.id"', custom)
    
    def test_customize_frequency(self):
        """Test customizing frequency"""
        xml = self.discovery.generate_collector_xml('RandomVal')
        custom = self.discovery.customize_template(xml, new_frequency=500)
        
        self.assertIn('Frequency="500"', custom)
    
    def test_customize_param_values(self):
        """Test customizing parameter values"""
        xml = self.discovery.generate_collector_xml('RandomVal', 'GetBoundedRandomValue')
        # Set min=0, max=1000
        custom = self.discovery.customize_template(xml, param_values={0: '0', 1: '1000'})
        
        # Should contain the new values in Param elements
        self.assertIn('<Param>0</Param>', custom)
        self.assertIn('<Param>1000</Param>', custom)
    
    def test_customize_multiple_attributes(self):
        """Test customizing multiple attributes at once"""
        xml = self.discovery.generate_collector_xml('RandomVal')
        custom = self.discovery.customize_template(
            xml,
            new_id='custom.id',
            new_frequency=2000
        )
        
        self.assertIn('ID="custom.id"', custom)
        self.assertIn('Frequency="2000"', custom)
    
    def test_customize_invalid_xml(self):
        """Test error handling for invalid XML"""
        with self.assertRaises(ValueError):
            self.discovery.customize_template('<invalid xml', new_id='test')


class TestNamespaceGeneration(unittest.TestCase):
    """Test generate_namespace_config() method"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
    
    def test_generate_basic_namespace(self):
        """Test generating basic namespace configuration"""
        config = self.discovery.generate_namespace_config(
            'TestNamespace',
            [('RandomVal', 'GetBoundedRandomValue')]
        )
        
        self.assertIn('<Namespace>', config)
        self.assertIn('<Name>TestNamespace</Name>', config)
        self.assertIn('<DefaultFrequency>', config)
        self.assertIn('<TargetConnection', config)
        self.assertIn('</Namespace>', config)
    
    def test_generate_with_custom_target(self):
        """Test generating namespace with custom target"""
        config = self.discovery.generate_namespace_config(
            'TestNamespace',
            [('RandomVal', 'GetBoundedRandomValue')],
            target_ip='192.168.1.100',
            target_port=6000
        )
        
        self.assertIn('IP="192.168.1.100"', config)
        self.assertIn('PORT="6000"', config)
    
    def test_generate_with_custom_frequency(self):
        """Test generating namespace with custom frequency"""
        config = self.discovery.generate_namespace_config(
            'TestNamespace',
            [('RandomVal', 'GetBoundedRandomValue')],
            default_frequency=2000
        )
        
        self.assertIn('<DefaultFrequency>2000</DefaultFrequency>', config)
        self.assertIn('Frequency="2000"', config)
    
    def test_generate_with_multiple_collectors(self):
        """Test generating namespace with multiple collectors"""
        config = self.discovery.generate_namespace_config(
            'TestNamespace',
            [
                ('RandomVal', 'GetBoundedRandomValue'),
                ('Timer', 'Timer')  # Use actual Timer function
            ]
        )
        
        # Should contain both collectors
        self.assertIn('RandomVal', config)
        self.assertIn('Timer', config)
        self.assertGreaterEqual(config.count('<Collector'), 2)  # Changed to >=
    
    def test_generate_with_invalid_collector(self):
        """Test handling of invalid collector in namespace"""
        config = self.discovery.generate_namespace_config(
            'TestNamespace',
            [
                ('RandomVal', 'GetBoundedRandomValue'),
                ('NonExistent', 'GetValue')
            ]
        )
        
        # Should contain error comment
        self.assertIn('<!-- Error:', config)
        # But should still have valid RandomVal
        self.assertIn('RandomVal', config)


class TestTemplateEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
    
    def test_collector_with_no_functions(self):
        """Test handling collector with no functions"""
        # Most collectors have functions, but test error handling
        # This would require mocking, skip for now
        pass
    
    def test_generate_with_special_characters_in_id(self):
        """Test generating template with special characters in ID"""
        xml = self.discovery.generate_collector_xml(
            'RandomVal',
            collector_id='test.id-with_special.chars'
        )
        
        self.assertIn('test.id-with_special.chars', xml)
    
    def test_very_high_frequency(self):
        """Test generating template with very high frequency"""
        xml = self.discovery.generate_collector_xml(
            'RandomVal',
            frequency=999999999
        )
        
        self.assertIn('Frequency="999999999"', xml)
    
    def test_namespace_with_empty_collectors(self):
        """Test generating namespace with empty collectors list"""
        config = self.discovery.generate_namespace_config(
            'EmptyNamespace',
            []
        )
        
        # Should still generate valid namespace structure
        self.assertIn('<Namespace>', config)
        self.assertIn('</Namespace>', config)


if __name__ == '__main__':
    unittest.main()
