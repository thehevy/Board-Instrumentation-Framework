"""
Tests for Oscar routing configuration parser and generator
"""

import pytest
from pathlib import Path
import tempfile
from biff_agents_core.utils.oscar_routing import (
    OscarConfigParser,
    OscarConfigGenerator,
    OscarRoutingAnalyzer,
    OscarConnection,
    OscarConfig
)


class TestOscarConfigParser:
    """Test Oscar configuration parsing"""
    
    def test_parse_basic_config(self, tmp_path):
        """Test parsing a basic Oscar configuration"""
        config_xml = """<?xml version="1.0" encoding="utf-8"?>
<Oscar ID="TestOscar">
  <IncomingMinionConnection PORT="1100"/>
  <TargetConnection IP="localhost" PORT="52001"/>
</Oscar>"""
        
        config_file = tmp_path / "oscar.xml"
        config_file.write_text(config_xml)
        
        parser = OscarConfigParser()
        config = parser.parse(config_file)
        
        assert config.oscar_id == "TestOscar"
        assert config.incoming_minion is not None
        assert config.incoming_minion.port == 1100
        assert len(config.target_connections) == 1
        assert config.target_connections[0].ip == "localhost"
        assert config.target_connections[0].port == 52001
    
    def test_parse_multiple_targets(self, tmp_path):
        """Test parsing Oscar with multiple Marvin targets"""
        config_xml = """<?xml version="1.0" encoding="utf-8"?>
<Oscar ID="MultiMarvin">
  <IncomingMinionConnection PORT="1100"/>
  <TargetConnection IP="192.168.1.100" PORT="52001"/>
  <TargetConnection IP="192.168.1.101" PORT="52002"/>
  <TargetConnection IP="192.168.1.102" PORT="52003"/>
</Oscar>"""
        
        config_file = tmp_path / "oscar.xml"
        config_file.write_text(config_xml)
        
        parser = OscarConfigParser()
        config = parser.parse(config_file)
        
        assert len(config.target_connections) == 3
        assert config.target_connections[0].port == 52001
        assert config.target_connections[1].port == 52002
        assert config.target_connections[2].port == 52003
    
    def test_parse_chained_oscar(self, tmp_path):
        """Test parsing chained Oscar configuration"""
        config_xml = """<?xml version="1.0" encoding="utf-8"?>
<Oscar ID="DownstreamOscar">
  <IncomingMinionConnection PORT="1100">
    <Oscar IP="upstream.oscar.com" Port="6200" Key="MySecretKey"/>
  </IncomingMinionConnection>
</Oscar>"""
        
        config_file = tmp_path / "oscar.xml"
        config_file.write_text(config_xml)
        
        parser = OscarConfigParser()
        config = parser.parse(config_file)
        
        assert len(config.chained_oscars) == 1
        assert config.chained_oscars[0].ip == "upstream.oscar.com"
        assert config.chained_oscars[0].port == 6200
        assert config.chained_oscars[0].key == "MySecretKey"
    
    def test_parse_marvin_autoconnect(self, tmp_path):
        """Test parsing Oscar with MarvinAutoConnect"""
        config_xml = """<?xml version="1.0" encoding="utf-8"?>
<Oscar ID="AutoConnectOscar">
  <IncomingMinionConnection PORT="10020">
    <MarvinAutoConnect Key="IPU-DEMO-KEY"/>
  </IncomingMinionConnection>
</Oscar>"""
        
        config_file = tmp_path / "oscar.xml"
        config_file.write_text(config_xml)
        
        parser = OscarConfigParser()
        config = parser.parse(config_file)
        
        assert config.incoming_minion.key == "IPU-DEMO-KEY"
        assert config.incoming_minion.port == 10020
    
    def test_parse_with_recording(self, tmp_path):
        """Test parsing Oscar with recording configuration"""
        config_xml = """<?xml version="1.0" encoding="utf-8"?>
<Oscar ID="RecordingOscar">
  <IncomingMinionConnection PORT="1100"/>
  <TargetConnection IP="localhost" PORT="52001"/>
  <RecordFile>Session_2026-02-02.biff</RecordFile>
</Oscar>"""
        
        config_file = tmp_path / "oscar.xml"
        config_file.write_text(config_xml)
        
        parser = OscarConfigParser()
        config = parser.parse(config_file)
        
        assert config.record_file == "Session_2026-02-02.biff"
    
    def test_parse_incoming_marvin_connection(self, tmp_path):
        """Test parsing Oscar with IncomingMarvinConnection"""
        config_xml = """<?xml version="1.0" encoding="utf-8"?>
<Oscar ID="BidirectionalOscar">
  <IncomingMinionConnection PORT="1100"/>
  <IncomingMarvinConnection PORT="1101"/>
  <TargetConnection IP="localhost" PORT="52001"/>
</Oscar>"""
        
        config_file = tmp_path / "oscar.xml"
        config_file.write_text(config_xml)
        
        parser = OscarConfigParser()
        config = parser.parse(config_file)
        
        assert config.incoming_marvin is not None
        assert config.incoming_marvin.port == 1101


