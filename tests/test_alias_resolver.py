"""
Test suite for AliasResolver
"""

import pytest
from biff_agents_core.config.alias_resolver import AliasResolver


class TestAliasResolver:
    """Test cases for alias resolution"""
    
    @pytest.fixture
    def resolver(self):
        """Create resolver with sample aliases"""
        return AliasResolver({
            'COLOR': 'blue',
            'SIZE': '10',
            'NAMESPACE': 'TestNamespace',
        })
    
    def test_simple_resolve(self, resolver):
        """Test simple alias resolution"""
        text = "The color is $(COLOR)"
        result = resolver.resolve(text)
        assert result == "The color is blue"
    
    def test_multiple_resolve(self, resolver):
        """Test multiple alias resolution"""
        text = "Color: $(COLOR), Size: $(SIZE)"
        result = resolver.resolve(text)
        assert result == "Color: blue, Size: 10"
    
    def test_nested_resolve(self):
        """Test nested alias resolution"""
        resolver = AliasResolver({
            'A': '$(B)',
            'B': '$(C)',
            'C': 'final_value'
        })
        text = "Value: $(A)"
        result = resolver.resolve(text)
        assert result == "Value: final_value"
    
    def test_unresolved_alias_error(self, resolver):
        """Test error on unresolved alias"""
        text = "Unknown: $(UNKNOWN)"
        with pytest.raises(ValueError, match="Unresolved aliases"):
            resolver.resolve(text)
    
    def test_circular_reference_error(self):
        """Test error on circular reference"""
        resolver = AliasResolver({
            'A': '$(B)',
            'B': '$(A)',
        })
        text = "Value: $(A)"
        with pytest.raises(ValueError, match="circular reference"):
            resolver.resolve(text)
    
    def test_add_alias(self, resolver):
        """Test adding new alias"""
        resolver.add_alias('NEW', 'value')
        text = "New: $(NEW)"
        result = resolver.resolve(text)
        assert result == "New: value"
    
    def test_get_unresolved_aliases(self, resolver):
        """Test getting list of unresolved aliases"""
        text = "Known: $(COLOR), Unknown: $(UNKNOWN), Another: $(MISSING)"
        unresolved = resolver.get_unresolved_aliases(text)
        assert set(unresolved) == {'UNKNOWN', 'MISSING'}
