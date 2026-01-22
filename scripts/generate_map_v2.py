#!/usr/bin/env python3
"""
Map Generator v2 for Canadian Building Codes
JSON-First approach: Directly parse Docling JSON output

Key improvements over v1:
- No MD parsing needed
- Accurate page numbers and bbox from JSON
- Division prefix for unique section IDs (A-1.1.1.1, B-1.1.1.1)
- TOC filtering via duplicate detection
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import Counter
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


# Building code stopwords
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
    'those', 'it', 'its', 'if', 'then', 'than', 'so', 'such', 'no', 'not',
    'only', 'same', 'other', 'into', 'over', 'under', 'after', 'before',
    'between', 'each', 'all', 'both', 'any', 'some', 'more', 'most', 'less',
    'least', 'own', 'up', 'down', 'out', 'off', 'about', 'also', 'just',
    'how', 'when', 'where', 'which', 'who', 'whom', 'what', 'why',
    # Building code specific
    'shall', 'must', 'except', 'unless', 'where', 'provided', 'required',
    'article', 'section', 'sentence', 'clause', 'subsection', 'part',
    'division', 'table', 'figure', 'note', 'appendix', 'annex',
    'accordance', 'compliance', 'requirement', 'provision', 'applicable',
    'apply', 'applies', 'applied', 'described', 'specified', 'permitted',
    'see', 'refer', 'reference', 'following', 'listed', 'contained',
    'include', 'including', 'includes', 'included', 'conform', 'conforms',
}


def extract_keywords(text: str, max_keywords: int = 15) -> List[str]:
    """Extract meaningful keywords using simple TF approach."""
    if not text:
        return []
    words = re.findall(r'[a-z][a-z0-9-]*[a-z0-9]|[a-z]', text.lower())
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    counter = Counter(words)
    return [word for word, _ in counter.most_common(max_keywords)]


def get_level_from_id(section_id: str) -> str:
    """Determine hierarchy level from ID pattern."""
    # Division A, B, C
    if re.match(r'^[A-C]$', section_id):
        return 'division'

    # Part pattern: A-Part 1, or just numeric start
    if 'Part' in section_id:
        return 'part'

    # Count dots for numeric IDs (after removing Division prefix)
    # A-1.1 → 1 dot → section
    numeric_part = re.sub(r'^[A-C]-', '', section_id)
    dots = numeric_part.count('.')

    if dots == 0:
        return 'part'  # Just "1" or "2"
    elif dots == 1:  # 1.1
        return 'section'
    elif dots == 2:  # 1.1.1
        return 'subsection'
    elif dots >= 3:  # 1.1.1.1
        return 'article'

    return 'unknown'


def get_parent_id(full_id: str) -> Optional[str]:
    """Calculate parent ID from full section ID."""
    # A-1.1.1.1 → A-1.1.1
    match = re.match(r'^([A-C]-)?(.*)', full_id)
    if match:
        prefix = match.group(1) or ''
        numeric = match.group(2)

        parts = numeric.split('.')
        if len(parts) > 1:
            parent_numeric = '.'.join(parts[:-1])
            return f"{prefix}{parent_numeric}"
    return None


def parse_docling_json(json_path: str) -> Dict:
    """
    Parse Docling JSON and extract sections with coordinates.

    Strategy:
    1. Track current Division from page_header AND section_header
    2. Extract section_header items with Division prefix
    3. Collect content text for keyword extraction
    4. Handle duplicates (keep larger page = filter TOC)
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    texts = data.get('texts', [])

    # Build page → Division mapping from multiple sources
    page_division = {}

    # 1. From page_header: "Division A", "Division B", etc.
    for item in texts:
        if item.get('label') == 'page_header':
            text = item.get('text', '')
            match = re.match(r'^Division\s+([A-C])$', text)
            if match:
                prov = item.get('prov', [{}])[0]
                page = prov.get('page_no', 0)
                page_division[page] = match.group(1)

    # 2. From page_footer: "Division A", "Division A 1-1", etc. (more consistent)
    for item in texts:
        if item.get('label') == 'page_footer':
            text = item.get('text', '')
            # Match "Division A", "Division A 1-1", "1-2 Division A", etc.
            match = re.search(r'Division\s+([A-C])', text)
            if match:
                prov = item.get('prov', [{}])[0]
                page = prov.get('page_no', 0)
                page_division[page] = match.group(1)

    # 3. From section_header: "Division A:" or "Division A" (standalone)
    # Only from content pages (page > 15)
    for item in texts:
        if item.get('label') == 'section_header':
            text = item.get('text', '')
            # Match both "Division A:" and standalone "Division A"
            match = re.match(r'^Division\s+([A-C])(?::|$)', text)
            if match:
                prov = item.get('prov', [{}])[0]
                page = prov.get('page_no', 0)
                # Skip TOC pages
                if page > 15:
                    page_division[page] = match.group(1)

    # Fill gaps: propagate Division forward until next change
    if page_division:
        sorted_pages = sorted(page_division.keys())
        max_page = max(sorted_pages) + 100

        filled_division = {}
        current_div = None

        for page in range(1, max_page):
            if page in page_division:
                current_div = page_division[page]
            filled_division[page] = current_div

        page_division = filled_division

    # Extract sections from section_headers
    sections = []
    seen_ids = {}  # Track seen IDs to filter duplicates

    # Also collect content for keywords
    current_section_idx = -1
    section_contents = []  # List of content strings per section

    # Pattern for numeric section IDs: "1.1.1.1. Title" or "A-1.1.1.1. Title"
    numeric_pattern = re.compile(r'^([A-C]-)?(\d+(?:\.\d+)*)\.\s*(.*)$')
    # Pattern for Part: "Part 1 Title" or "Part 1. Title"
    part_pattern = re.compile(r'^Part\s+(\d+)\.?\s*(.*)$', re.IGNORECASE)
    # Pattern for Appendix: "A-1.1.1.1. Title" (Appendix annotations)
    appendix_pattern = re.compile(r'^(A-\d+(?:\.\d+)*(?:\.\(\d+\))?)\s*(.*)$')

    for item in texts:
        label = item.get('label', '')
        text = item.get('text', '').strip()
        prov = item.get('prov', [{}])[0]
        page = prov.get('page_no', 0)
        bbox = prov.get('bbox', None)

        # Get current division for this page
        current_division = page_division.get(page, None)

        if label == 'section_header':
            section_id = None
            title = text

            # Try numeric pattern first
            match = numeric_pattern.match(text)
            if match:
                existing_prefix = match.group(1)  # May be None or "A-"
                numeric_id = match.group(2)
                title = match.group(3) or numeric_id

                # Build full ID with Division prefix
                if existing_prefix:
                    # Already has prefix (like Appendix A-1.1.1.1)
                    section_id = f"{existing_prefix}{numeric_id}"
                elif current_division:
                    section_id = f"{current_division}-{numeric_id}"
                else:
                    section_id = numeric_id

            # Try Part pattern
            elif part_pattern.match(text):
                match = part_pattern.match(text)
                part_num = match.group(1)
                title = match.group(2) or f"Part {part_num}"
                if current_division:
                    section_id = f"{current_division}-Part{part_num}"
                else:
                    section_id = f"Part{part_num}"

            # Division header itself
            elif text.startswith('Division') and ':' in text:
                # "Division A: Compliance..." → just "A"
                match = re.match(r'^Division\s+([A-C]):', text)
                if match:
                    section_id = match.group(1)
                    title = text

            # Skip if no valid ID extracted
            if not section_id:
                continue

            # Skip TOC entries (pages 1-15 typically)
            # But keep Division headers even if early
            if page < 15 and not re.match(r'^[A-C]$', section_id):
                continue

            # Duplicate handling: keep the one with larger page (skip TOC)
            if section_id in seen_ids:
                existing_page = seen_ids[section_id]['page']
                if page > existing_page:
                    # Update with this one (further in document = real content)
                    idx = seen_ids[section_id]['idx']
                    sections[idx] = {
                        "id": section_id,
                        "title": title,
                        "page": page,
                        "bbox": bbox,
                        "level": get_level_from_id(section_id),
                        "parent_id": get_parent_id(section_id),
                        "division": current_division,
                    }
                    seen_ids[section_id] = {'page': page, 'idx': idx}
                # else: keep existing (earlier, possibly real if this is index)
                continue

            # New section
            section = {
                "id": section_id,
                "title": title,
                "page": page,
                "bbox": bbox,
                "level": get_level_from_id(section_id),
                "parent_id": get_parent_id(section_id),
                "division": current_division,
            }
            seen_ids[section_id] = {'page': page, 'idx': len(sections)}
            sections.append(section)
            current_section_idx = len(sections) - 1
            section_contents.append("")

        # Collect content text for keywords
        elif label in ('text', 'list_item', 'paragraph') and current_section_idx >= 0:
            if current_section_idx < len(section_contents):
                section_contents[current_section_idx] += " " + text

    # Extract keywords for each section
    for i, section in enumerate(sections):
        if i < len(section_contents):
            section['keywords'] = extract_keywords(section_contents[i])
        else:
            section['keywords'] = []

    return sections, data


