"""Unit tests for environment validator"""
import unittest
from unittest.mock import patch, MagicMock
import subprocess
import socket

from biff_agents_core.utils.environment_validator import EnvironmentValidator


class TestEnvironmentValidator(unittest.TestCase):
    """Test cases for EnvironmentValidator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = EnvironmentValidator()
    
    def test_initialization(self):
        """Test validator initializes with empty lists"""
        self.assertEqual(len(self.validator.issues), 0)
        self.assertEqual(len(self.validator.warnings), 0)
        self.assertEqual(len(self.validator.info), 0)
    
    @patch('subprocess.run')
    def test_check_java_version_success(self, mock_run):
        """Test Java version check with valid Java"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stderr='openjdk version "11.0.12" 2021-07-20\n'
        )
        
        result = self.validator.check_java_version()
        
        self.assertTrue(result["sufficient"])
        self.assertTrue(result["installed"])
        self.assertEqual(len(self.validator.issues), 0)
        self.assertTrue(any('Java' in msg for msg in self.validator.info))
    
    @patch('subprocess.run')
    def test_check_java_version_not_found(self, mock_run):
        """Test Java version check when Java not installed"""
        mock_run.side_effect = FileNotFoundError()
        
        result = self.validator.check_java_version()
        
        self.assertFalse(result["sufficient"])
        self.assertFalse(result["installed"])
        # Changed to warning since Java only needed for Marvin
        self.assertTrue(any('Java not found' in msg for msg in self.validator.warnings))
    
    @patch('subprocess.run')
    def test_check_java_version_old(self, mock_run):
        """Test Java version check with old Java version"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stderr='java version "1.8.0_291"\n'
        )
        
        result = self.validator.check_java_version()
        
        self.assertFalse(result["sufficient"])
        self.assertTrue(result["installed"])
        # Changed to warning since Java only needed for Marvin
        self.assertTrue(any('Java 8' in msg for msg in self.validator.warnings))
    
    def test_check_python_version_success(self):
        """Test Python version check (should pass on current Python)"""
        result = self.validator.check_python_version()
        
        # Current Python must be 3.9+ to run this test
        self.assertTrue(result)
        self.assertTrue(any('Python' in msg for msg in self.validator.info))
    
    @patch('socket.socket')
    def test_check_ports_available_success(self, mock_socket):
        """Test port check when ports are available"""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        result = self.validator.check_ports_available([1100, 52001])
        
        self.assertTrue(result["all_available"])
        self.assertTrue(any('1100' in msg for msg in self.validator.info))
        self.assertTrue(any('52001' in msg for msg in self.validator.info))
    
    def test_check_ports_available_in_use(self):
        """Test port check when port is in use"""
        # Mock is_port_available to return False
        with patch.object(self.validator, 'is_port_available', return_value=False):
            result = self.validator.check_ports_available([1100])
            
            self.assertFalse(result["all_available"])
            self.assertTrue(any('in use' in msg.lower() for msg in self.validator.warnings))
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('shutil.which')
    def test_check_gradle_found(self, mock_which, mock_exists, mock_run):
        """Test Gradle check when installed"""
        mock_exists.return_value = False  # No gradlew
        mock_which.return_value = '/usr/bin/gradle'
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='Gradle 7.0\n'
        )
        
        result = self.validator.check_gradle()
        
        self.assertTrue(result["installed"])
        # Note: check_gradle doesn't add info messages, only warnings/issues
    
    @patch('os.path.exists')
    @patch('shutil.which')
    def test_check_gradle_not_found(self, mock_which, mock_exists):
        """Test Gradle check when not installed"""
        mock_which.return_value = None
        mock_exists.return_value = False
        
        result = self.validator.check_gradle()
        
        self.assertFalse(result["installed"])
        self.assertTrue(any('Gradle' in msg for msg in self.validator.warnings))
    
    def test_validate_all(self):
        """Test validate_all runs all checks and returns results dict"""
        results = self.validator.validate_all()
        
        # Should return a dict with expected keys
        self.assertIn('python', results)
        self.assertIn('java', results)
        self.assertIn('ports', results)
        self.assertIn('system', results)
        self.assertIn('ready', results)
        
        # ready should be boolean
        self.assertIsInstance(results['ready'], bool)
    
    def test_suggest_fixes_with_java_missing(self):
        """Test fix suggestions when Java is missing"""
        self.validator.issues.append("✗ Java not found in PATH")
        
        fixes = self.validator.suggest_fixes()
        
        self.assertTrue(len(fixes) > 0)
        self.assertTrue(any('Java' in fix for fix in fixes))
    
    def test_suggest_fixes_with_port_conflict(self):
        """Test fix suggestions when port is in use"""
        self.validator.warnings.append("⚠ Port 1100 is in use")
        
        fixes = self.validator.suggest_fixes()
        
        self.assertTrue(len(fixes) > 0)
        self.assertTrue(any('Port' in fix for fix in fixes))
    
    def test_suggest_fixes_with_gradle_missing(self):
        """Test fix suggestions when Gradle is missing"""
        # Note: Gradle warnings don't generate fix suggestions in current implementation
        # This is expected behavior as gradlew is included in BIFF repo
        self.validator.warnings.append("⚠ Gradle not found")
        
        fixes = self.validator.suggest_fixes()
        
        # Should return empty list or general suggestion
        self.assertIsInstance(fixes, list)


if __name__ == '__main__':
    unittest.main()
