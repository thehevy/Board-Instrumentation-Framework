#!/usr/bin/env python
"""Quick test of search functionality"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from biff_agents_core.utils.collector_discovery import CollectorDiscovery

biff_root = Path(__file__).parent.parent
discovery = CollectorDiscovery(biff_root)

print("=== Testing function search ===")
results = discovery.search_collectors(has_function='GetUsage')
print(f"Found {len(results)} collectors with 'GetUsage':")
for c in results:
    matching = [f.name for f in c.functions if 'getusage' in f.name.lower()]
    print(f"  {c.name}: {matching}")

print("\n=== Testing search_by_function ===")
results = discovery.search_by_function('GetUsage', exact=False)
print(f"Found {len(results)} collectors:")
for c in results:
    matching = [f.name for f in c.functions if 'getusage' in f.name.lower()]
    print(f"  {c.name}: {matching}")

print("\n=== Testing regex search ===")
results = discovery.regex_search(r'^Docker', search_in='name')
print(f"Found {len(results)} collectors starting with 'Docker':")
for c in results:
    print(f"  {c.name}")

print("\n=== Testing full-text search ===")
results = discovery.full_text_search('docker container')
print(f"Found {len(results)} results:")
for c, score in results:
    print(f"  {c.name}: {score:.1f}")
