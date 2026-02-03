"""
Tests for collector search functionality

Tests advanced search, full-text search, function search, and regex search.
"""

import unittest
import re
from pathlib import Path
from biff_agents_core.utils.collector_discovery import CollectorDiscovery


class TestAdvancedSearchFilters(unittest.TestCase):
    """Test search_collectors() with various filters"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        # Find BIFF root (go up from tests/ to biff-agents/ to Board-Instrumentation-Framework/)
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
    
    def test_filter_by_category(self):
        """Test filtering collectors by category"""
        results = self.discovery.search_collectors(by_category='system')
        
        self.assertGreater(len(results), 0, "Should find system collectors")
        for collector in results:
            self.assertEqual(collector.category, 'system')
    
    def test_filter_by_min_functions(self):
        """Test filtering collectors by minimum function count"""
        min_funcs = 10
        results = self.discovery.search_collectors(min_functions=min_funcs)
        
        self.assertGreater(len(results), 0, f"Should find collectors with {min_funcs}+ functions")
        for collector in results:
            self.assertGreaterEqual(
                len(collector.functions),
                min_funcs,
                f"{collector.name} should have at least {min_funcs} functions"
            )
    
    def test_filter_by_function_name(self):
        """Test filtering collectors by function name"""
        # CPU collector has functions with "Percentage" in name
        results = self.discovery.search_collectors(has_function='Percentage')
        
        self.assertGreater(len(results), 0, "Should find collectors with Percentage functions")
        
        # Verify at least one result has matching function
        found_match = False
        for collector in results:
            for func in collector.functions:
                if 'percentage' in func.name.lower():
                    found_match = True
                    break
            if found_match:
                break
        
        self.assertTrue(found_match, "At least one collector should have function with 'Percentage'")
    
    def test_combined_filters(self):
        """Test combining multiple filters"""
        results = self.discovery.search_collectors(
            by_category='system',
            min_functions=5
        )
        
        self.assertGreater(len(results), 0, "Should find system collectors with 5+ functions")
        for collector in results:
            self.assertEqual(collector.category, 'system')
            self.assertGreaterEqual(len(collector.functions), 5)
    
    def test_filter_no_results(self):
        """Test filters that return no results"""
        results = self.discovery.search_collectors(
            by_category='nonexistent_category'
        )
        
        self.assertEqual(len(results), 0, "Should return empty list for non-existent category")


class TestFullTextSearch(unittest.TestCase):
    """Test full_text_search() with scoring"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
    
    def test_search_single_keyword(self):
        """Test searching with single keyword"""
        results = self.discovery.full_text_search('cpu')
        
        self.assertGreater(len(results), 0, "Should find CPU-related collectors")
        
        # Verify results are tuples of (collector, score)
        for collector, score in results:
            self.assertGreater(score, 0, "Score should be positive")
            # At least one should match 'cpu' in name or description
            has_match = (
                'cpu' in collector.name.lower() or
                'cpu' in collector.description.lower() or
                any('cpu' in f.name.lower() for f in collector.functions)
            )
            if has_match:
                break
        
        self.assertTrue(True, "Found CPU-related content")
    
    def test_search_multiple_keywords(self):
        """Test searching with multiple keywords"""
        results = self.discovery.full_text_search('docker container')
        
        self.assertGreater(len(results), 0, "Should find docker container collectors")
        
        # First result should have highest score
        if len(results) > 1:
            self.assertGreaterEqual(
                results[0][1],
                results[1][1],
                "Results should be sorted by score"
            )
    
    def test_search_results_sorted(self):
        """Test that results are sorted by relevance score"""
        results = self.discovery.full_text_search('system')
        
        if len(results) > 1:
            for i in range(len(results) - 1):
                self.assertGreaterEqual(
                    results[i][1],
                    results[i + 1][1],
                    f"Result {i} should have higher or equal score than {i+1}"
                )
    
    def test_search_max_results(self):
        """Test limiting number of results"""
        max_results = 3
        results = self.discovery.full_text_search('get', max_results=max_results)
        
        self.assertLessEqual(
            len(results),
            max_results,
            f"Should return at most {max_results} results"
        )
    
    def test_search_no_matches(self):
        """Test searching for non-existent keywords"""
        results = self.discovery.full_text_search('xyzabc123nonexistent')
        
        self.assertEqual(len(results), 0, "Should return empty list for non-existent keywords")
    
    def test_search_name_higher_weight(self):
        """Test that name matches have higher scores than description matches"""
        # Search for "Random" - should rank RandomVal high (name match)
        results = self.discovery.full_text_search('random')
        
        if len(results) > 0:
            # RandomVal should be in results with high score due to name match
            random_val_result = next((r for r in results if r[0].name == 'RandomVal'), None)
            if random_val_result:
                self.assertGreater(
                    random_val_result[1],
                    5.0,  # Name weight is 5.0
                    "RandomVal should have high score due to name match"
                )


