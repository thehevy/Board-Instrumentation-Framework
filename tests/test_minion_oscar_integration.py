"""
Tests for Minion to Oscar integration
"""

import pytest
from pathlib import Path
import tempfile
from biff_agents_core.utils.minion_oscar_integration import (
    MinionConfigParser,
    MinionOscarIntegration,
    MinionNamespaceAnalyzer,
    MinionNamespace
)


class TestMinionConfigParser:
    """Test Minion configuration parsing"""
    
    def test_parse_simple_namespace(self, tmp_path):
        """Test parsing a simple namespace"""
        config_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>TestNamespace</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
    <Collector ID="cpu.usage" Frequency="500">
      <Executable>Collectors\\CPU.py</Executable>
      <Param>GetCPU_Percentage</Param>
    </Collector>
  </Namespace>
</Minion>"""
        
        config_file = tmp_path / "minion.xml"
        config_file.write_text(config_xml)
        
        parser = MinionConfigParser()
        namespaces = parser.parse(config_file)
        
        assert len(namespaces) == 1
        ns = namespaces[0]
        assert ns.name == "TestNamespace"
        assert ns.target_ip == "localhost"
        assert ns.target_port == 1100
        assert ns.default_frequency == 1000
        assert len(ns.collectors) == 1
        assert ns.collectors[0]['id'] == "cpu.usage"
    
    def test_parse_multiple_namespaces(self, tmp_path):
        """Test parsing multiple namespaces"""
        config_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>System</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="192.168.1.100" PORT="1100"/>
    <Collector ID="cpu" Frequency="500">
      <Executable>CPU.py</Executable>
    </Collector>
  </Namespace>
  <Namespace>
    <Name>Network</Name>
    <DefaultFrequency>2000</DefaultFrequency>
    <TargetConnection IP="192.168.1.100" PORT="1100"/>
    <Collector ID="bandwidth">
      <Executable>Network.py</Executable>
    </Collector>
  </Namespace>
</Minion>"""
        
        config_file = tmp_path / "minion.xml"
        config_file.write_text(config_xml)
        
        parser = MinionConfigParser()
        namespaces = parser.parse(config_file)
        
        assert len(namespaces) == 2
        assert namespaces[0].name == "System"
        assert namespaces[1].name == "Network"
        assert namespaces[0].default_frequency == 1000
        assert namespaces[1].default_frequency == 2000
    
    def test_parse_with_actors(self, tmp_path):
        """Test parsing namespace with actors"""
        config_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>TestNS</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
    <Actor ID="restart_service">
      <Executable>restart.sh</Executable>
      <Param>nginx</Param>
    </Actor>
  </Namespace>
</Minion>"""
        
        config_file = tmp_path / "minion.xml"
        config_file.write_text(config_xml)
        
        parser = MinionConfigParser()
        namespaces = parser.parse(config_file)
        
        assert len(namespaces[0].actors) == 1
        assert namespaces[0].actors[0]['id'] == "restart_service"


class TestMinionOscarIntegration:
    """Test Minion to Oscar integration"""
    
    def test_generate_oscar_from_single_namespace(self, tmp_path):
        """Test generating Oscar config from single namespace"""
        config_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>Production</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="192.168.1.50" PORT="1100"/>
    <Collector ID="cpu">
      <Executable>CPU.py</Executable>
    </Collector>
  </Namespace>
</Minion>"""
        
        config_file = tmp_path / "minion.xml"
        config_file.write_text(config_xml)
        
        integration = MinionOscarIntegration()
        oscar_configs = integration.generate_oscar_from_minion(
            config_file,
            marvin_ips=['192.168.1.100']
        )
        
        assert 'Production' in oscar_configs
        oscar_xml = oscar_configs['Production']
        assert 'Oscar_Production' in oscar_xml
        assert 'PORT="1100"' in oscar_xml
        assert 'IP="192.168.1.100"' in oscar_xml
        assert 'PORT="52001"' in oscar_xml
    
    def test_generate_unified_oscar(self, tmp_path):
        """Test generating single Oscar for multiple namespaces"""
        config_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>System</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
    <Collector ID="cpu"><Executable>CPU.py</Executable></Collector>
  </Namespace>
  <Namespace>
    <Name>Network</Name>
    <DefaultFrequency>2000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
    <Collector ID="bandwidth"><Executable>Network.py</Executable></Collector>
  </Namespace>
