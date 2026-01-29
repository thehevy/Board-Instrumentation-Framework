"""
Test suite for BIFFXMLParser
"""

import pytest
import xml.etree.ElementTree as ET
from pathlib import Path
import tempfile

from biff_agents_core.config.xml_parser import BIFFXMLParser


class TestBIFFXMLParser:
    """Test cases for XML parser"""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return BIFFXMLParser()
    
    @pytest.fixture
    def sample_minion_xml(self):
        """Create sample Minion XML"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<Minion>
    <AliasList>
        <Alias COLOR="blue" SIZE="10"/>
        <Alias NAMESPACE="TestNamespace"/>
    </AliasList>
    <Namespace>
        <Name>$(NAMESPACE)</Name>
        <DefaultFrequency>1000</DefaultFrequency>
        <TargetConnection IP="localhost" PORT="5100"/>
        <Collector ID="cpu.usage" Frequency="500">
            <Executable>Collectors/CPU.py</Executable>
            <Param>GetUsage</Param>
        </Collector>
        <Actor ID="restart_service">
            <Executable>/usr/bin/systemctl</Executable>
            <Param>restart</Param>
            <Param>myservice</Param>
        </Actor>
    </Namespace>
</Minion>
"""
    
    @pytest.fixture
    def sample_oscar_xml(self):
        """Create sample Oscar XML"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<Oscar>
    <IncomingMinionConnection PORT="10020"/>
    <MarvinAutoConnect Key="demo123"/>
    <TargetConnection IP="192.168.1.100" PORT="52001"/>
</Oscar>
"""
    
    def test_parse_valid_xml(self, parser, sample_minion_xml):
        """Test parsing valid XML"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(sample_minion_xml)
            f.flush()
            
            root = parser.parse_config(f.name)
            
            assert root.tag == 'Minion'
            Path(f.name).unlink()
    
    def test_parse_nonexistent_file(self, parser):
        """Test parsing nonexistent file raises error"""
        with pytest.raises(FileNotFoundError):
            parser.parse_config('nonexistent.xml')
    
    def test_extract_aliases(self, parser, sample_minion_xml):
        """Test alias extraction"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(sample_minion_xml)
            f.flush()
            
            root = parser.parse_config(f.name)
            aliases = parser.extract_aliases(root)
            
            assert 'COLOR' in aliases
            assert aliases['COLOR'] == 'blue'
            assert 'SIZE' in aliases
            assert aliases['SIZE'] == '10'
            assert 'NAMESPACE' in aliases
            
            Path(f.name).unlink()
    
    def test_extract_collectors(self, parser, sample_minion_xml):
        """Test collector extraction"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(sample_minion_xml)
            f.flush()
            
            root = parser.parse_config(f.name)
            collectors = parser.extract_collectors(root)
            
            assert len(collectors) == 1
            assert collectors[0]['id'] == 'cpu.usage'
            assert collectors[0]['frequency'] == '500'
            assert collectors[0]['executable'] == 'Collectors/CPU.py'
            assert 'GetUsage' in collectors[0]['params']
            
            Path(f.name).unlink()
    
    def test_extract_actors(self, parser, sample_minion_xml):
        """Test actor extraction"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(sample_minion_xml)
            f.flush()
            
            root = parser.parse_config(f.name)
            actors = parser.extract_actors(root)
            
            assert len(actors) == 1
            assert actors[0]['id'] == 'restart_service'
            assert actors[0]['executable'] == '/usr/bin/systemctl'
            assert len(actors[0]['params']) == 2
            
            Path(f.name).unlink()
    
    def test_get_component_type_minion(self, parser, sample_minion_xml):
        """Test component type detection - Minion"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(sample_minion_xml)
            f.flush()
            
            root = parser.parse_config(f.name)
            comp_type = parser.get_component_type(root)
            
            assert comp_type == 'Minion'
            Path(f.name).unlink()
    
    def test_get_component_type_oscar(self, parser, sample_oscar_xml):
        """Test component type detection - Oscar"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(sample_oscar_xml)
            f.flush()
            
            root = parser.parse_config(f.name)
            comp_type = parser.get_component_type(root)
            
            assert comp_type == 'Oscar'
            Path(f.name).unlink()
    
    def test_extract_oscar_connections(self, parser, sample_oscar_xml):
        """Test Oscar connection extraction"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(sample_oscar_xml)
            f.flush()
            
            root = parser.parse_config(f.name)
            connections = parser.extract_oscar_connections(root)
            
            assert connections['incoming_port'] == '10020'
            assert connections['autoconnect_key'] == 'demo123'
            assert len(connections['targets']) == 1
            assert connections['targets'][0]['ip'] == '192.168.1.100'
            
            Path(f.name).unlink()
