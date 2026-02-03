"""
Tests for Oscar CLI commands
"""

import pytest
from pathlib import Path
import tempfile
import sys
from io import StringIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from biff_cli.main import main


class TestOscarGenerate:
    """Test oscar generate command"""
    
    def test_generate_unified_oscar(self, tmp_path, monkeypatch):
        """Test generating unified Oscar config"""
        # Create Minion config
        minion_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>Production</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
    <Collector ID="cpu"><Executable>CPU.py</Executable></Collector>
  </Namespace>
</Minion>"""
        
        minion_file = tmp_path / "MinionConfig.xml"
        minion_file.write_text(minion_xml)
        
        output_file = tmp_path / "OscarConfig.xml"
        
        # Run command
        monkeypatch.setattr('sys.argv', [
            'biff', 'oscar', 'generate',
            '--from-minion', str(minion_file),
            '-o', str(output_file)
        ])
        
        result = main()
        
        assert result == 0
        assert output_file.exists()
        
        oscar_content = output_file.read_text()
        assert 'Oscar' in oscar_content
        assert 'PORT="1100"' in oscar_content
        assert 'PORT="52001"' in oscar_content
    
    def test_generate_per_namespace(self, tmp_path, monkeypatch):
        """Test generating per-namespace Oscar configs"""
        minion_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>NS1</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
    <Collector ID="cpu"><Executable>CPU.py</Executable></Collector>
  </Namespace>
  <Namespace>
    <Name>NS2</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1200"/>
    <Collector ID="mem"><Executable>Memory.py</Executable></Collector>
  </Namespace>
</Minion>"""
        
        minion_file = tmp_path / "MinionConfig.xml"
        minion_file.write_text(minion_xml)
        
        output_base = tmp_path / "Oscar"
        
        monkeypatch.setattr('sys.argv', [
            'biff', 'oscar', 'generate',
            '--from-minion', str(minion_file),
            '--per-namespace',
            '-o', str(output_base)
        ])
        
        result = main()
        
        assert result == 0
        assert (tmp_path / "Oscar_NS1.xml").exists()
        assert (tmp_path / "Oscar_NS2.xml").exists()
    
    def test_generate_missing_minion(self, tmp_path, monkeypatch):
        """Test error handling for missing Minion config"""
        monkeypatch.setattr('sys.argv', [
            'biff', 'oscar', 'generate',
            '--from-minion', str(tmp_path / "nonexistent.xml")
        ])
        
        result = main()
        assert result == 1
    
    def test_generate_with_marvin_params(self, tmp_path, monkeypatch):
        """Test generation with Marvin parameters"""
        minion_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>Test</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
  </Namespace>
</Minion>"""
        
        minion_file = tmp_path / "MinionConfig.xml"
        minion_file.write_text(minion_xml)
        
        output_file = tmp_path / "Oscar.xml"
        
        monkeypatch.setattr('sys.argv', [
            'biff', 'oscar', 'generate',
            '--from-minion', str(minion_file),
            '--marvin-count', '3',
            '--oscar-id', 'Production',
            '-o', str(output_file)
        ])
        
        result = main()
        
        assert result == 0
        oscar_content = output_file.read_text()
        assert 'Production' in oscar_content


class TestOscarValidate:
    """Test oscar validate command"""
    
    def test_validate_valid_routing(self, tmp_path, monkeypatch):
        """Test validating valid Minion→Oscar routing"""
        minion_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>Test</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
  </Namespace>
</Minion>"""
        
        oscar_xml = """<?xml version="1.0"?>
<Oscar ID="TestOscar">
  <IncomingMinionConnection PORT="1100"/>
  <TargetConnection IP="localhost" PORT="52001"/>
</Oscar>"""
        
        minion_file = tmp_path / "Minion.xml"
        oscar_file = tmp_path / "Oscar.xml"
        minion_file.write_text(minion_xml)
        oscar_file.write_text(oscar_xml)
        
        monkeypatch.setattr('sys.argv', [
            'biff', 'oscar', 'validate',
            '--minion', str(minion_file),
            '--oscar', str(oscar_file)
        ])
        
        result = main()
        assert result == 0
    
    def test_validate_port_mismatch(self, tmp_path, monkeypatch):
        """Test validation detects port mismatches"""
        minion_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>Test</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
  </Namespace>
</Minion>"""
        
        oscar_xml = """<?xml version="1.0"?>
<Oscar ID="TestOscar">
  <IncomingMinionConnection PORT="1200"/>
  <TargetConnection IP="localhost" PORT="52001"/>