</Minion>"""
        
        config_file = tmp_path / "minion.xml"
        config_file.write_text(config_xml)
        
        integration = MinionOscarIntegration()
        oscar_xml, port_map = integration.generate_unified_oscar(
            config_file,
            oscar_id="UnifiedOscar",
            marvin_count=2
        )
        
        assert 'UnifiedOscar' in oscar_xml
        assert 'PORT="1100"' in oscar_xml
        assert len(port_map) == 2
        assert port_map['Marvin1']['port'] == 52001
        assert port_map['Marvin2']['port'] == 52002
    
    def test_generate_unified_fails_different_ports(self, tmp_path):
        """Test that unified generation fails if namespaces target different ports"""
        config_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>NS1</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
  </Namespace>
  <Namespace>
    <Name>NS2</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1200"/>
  </Namespace>
</Minion>"""
        
        config_file = tmp_path / "minion.xml"
        config_file.write_text(config_xml)
        
        integration = MinionOscarIntegration()
        
        with pytest.raises(ValueError, match="must target the same Oscar port"):
            integration.generate_unified_oscar(config_file)
    
    def test_validate_minion_oscar_routing(self, tmp_path):
        """Test validating Minion → Oscar routing"""
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
        
        minion_file = tmp_path / "minion.xml"
        oscar_file = tmp_path / "oscar.xml"
        minion_file.write_text(minion_xml)
        oscar_file.write_text(oscar_xml)
        
        integration = MinionOscarIntegration()
        errors = integration.validate_minion_oscar_routing(minion_file, oscar_file)
        
        assert len(errors) == 0
    
    def test_validate_detects_port_mismatch(self, tmp_path):
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
        
        minion_file = tmp_path / "minion.xml"
        oscar_file = tmp_path / "oscar.xml"
        minion_file.write_text(minion_xml)
        oscar_file.write_text(oscar_xml)
        
        integration = MinionOscarIntegration()
        errors = integration.validate_minion_oscar_routing(minion_file, oscar_file)
        
        assert len(errors) > 0
        assert any('port' in err.lower() for err in errors)
    
    def test_validate_detects_missing_targets(self, tmp_path):
        """Test validation detects Oscar with no targets"""
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
</Oscar>"""
        
        minion_file = tmp_path / "minion.xml"
        oscar_file = tmp_path / "oscar.xml"
        minion_file.write_text(minion_xml)
        oscar_file.write_text(oscar_xml)
        
        integration = MinionOscarIntegration()
        errors = integration.validate_minion_oscar_routing(minion_file, oscar_file)
        
        assert len(errors) > 0
        assert any('TargetConnections' in err for err in errors)
    
    def test_generate_deployment_guide(self, tmp_path):
        """Test generating deployment guide"""
        minion_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>Production</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="192.168.1.50" PORT="1100"/>
    <Collector ID="cpu"><Executable>CPU.py</Executable></Collector>
    <Actor ID="restart"><Executable>restart.sh</Executable></Actor>
  </Namespace>
</Minion>"""
        
        config_file = tmp_path / "minion.xml"
        config_file.write_text(minion_xml)
        
        integration = MinionOscarIntegration()
        oscar_xml, port_map = integration.generate_unified_oscar(config_file, marvin_count=2)
        
        guide = integration.generate_deployment_guide(config_file, oscar_xml, port_map)
        
        assert '# BIFF Deployment Guide' in guide
        assert 'Production' in guide
        assert 'Collectors: 1' in guide
        assert 'Actors: 1' in guide
        assert 'Marvin1' in guide
        assert 'Marvin2' in guide
        assert 'python Oscar.py' in guide
        assert 'python Minion.py' in guide


class TestMinionNamespaceAnalyzer:
    """Test Minion namespace analysis"""
    
    def test_analyze_simple_config(self, tmp_path):
        """Test analyzing a simple configuration"""
        config_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>NS1</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
    <Collector ID="cpu"><Executable>CPU.py</Executable></Collector>
    <Collector ID="mem"><Executable>Memory.py</Executable></Collector>
  </Namespace>