def generate_map(json_path: str, code_name: str = None, code_version: str = None) -> Dict:
    """Generate map JSON from Docling JSON output."""
    json_path = Path(json_path)

    # Auto-detect code name and version from filename
    if code_name is None:
        name = json_path.stem.upper()
        code_name = re.sub(r'[\d_].*$', '', name) or name

    if code_version is None:
        match = re.search(r'(\d{4})', json_path.stem)
        code_version = match.group(1) if match else "unknown"

    print(f"Parsing: {json_path.name}")
    print(f"Code: {code_name} {code_version}")

    sections, raw_data = parse_docling_json(str(json_path))
    print(f"Found {len(sections)} sections")

    # Get source PDF metadata
    origin = raw_data.get('origin', {})
    source_pdf = {
        "filename": origin.get('filename', ''),
    }

    # Build map structure
    map_data = {
        "code": code_name,
        "version": code_version,
        "generated": datetime.now().isoformat(),
        "source_pdf": source_pdf,
        "sections": []
    }

    # Convert sections to output format
    for section in sections:
        section_dict = {
            "id": section['id'],
            "title": section['title'],
            "page": section['page'],
            "level": section['level'],
        }

        if section.get('parent_id'):
            section_dict["parent_id"] = section['parent_id']

        if section.get('bbox'):
            section_dict["bbox"] = section['bbox']

        if section.get('keywords'):
            section_dict["keywords"] = section['keywords']

        if section.get('division'):
            section_dict["division"] = section['division']

        map_data["sections"].append(section_dict)

    return map_data