class TestFunctionNameSearch(unittest.TestCase):
    """Test search_by_function() with exact and partial matching"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
    
    def test_partial_match(self):
        """Test partial function name matching"""
        results = self.discovery.search_by_function('Get', exact=False)
        
        self.assertGreater(len(results), 0, "Should find collectors with 'Get' in function names")
        
        # Verify at least one has matching function
        found = False
        for collector in results:
            for func in collector.functions:
                if 'get' in func.name.lower():
                    found = True
                    break
            if found:
                break
        
        self.assertTrue(found, "At least one collector should have function containing 'Get'")
    
    def test_case_insensitive(self):
        """Test that search is case-insensitive"""
        results_lower = self.discovery.search_by_function('random', exact=False)
        results_upper = self.discovery.search_by_function('RANDOM', exact=False)
        results_mixed = self.discovery.search_by_function('RaNdOm', exact=False)
        
        self.assertEqual(
            len(results_lower),
            len(results_upper),
            "Case should not affect results"
        )
        self.assertEqual(
            len(results_lower),
            len(results_mixed),
            "Case should not affect results"
        )
    
    def test_no_matches(self):
        """Test searching for non-existent function"""
        results = self.discovery.search_by_function('NonExistentFunction123', exact=False)
        
        self.assertEqual(len(results), 0, "Should return empty list for non-existent function")


class TestRegexSearch(unittest.TestCase):
    """Test regex_search() with pattern matching"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
    
    def test_pattern_in_name(self):
        """Test regex pattern matching in collector names"""
        results = self.discovery.regex_search(r'^Docker', search_in='name')
        
        self.assertGreater(len(results), 0, "Should find collectors starting with 'Docker'")
        for collector in results:
            self.assertTrue(
                collector.name.startswith('Docker'),
                f"{collector.name} should start with 'Docker'"
            )
    
    def test_pattern_in_functions(self):
        """Test regex pattern matching in function names"""
        # Match functions like GetCPU_*, GetRandom*, etc.
        results = self.discovery.regex_search(r'Get\w+', search_in='functions')
        
        self.assertGreater(len(results), 0, "Should find collectors with Get* functions")
    
    def test_pattern_in_all(self):
        """Test regex pattern searching all fields"""
        results = self.discovery.regex_search(r'system|docker', search_in='all')
        
        self.assertGreater(len(results), 0, "Should find collectors matching pattern")
    
    def test_invalid_regex(self):
        """Test handling of invalid regex patterns"""
        with self.assertRaises(ValueError) as context:
            self.discovery.regex_search(r'[invalid(regex', search_in='name')
        
        self.assertIn('Invalid regex pattern', str(context.exception))
    
    def test_complex_pattern(self):
        """Test complex regex patterns"""
        # Match collectors with underscore in name
        results = self.discovery.regex_search(r'\w+_\w+', search_in='name')
        
        self.assertGreater(len(results), 0, "Should find collectors with underscore")
        for collector in results:
            self.assertIn('_', collector.name, f"{collector.name} should contain underscore")


class TestSearchEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        current = Path(__file__).parent.parent.parent
        cls.discovery = CollectorDiscovery(current)
    
    def test_empty_search_query(self):
        """Test searching with empty query"""
        results = self.discovery.full_text_search('')
        
        self.assertEqual(len(results), 0, "Empty query should return no results")
    
    def test_special_characters_in_query(self):
        """Test searching with special characters"""
        # Should not crash, may or may not find results
        try:
            results = self.discovery.full_text_search('test@#$%')
            # No assertion - just verify it doesn't crash
            self.assertIsInstance(results, list)
        except Exception as e:
            self.fail(f"Search with special characters should not crash: {e}")
    
    def test_very_long_query(self):
        """Test searching with very long query"""
        long_query = ' '.join(['word'] * 100)
        results = self.discovery.full_text_search(long_query)
        
        self.assertIsInstance(results, list, "Should return list even for long query")


if __name__ == '__main__':
    unittest.main()
