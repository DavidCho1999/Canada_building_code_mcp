#!/usr/bin/env python3
"""Test script for Building Code MCP (without MCP SDK)"""

import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import only the core class (not the MCP decorators)
import importlib.util
spec = importlib.util.spec_from_file_location("mcp_core", Path(__file__).parent / "src" / "mcp_server.py")

# Read and exec only the class definition
with open(Path(__file__).parent / "src" / "mcp_server.py", 'r', encoding='utf-8') as f:
    code = f.read()

# Extract class and dependencies only (before MCP server setup)
exec_code = []
in_class = False
brace_count = 0

for line in code.split('\n'):
    # Skip MCP server setup section
    if '# MCP Server setup' in line or '# Create MCP server' in line:
        break
    exec_code.append(line)

exec('\n'.join(exec_code), globals())

# Now test
print("="*50)
print("Canadian Building Code MCP - Test")
print("="*50)

maps_dir = Path(__file__).parent / "maps"
mcp = BuildingCodeMCP(str(maps_dir))

print(f"\n1. list_codes()")
print("-"*30)
result = mcp.list_codes()
print(f"Total codes: {result['total_codes']}")
codes = [c['code'] for c in result['available_codes']]
print(f"Codes: {', '.join(codes[:8])}...")

print(f"\n2. search_code('fire separation', 'NBC')")
print("-"*30)
result = mcp.search_code('fire separation', 'NBC')
print(f"Found: {result['total_found']} sections")
for s in result['sections'][:5]:
    title = s['title'][:40] + '...' if len(s['title']) > 40 else s['title']
    print(f"  [{s['id']}] {title} (p.{s['page']})")

print(f"\n3. get_section('9.10.14', 'NBC')")
print("-"*30)
result = mcp.get_section('9.10.14', 'NBC')
if result:
    print(f"ID: {result['id']}")
    print(f"Title: {result['title']}")
    print(f"Page: {result['page']}")
    print(f"Keywords: {result.get('keywords', [])[:5]}")
else:
    print("Not found")

print(f"\n4. get_hierarchy('9.10', 'NBC')")
print("-"*30)
result = mcp.get_hierarchy('9.10', 'NBC')
parent = result.get('parent')
print(f"Parent: {parent['id'] if parent else 'None'}")
print(f"Children: {len(result.get('children', []))} sections")
children_sample = result.get('children', [])[:3]
for c in children_sample:
    print(f"  - {c['id']}: {c['title'][:30]}...")
print(f"Siblings: {len(result.get('siblings', []))} sections")

print("\n" + "="*50)
print("Test completed!")
print("="*50)