</Oscar>"""
        
        minion_file = tmp_path / "Minion.xml"
        oscar_file = tmp_path / "Oscar.xml"
        minion_file.write_text(minion_xml)
        oscar_file.write_text(oscar_xml)
        
        monkeypatch.setattr('sys.argv', [
            'biff', 'oscar', 'validate',
            '--minion', str(minion_file),
            '--oscar', str(oscar_file)
        ])
        
        result = main()
        assert result == 1
    
    def test_validate_missing_files(self, tmp_path, monkeypatch):
        """Test validation with missing files"""
        monkeypatch.setattr('sys.argv', [
            'biff', 'oscar', 'validate',
            '--minion', str(tmp_path / "nonexistent.xml"),
            '--oscar', str(tmp_path / "missing.xml")
        ])
        
        result = main()
        assert result == 1


class TestOscarAnalyze:
    """Test oscar analyze command"""
    
    def test_analyze_minion_config(self, tmp_path, monkeypatch, capsys):
        """Test analyzing Minion configuration"""
        minion_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>System</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
    <Collector ID="cpu" Frequency="100"><Executable>CPU.py</Executable></Collector>
    <Collector ID="mem"><Executable>Memory.py</Executable></Collector>
    <Actor ID="restart"><Executable>restart.sh</Executable></Actor>
  </Namespace>
  <Namespace>
    <Name>Network</Name>
    <DefaultFrequency>2000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
    <Collector ID="bandwidth"><Executable>Network.py</Executable></Collector>
  </Namespace>
</Minion>"""
        
        minion_file = tmp_path / "Minion.xml"
        minion_file.write_text(minion_xml)
        
        monkeypatch.setattr('sys.argv', [
            'biff', 'oscar', 'analyze',
            '--minion', str(minion_file)
        ])
        
        result = main()
        
        assert result == 0
        
        captured = capsys.readouterr()
        assert 'Namespaces: 2' in captured.out
        assert 'Total Collectors: 3' in captured.out
        assert 'Total Actors: 1' in captured.out
    
    def test_analyze_json_output(self, tmp_path, monkeypatch, capsys):
        """Test JSON output format"""
        minion_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>Test</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
  </Namespace>
</Minion>"""
        
        minion_file = tmp_path / "Minion.xml"
        minion_file.write_text(minion_xml)
        
        monkeypatch.setattr('sys.argv', [
            'biff', 'oscar', 'analyze',
            '--minion', str(minion_file),
            '--json'
        ])
        
        result = main()
        
        assert result == 0
        
        captured = capsys.readouterr()
        assert 'namespace_count' in captured.out
        assert '"namespace_count": 1' in captured.out
    
    def test_analyze_missing_minion(self, tmp_path, monkeypatch):
        """Test analyze with missing Minion config"""
        monkeypatch.setattr('sys.argv', [
            'biff', 'oscar', 'analyze',
            '--minion', str(tmp_path / "nonexistent.xml")
        ])
        
        result = main()
        assert result == 1


class TestOscarDeployGuide:
    """Test oscar deploy-guide command"""
    
    def test_generate_deploy_guide(self, tmp_path, monkeypatch):
        """Test generating deployment guide"""
        minion_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>Production</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="192.168.1.50" PORT="1100"/>
    <Collector ID="cpu"><Executable>CPU.py</Executable></Collector>
  </Namespace>
</Minion>"""
        
        minion_file = tmp_path / "Minion.xml"
        minion_file.write_text(minion_xml)
        
        output_file = tmp_path / "deploy.md"
        
        monkeypatch.setattr('sys.argv', [
            'biff', 'oscar', 'deploy-guide',
            '--minion', str(minion_file),
            '-o', str(output_file)
        ])
        
        result = main()
        
        assert result == 0
        assert output_file.exists()
        
        guide = output_file.read_text()
        assert '# BIFF Deployment Guide' in guide
        assert 'Production' in guide
        assert 'python Oscar.py' in guide
        assert 'python Minion.py' in guide
    
    def test_deploy_guide_with_existing_oscar(self, tmp_path, monkeypatch):
        """Test deployment guide with existing Oscar config"""
        minion_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>Test</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
  </Namespace>
</Minion>"""
        
        oscar_xml = """<?xml version="1.0"?>
<Oscar ID="TestOscar">
  <IncomingMinionConnection PORT="1100"/>
  <TargetConnection IP="localhost" PORT="52001"/>
</Oscar>"""
        
        minion_file = tmp_path / "Minion.xml"
        oscar_file = tmp_path / "Oscar.xml"
        output_file = tmp_path / "deploy.md"
        
        minion_file.write_text(minion_xml)
        oscar_file.write_text(oscar_xml)
        
        monkeypatch.setattr('sys.argv', [
            'biff', 'oscar', 'deploy-guide',
            '--minion', str(minion_file),
            '--oscar', str(oscar_file),
            '-o', str(output_file)
        ])
        
        result = main()
        
        assert result == 0
        assert output_file.exists()


class TestOscarCommandErrors:
    """Test error handling for Oscar commands"""
    
    def test_no_action_specified(self, monkeypatch):
        """Test error when no Oscar action specified"""
        monkeypatch.setattr('sys.argv', ['biff', 'oscar'])
        
        # Handler returns 1 when no action specified
        result = main()
        assert result == 1
    
    def test_invalid_action(self, tmp_path, monkeypatch):
        """Test handling of invalid Oscar action"""
        # Note: argparse prevents invalid actions, so this tests the parser
        monkeypatch.setattr('sys.argv', ['biff', 'oscar', 'generate'])
        
        # Missing required --from-minion argument
        with pytest.raises(SystemExit) as excinfo:
            main()
        
        assert excinfo.value.code != 0