def main():
    parser = argparse.ArgumentParser(
        description="Generate Map JSON from Docling JSON output (v2)"
    )
    parser.add_argument(
        "input",
        help="Docling JSON file or directory containing JSON file"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file (default: maps/<code_name><version>.json)"
    )
    parser.add_argument(
        "--code", "-c",
        help="Code name (e.g., NBC, OBC). Auto-detected if not provided."
    )
    parser.add_argument(
        "--version", "-v",
        help="Code version (e.g., 2025). Auto-detected if not provided."
    )

    args = parser.parse_args()

    input_path = Path(args.input)

    # Find JSON file
    if input_path.is_dir():
        json_files = [f for f in input_path.glob("*.json")
                      if not f.name.endswith('_meta.json')]
        if not json_files:
            print(f"No JSON files found in {input_path}")
            return
        json_path = json_files[0]
    else:
        json_path = input_path

    # Generate map
    map_data = generate_map(str(json_path), args.code, args.version)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path("maps")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{map_data['code']}{map_data['version']}.json"

    # Save map
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(map_data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved: {output_path}")
    print(f"Sections: {len(map_data['sections'])}")

    # Show sample
    if map_data['sections']:
        print("\nSample sections:")
        for section in map_data['sections'][:5]:
            print(f"  {section['id']}: page {section['page']} - {section['title'][:40]}")

    # Show stats by division
    divisions = {}
    for s in map_data['sections']:
        div = s.get('division', 'None')
        divisions[div] = divisions.get(div, 0) + 1
    print(f"\nBy Division: {divisions}")


if __name__ == "__main__":
    main()