</Minion>"""
        
        config_file = tmp_path / "minion.xml"
        config_file.write_text(config_xml)
        
        analyzer = MinionNamespaceAnalyzer()
        analysis = analyzer.analyze_namespaces(config_file)
        
        assert analysis['namespace_count'] == 1
        assert analysis['unique_targets'] == 1
        assert analysis['total_collectors'] == 2
        assert 'localhost:1100' in analysis['targets']
    
    def test_analyze_multiple_targets(self, tmp_path):
        """Test analyzing config with multiple targets"""
        config_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>NS1</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="oscar1.local" PORT="1100"/>
    <Collector ID="cpu"><Executable>CPU.py</Executable></Collector>
  </Namespace>
  <Namespace>
    <Name>NS2</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="oscar2.local" PORT="1100"/>
    <Collector ID="mem"><Executable>Memory.py</Executable></Collector>
  </Namespace>
</Minion>"""
        
        config_file = tmp_path / "minion.xml"
        config_file.write_text(config_xml)
        
        analyzer = MinionNamespaceAnalyzer()
        analysis = analyzer.analyze_namespaces(config_file)
        
        assert analysis['namespace_count'] == 2
        assert analysis['unique_targets'] == 2
        assert 'oscar1.local:1100' in analysis['targets']
        assert 'oscar2.local:1100' in analysis['targets']
    
    def test_analyze_high_frequency_collectors(self, tmp_path):
        """Test detecting high-frequency collectors"""
        config_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>HighFreq</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
    <Collector ID="fast" Frequency="100">
      <Executable>Fast.py</Executable>
    </Collector>
    <Collector ID="normal" Frequency="1000">
      <Executable>Normal.py</Executable>
    </Collector>
  </Namespace>
</Minion>"""
        
        config_file = tmp_path / "minion.xml"
        config_file.write_text(config_xml)
        
        analyzer = MinionNamespaceAnalyzer()
        analysis = analyzer.analyze_namespaces(config_file)
        
        assert len(analysis['high_frequency_collectors']) == 1
        assert analysis['high_frequency_collectors'][0]['collector'] == 'fast'
        assert analysis['high_frequency_collectors'][0]['frequency'] == 100
    
    def test_analyze_averages(self, tmp_path):
        """Test calculating averages"""
        config_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>NS1</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
    <Collector ID="c1"><Executable>C1.py</Executable></Collector>
    <Collector ID="c2"><Executable>C2.py</Executable></Collector>
    <Collector ID="c3"><Executable>C3.py</Executable></Collector>
  </Namespace>
  <Namespace>
    <Name>NS2</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="localhost" PORT="1100"/>
    <Collector ID="c4"><Executable>C4.py</Executable></Collector>
  </Namespace>
</Minion>"""
        
        config_file = tmp_path / "minion.xml"
        config_file.write_text(config_xml)
        
        analyzer = MinionNamespaceAnalyzer()
        analysis = analyzer.analyze_namespaces(config_file)
        
        assert analysis['avg_collectors_per_namespace'] == 2.0


class TestEndToEndIntegration:
    """Test complete integration workflows"""
    
    def test_complete_workflow(self, tmp_path):
        """Test complete Minion → Oscar workflow"""
        # Create Minion config
        minion_xml = """<?xml version="1.0"?>
<Minion>
  <Namespace>
    <Name>Production</Name>
    <DefaultFrequency>1000</DefaultFrequency>
    <TargetConnection IP="192.168.1.50" PORT="1100"/>
    <Collector ID="cpu.usage" Frequency="500">
      <Executable>CPU.py</Executable>
      <Param>GetCPU_Percentage</Param>
    </Collector>
    <Collector ID="memory.usage">
      <Executable>Memory.py</Executable>
      <Param>GetMemoryUsage</Param>
    </Collector>
  </Namespace>
</Minion>"""
        
        minion_file = tmp_path / "MinionConfig.xml"
        minion_file.write_text(minion_xml)
        
        # Generate Oscar config
        integration = MinionOscarIntegration()
        oscar_xml, port_map = integration.generate_unified_oscar(
            minion_file,
            oscar_id="ProductionOscar",
            marvin_count=1
        )
        
        # Save Oscar config
        oscar_file = tmp_path / "OscarConfig.xml"
        oscar_file.write_text(oscar_xml)
        
        # Validate routing
        errors = integration.validate_minion_oscar_routing(minion_file, oscar_file)
        assert len(errors) == 0
        
        # Generate deployment guide
        guide = integration.generate_deployment_guide(minion_file, oscar_xml, port_map)
        
        assert 'ProductionOscar' in oscar_xml
        assert 'Production' in guide
        assert 'cpu.usage' not in guide  # Collector details not in guide
        assert 'Collectors: 2' in guide