class TestOscarConfigGenerator:
    """Test Oscar configuration generation"""
    
    def test_generate_basic_config(self):
        """Test generating a basic Oscar configuration"""
        generator = OscarConfigGenerator()
        xml = generator.generate_basic(
            oscar_id="TestOscar",
            minion_port=1100,
            marvin_targets=[('localhost', 52001)]
        )
        
        assert 'TestOscar' in xml
        assert 'PORT="1100"' in xml
        assert 'IP="localhost"' in xml
        assert 'PORT="52001"' in xml
    
    def test_generate_from_minion_namespace(self):
        """Test generating Oscar config from Minion namespace"""
        generator = OscarConfigGenerator()
        xml = generator.generate_from_minion_namespace(
            namespace_name="SystemMonitoring",
            target_ip="192.168.1.50",
            target_port=1100,
            marvin_ips=['192.168.1.100', '192.168.1.101']
        )
        
        assert 'Oscar_SystemMonitoring' in xml
        assert 'PORT="1100"' in xml
        assert 'IP="192.168.1.100"' in xml
        assert 'PORT="52001"' in xml
        assert 'IP="192.168.1.101"' in xml
        assert 'PORT="52002"' in xml
    
    def test_generate_multi_marvin(self):
        """Test generating Oscar config for multiple Marvins"""
        generator = OscarConfigGenerator()
        xml, port_map = generator.generate_multi_marvin(
            oscar_id="MultiOscar",
            minion_port=1100,
            marvin_count=3
        )
        
        assert 'MultiOscar' in xml
        assert len(port_map) == 3
        assert port_map['Marvin1']['port'] == 52001
        assert port_map['Marvin2']['port'] == 52002
        assert port_map['Marvin3']['port'] == 52003
        assert 'PORT="52001"' in xml
        assert 'PORT="52002"' in xml
        assert 'PORT="52003"' in xml
    
    def test_generate_multi_marvin_custom_ips(self):
        """Test generating multi-Marvin config with custom IPs"""
        generator = OscarConfigGenerator()
        xml, port_map = generator.generate_multi_marvin(
            oscar_id="DistributedOscar",
            minion_port=1100,
            marvin_count=3,
            marvin_ips=['192.168.1.10', '192.168.1.20', '192.168.1.30']
        )
        
        assert port_map['Marvin1']['ip'] == '192.168.1.10'
        assert port_map['Marvin2']['ip'] == '192.168.1.20'
        assert port_map['Marvin3']['ip'] == '192.168.1.30'
    
    def test_generate_with_chaining(self):
        """Test generating chained Oscar configuration"""
        generator = OscarConfigGenerator()
        xml = generator.generate_with_chaining(
            oscar_id="SiteOscar",
            minion_port=1100,
            upstream_oscar_ip="regional.oscar.com",
            upstream_oscar_port=6200,
            chain_key="SITE-TO-REGIONAL"
        )
        
        assert 'SiteOscar' in xml
        assert 'regional.oscar.com' in xml
        assert 'Port="6200"' in xml
        assert 'Key="SITE-TO-REGIONAL"' in xml
    
    def test_generate_validates_xml(self):
        """Test that generated XML is valid"""
        import xml.etree.ElementTree as ET
        
        generator = OscarConfigGenerator()
        xml = generator.generate_basic("Test", 1100, [('localhost', 52001)])
        
        # Should parse without error
        root = ET.fromstring(xml)
        assert root.tag == 'Oscar'
        assert root.get('ID') == 'Test'


