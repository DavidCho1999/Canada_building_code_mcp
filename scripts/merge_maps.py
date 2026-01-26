#!/usr/bin/env python3
"""
Merge all maps/*.json into a single file for ChatGPT GPTs Knowledge Base.

Usage:
    python scripts/merge_maps.py

Output:
    combined_map.json (in project root)

Note: This file should NOT be committed to git.
      It's a derived artifact that can be regenerated from maps/*.json
"""

import json
from pathlib import Path
from datetime import datetime


def merge_maps():
    """Merge all map files into one combined JSON."""

    maps_dir = Path(__file__).parent.parent / "maps"
    output_file = Path(__file__).parent.parent / "combined_map.json"

    # Collect all map files
    map_files = sorted(maps_dir.glob("*.json"))

    if not map_files:
        print("Error: No map files found in maps/")
        return

    print(f"Found {len(map_files)} map files:")

    combined = {
        "generated": datetime.now().isoformat(),
        "description": "Canadian Building Codes - Combined Map for GPTs Knowledge Base",
        "usage": {
            "search": "Find sections by keywords in the 'keywords' array",
            "reference": "Use 'id' for section reference, 'page' for PDF page number",
            "codes": "NBC=National, OBC=Ontario, BCBC=BC, ABC=Alberta, QCC=Quebec, etc."
        },
        "codes": {}
    }

    total_sections = 0

    for map_file in map_files:
        code_name = map_file.stem  # e.g., "NBC2025", "OBC_Vol1"

        with open(map_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        section_count = len(data.get("sections", []))
        total_sections += section_count

        print(f"  - {code_name}: {section_count:,} sections")

        # Add to combined
        combined["codes"][code_name] = {
            "code": data.get("code", code_name),
            "version": data.get("version", ""),
            "source_pdf": data.get("source_pdf", {}).get("filename", ""),
            "section_count": section_count,
            "sections": data.get("sections", [])
        }

    # Add summary
    combined["summary"] = {
        "total_codes": len(map_files),
        "total_sections": total_sections,
        "codes_list": list(combined["codes"].keys())
    }

    # Write combined file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    file_size = output_file.stat().st_size / (1024 * 1024)  # MB

    print(f"\nOutput: {output_file}")
    print(f"Total: {total_sections:,} sections from {len(map_files)} codes")
    print(f"Size: {file_size:.1f} MB")
    print("\nNext steps:")
    print("  1. Go to ChatGPT -> Explore GPTs -> Create")
    print("  2. Upload combined_map.json to Knowledge")
    print("  3. Use the system prompt from docs/GPT_SYSTEM_PROMPT.md")


if __name__ == "__main__":
    merge_maps()
