#!/usr/bin/env python3
"""
Generate Example Dashboards for BIFF Agents

Creates complete dashboard configurations from example Minion configs
to showcase different use cases and widget combinations.

Phase 3 Week 8 Day 5
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from biff_agents_marvin.composers.monitoring_composer import MonitoringDashboardComposer
from biff_agents_marvin.composers.performance_composer import PerformanceDashboardComposer
from biff_agents_marvin.utils.minion_discovery import MinionDataSourceDiscovery


def generate_server_monitoring_dashboard():
    """Generate Example 1: Server Monitoring Dashboard"""
    print("=" * 70)
    print("Example 1: Server Monitoring Dashboard")
    print("=" * 70)
    
    config_path = Path("examples/01_server_monitoring_config.xml")
    output_path = Path("examples/dashboards/01_server_monitoring")
    
    if not config_path.exists():
        print(f"⚠️  Config not found: {config_path}")
        return False
    
    try:
        # Use monitoring composer for comprehensive server view
        composer = MonitoringDashboardComposer(str(config_path))
        result = composer.generate_dashboard(str(output_path))
        
        print(f"\n✅ Generated Server Monitoring Dashboard")
        print(f"   Location: {output_path}")
        print(f"   Files: {len(result.get('tabs', [])) + 1}")
        print(f"   - Overview tab: CPU and memory gauges")
        print(f"   - Details tab: Network and disk charts")
        print(f"   - Status tab: System health indicators")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def generate_application_performance_dashboard():
    """Generate Example 2: Application Performance Dashboard"""
    print("\n" + "=" * 70)
    print("Example 2: Application Performance Dashboard")
    print("=" * 70)
    
    config_path = Path("examples/02_application_performance_config.xml")
    output_path = Path("examples/dashboards/02_application_performance")
    
    if not config_path.exists():
        print(f"⚠️  Config not found: {config_path}")
        return False
    
    try:
        # Use performance composer for app metrics
        composer = PerformanceDashboardComposer(str(config_path))
        result = composer.generate_dashboard(str(output_path))
        
        print(f"\n✅ Generated Application Performance Dashboard")
        print(f"   Location: {output_path}")
        print(f"   Files: {len(result.get('tabs', [])) + 1}")
        print(f"   - Request rates and response times")
        print(f"   - Error rate tracking")
        print(f"   - Database and cache metrics")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def generate_iot_sensors_dashboard():
    """Generate Example 3: IoT Sensors Dashboard"""
    print("\n" + "=" * 70)
    print("Example 3: IoT Sensors Dashboard")
    print("=" * 70)
    
    config_path = Path("examples/03_iot_sensors_config.xml")
    output_path = Path("examples/dashboards/03_iot_sensors")
    
    if not config_path.exists():
        print(f"⚠️  Config not found: {config_path}")
        return False
    
    try:
        composer = MonitoringDashboardComposer(str(config_path))
        result = composer.generate_dashboard(str(output_path))
        
        print(f"\n✅ Generated IoT Sensors Dashboard")
        print(f"   Location: {output_path}")
        print(f"   Files: {len(result.get('tabs', [])) + 1}")
        print(f"   - Temperature and humidity gauges")
        print(f"   - Motion detection LEDs")
        print(f"   - Power consumption charts")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def generate_network_operations_dashboard():
    """Generate Example 4: Network Operations Dashboard"""
    print("\n" + "=" * 70)
    print("Example 4: Network Operations Dashboard")
    print("=" * 70)
    
    config_path = Path("examples/04_network_operations_config.xml")
    output_path = Path("examples/dashboards/04_network_operations")
    
    if not config_path.exists():
        print(f"⚠️  Config not found: {config_path}")
        return False
    
    try:
        composer = PerformanceDashboardComposer(str(config_path))
        result = composer.generate_dashboard(str(output_path))
        
        print(f"\n✅ Generated Network Operations Dashboard")
        print(f"   Location: {output_path}")
        print(f"   Files: {len(result.get('tabs', [])) + 1}")
        print(f"   - Interface bandwidth and packet rates")
        print(f"   - Connection statistics")
        print(f"   - Firewall and DNS metrics")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def generate_containers_dashboard():
    """Generate Example 5: Container & Microservices Dashboard"""
    print("\n" + "=" * 70)
    print("Example 5: Container & Microservices Dashboard")
    print("=" * 70)
    
    config_path = Path("examples/05_containers_config.xml")
    output_path = Path("examples/dashboards/05_containers")
    
    if not config_path.exists():
        print(f"⚠️  Config not found: {config_path}")
        return False
    
    try:
        composer = MonitoringDashboardComposer(str(config_path))
        result = composer.generate_dashboard(str(output_path))
        
        print(f"\n✅ Generated Container Dashboard")
        print(f"   Location: {output_path}")
        print(f"   Files: {len(result.get('tabs', [])) + 1}")
        print(f"   - Container CPU and memory usage")
        print(f"   - Network throughput per container")
        print(f"   - Container status indicators")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def main():
    """Generate all example dashboards"""
    print("\n" + "=" * 70)
    print("BIFF Agents - Example Dashboard Generator")
    print("Phase 3 Week 8 Day 5")
    print("=" * 70)
    
    # Ensure output directory exists
    output_base = Path("examples/dashboards")
    output_base.mkdir(parents=True, exist_ok=True)
    
    results = []
    results.append(("Server Monitoring", generate_server_monitoring_dashboard()))
    results.append(("Application Performance", generate_application_performance_dashboard()))
    results.append(("IoT Sensors", generate_iot_sensors_dashboard()))
    results.append(("Network Operations", generate_network_operations_dashboard()))
    results.append(("Container & Microservices", generate_containers_dashboard()))
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print("=" * 70)
    print(f"Generated: {passed}/{total} dashboards")
    print(f"Location: examples/dashboards/")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 All example dashboards generated successfully!")
        print("\nNext steps:")
        print("1. Copy a dashboard directory to your Marvin workspace")
        print("2. Update IP addresses in App.Config.xml")
        print("3. Launch Marvin: java -jar BIFF.Marvin.jar -i App.Config.xml")
    else:
        print(f"\n⚠️  {total - passed} dashboard(s) failed to generate")
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