class TestOscarRoutingAnalyzer:
    """Test Oscar routing analysis"""
    
    def test_analyze_valid_config(self):
        """Test analyzing a valid Oscar configuration"""
        config = OscarConfig(
            oscar_id="TestOscar",
            incoming_minion=OscarConnection('0.0.0.0', 1100, 'incoming_minion'),
            incoming_marvin=None,
            target_connections=[
                OscarConnection('localhost', 52001, 'target_marvin')
            ],
            chained_oscars=[],
            downstream_oscars=[]
        )
        
        analyzer = OscarRoutingAnalyzer()
        analysis = analyzer.analyze_routing(config)
        
        assert analysis['listens_for_minions'] is True
        assert analysis['forwards_to_marvins'] == 1
        assert analysis['chained_to_oscar'] is False
        assert len(analysis['errors']) == 0
    
    def test_analyze_missing_incoming_connection(self):
        """Test analyzing Oscar with no incoming connection"""
        config = OscarConfig(
            oscar_id="BrokenOscar",
            incoming_minion=None,
            incoming_marvin=None,
            target_connections=[
                OscarConnection('localhost', 52001, 'target_marvin')
            ],
            chained_oscars=[],
            downstream_oscars=[]
        )
        
        analyzer = OscarRoutingAnalyzer()
        analysis = analyzer.analyze_routing(config)
        
        assert len(analysis['errors']) > 0
        assert any('IncomingMinionConnection' in err for err in analysis['errors'])
    
    def test_analyze_no_targets(self):
        """Test analyzing Oscar with no target connections"""
        config = OscarConfig(
            oscar_id="NoTargetsOscar",
            incoming_minion=OscarConnection('0.0.0.0', 1100, 'incoming_minion'),
            incoming_marvin=None,
            target_connections=[],
            chained_oscars=[],
            downstream_oscars=[]
        )
        
        analyzer = OscarRoutingAnalyzer()
        analysis = analyzer.analyze_routing(config)
        
        assert len(analysis['warnings']) > 0
        assert any('not be forwarded' in warn for warn in analysis['warnings'])
    
    def test_analyze_port_conflict(self):
        """Test detecting port conflicts"""
        config = OscarConfig(
            oscar_id="ConflictOscar",
            incoming_minion=OscarConnection('0.0.0.0', 1100, 'incoming_minion'),
            incoming_marvin=None,
            target_connections=[
                OscarConnection('localhost', 1100, 'target_marvin')  # Same port!
            ],
            chained_oscars=[],
            downstream_oscars=[]
        )
        
        analyzer = OscarRoutingAnalyzer()
        analysis = analyzer.analyze_routing(config)
        
        assert len(analysis['errors']) > 0
        assert any('Port conflict' in err for err in analysis['errors'])
    
    def test_validate_minion_oscar_connection(self):
        """Test validating Minion to Oscar connection"""
        config = OscarConfig(
            oscar_id="TestOscar",
            incoming_minion=OscarConnection('0.0.0.0', 1100, 'incoming_minion'),
            incoming_marvin=None,
            target_connections=[],
            chained_oscars=[],
            downstream_oscars=[]
        )
        
        analyzer = OscarRoutingAnalyzer()
        
        # Valid connection
        errors = analyzer.validate_minion_oscar_connection(1100, config)
        assert len(errors) == 0
        
        # Invalid connection (wrong port)
        errors = analyzer.validate_minion_oscar_connection(1200, config)
        assert len(errors) > 0
        assert any('port' in err.lower() for err in errors)
    
    def test_analyze_chained_oscar(self):
        """Test analyzing chained Oscar configuration"""
        config = OscarConfig(
            oscar_id="SiteOscar",
            incoming_minion=OscarConnection('0.0.0.0', 1100, 'incoming_minion'),
            incoming_marvin=None,
            target_connections=[],
            chained_oscars=[
                OscarConnection('regional.oscar.com', 6200, 'oscar_chain', key='KEY')
            ],
            downstream_oscars=[]
        )
        
        analyzer = OscarRoutingAnalyzer()
        analysis = analyzer.analyze_routing(config)
        
        assert analysis['chained_to_oscar'] is True
        assert len(analysis['warnings']) == 0  # Chained Oscar counts as a target


class TestOscarConnection:
    """Test OscarConnection dataclass"""
    
    def test_connection_string_representation(self):
        """Test string representation of connection"""
        conn = OscarConnection('192.168.1.100', 52001, 'target_marvin')
        assert str(conn) == '192.168.1.100:52001'
    
    def test_connection_with_key(self):
        """Test connection with authentication key"""
        conn = OscarConnection(
            '10.0.0.1',
            6200,
            'oscar_chain',
            key='SECRET_KEY'
        )
        assert conn.key == 'SECRET_KEY'
        assert conn.connection_type == 'oscar_chain'


class TestOscarConfig:
    """Test OscarConfig dataclass"""
    
    def test_config_string_representation(self):
        """Test string representation of config"""
        config = OscarConfig(
            oscar_id="TestOscar",
            incoming_minion=OscarConnection('0.0.0.0', 1100, 'incoming_minion'),
            incoming_marvin=None,
            target_connections=[
                OscarConnection('localhost', 52001, 'target_marvin'),
                OscarConnection('localhost', 52002, 'target_marvin')
            ],
            chained_oscars=[],
            downstream_oscars=[]
        )
        
        str_repr = str(config)
        assert 'TestOscar' in str_repr
        assert '0.0.0.0:1100' in str_repr
        assert 'Target Marvins: 2' in str_repr


class TestEndToEndWorkflow:
    """Test complete Oscar configuration workflows"""
    
    def test_generate_parse_analyze_cycle(self, tmp_path):
        """Test generating, parsing, and analyzing a config"""
        # Generate
        generator = OscarConfigGenerator()
        xml = generator.generate_basic(
            oscar_id="E2EOscar",
            minion_port=1100,
            marvin_targets=[('localhost', 52001)]
        )
        
        # Write to file
        config_file = tmp_path / "oscar.xml"
        config_file.write_text(xml)
        
        # Parse
        parser = OscarConfigParser()
        config = parser.parse(config_file)
        
        # Analyze
        analyzer = OscarRoutingAnalyzer()
        analysis = analyzer.analyze_routing(config)
        
        assert analysis['listens_for_minions'] is True
        assert analysis['forwards_to_marvins'] == 1
        assert len(analysis['errors']) == 0
    
    def test_multi_marvin_workflow(self, tmp_path):
        """Test complete workflow for multi-Marvin setup"""
        generator = OscarConfigGenerator()
        xml, port_map = generator.generate_multi_marvin(
            oscar_id="Production",
            minion_port=1100,
            marvin_count=5,
            marvin_ips=['10.0.0.10', '10.0.0.20', '10.0.0.30']
        )
        
        # Write and parse
        config_file = tmp_path / "oscar.xml"
        config_file.write_text(xml)
        
        parser = OscarConfigParser()
        config = parser.parse(config_file)
        
        assert len(config.target_connections) == 5
        assert config.target_connections[0].ip == '10.0.0.10'
        assert config.target_connections[0].port == 52001
        assert config.target_connections[4].port == 52005
        
        # Analyze
        analyzer = OscarRoutingAnalyzer()
        analysis = analyzer.analyze_routing(config)
        assert analysis['forwards_to_marvins'] == 5
