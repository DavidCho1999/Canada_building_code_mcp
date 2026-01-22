#!/usr/bin/env python3
"""
Map Generator for User's Guides (Commentary-based documents)
Handles UGP4 (Structural Commentaries) and UGNECB (Energy Code Guide)

Different from v2 which handles Division A/B/C based building codes.
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import Counter
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


# Stopwords for keyword extraction
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
    'those', 'it', 'its', 'if', 'then', 'than', 'so', 'such', 'no', 'not',
    'only', 'same', 'other', 'into', 'over', 'under', 'after', 'before',
    'between', 'each', 'all', 'both', 'any', 'some', 'more', 'most', 'less',
    'shall', 'must', 'except', 'unless', 'provided', 'required',
    'article', 'section', 'sentence', 'clause', 'part', 'commentary',
    'see', 'refer', 'reference', 'following', 'example', 'figure', 'table',
}


def extract_keywords(text: str, max_keywords: int = 15) -> List[str]:
    """Extract meaningful keywords using simple TF approach."""
    if not text:
        return []
    words = re.findall(r'[a-z][a-z0-9-]*[a-z0-9]|[a-z]', text.lower())
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    counter = Counter(words)
    return [word for word, _ in counter.most_common(max_keywords)]


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    # Remove special characters, keep alphanumeric and spaces
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text.strip())
    # Remove multiple hyphens
    text = re.sub(r'-+', '-', text)
    return text[:50]  # Limit length


def parse_ugp4(json_path: str) -> List[Dict]:
    """
    Parse UGP4 (Structural Commentaries).
    Structure: Commentary A, B, C... with subsection titles.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    texts = data.get('texts', [])
    sections = []
    seen_ids = {}

    # Track current commentary
    current_commentary = None
    current_commentary_title = None
    current_section_idx = -1
    section_contents = []

    # Commentary pattern: "Commentary A", "Commentary B", etc.
    commentary_pattern = re.compile(r'^Commentary\s+([A-Z])(?:\s+(.+))?$')

    for item in texts:
        label = item.get('label', '')
        text = item.get('text', '').strip()
        prov = item.get('prov', [{}])[0]
        page = prov.get('page_no', 0)
        bbox = prov.get('bbox', None)

        # Skip early pages (TOC, intro)
        if page < 15:
            continue

        if label == 'section_header':
            # Check if it's a Commentary header
            match = commentary_pattern.match(text)
            if match:
                letter = match.group(1)
                title = match.group(2) or ""

                # Only create new commentary if letter changes
                if letter != current_commentary:
                    current_commentary = letter
                    current_commentary_title = title

                    section_id = f"Commentary-{letter}"
                    if section_id not in seen_ids:
                        section = {
                            "id": section_id,
                            "title": f"Commentary {letter}" + (f": {title}" if title else ""),
                            "page": page,
                            "level": "commentary",
                            "bbox": bbox,
                        }
                        seen_ids[section_id] = len(sections)
                        sections.append(section)
                        current_section_idx = len(sections) - 1
                        section_contents.append("")
                continue

            # Skip if no current commentary yet
            if not current_commentary:
                continue

            # Skip common non-content headers
            skip_patterns = [
                'Table of Contents', 'Notable Changes', 'References',
                'CANADIAN COMMISSION', 'NRCC-CONST', 'First Printing'
            ]
            if any(p in text for p in skip_patterns):
                continue

            # This is a subsection within the commentary
            slug = slugify(text)
            if not slug:
                continue

            section_id = f"{current_commentary}-{slug}"

            # Handle duplicates - keep later occurrence
            if section_id in seen_ids:
                existing_idx = seen_ids[section_id]
                existing_page = sections[existing_idx]['page']
                if page > existing_page:
                    sections[existing_idx] = {
                        "id": section_id,
                        "title": text,
                        "page": page,
                        "level": "subsection",
                        "parent_id": f"Commentary-{current_commentary}",
                        "bbox": bbox,
                    }
                continue

            section = {
                "id": section_id,
                "title": text,
                "page": page,
                "level": "subsection",
                "parent_id": f"Commentary-{current_commentary}",
                "bbox": bbox,
            }
            seen_ids[section_id] = len(sections)
            sections.append(section)
            current_section_idx = len(sections) - 1
            section_contents.append("")

        # Collect content for keywords
        elif label in ('text', 'list_item', 'paragraph') and current_section_idx >= 0:
            if current_section_idx < len(section_contents):
                section_contents[current_section_idx] += " " + text

    # Add keywords
    for i, section in enumerate(sections):
        if i < len(section_contents):
            section['keywords'] = extract_keywords(section_contents[i])
        else:
            section['keywords'] = []

    return sections, data


def parse_ugnecb(json_path: str) -> List[Dict]:
    """
    Parse UGNECB (Energy Code Guide).
    Structure: Commentary on Part X with Article references.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    texts = data.get('texts', [])
    sections = []
    seen_ids = {}

    current_part = None
    current_section_idx = -1
    section_contents = []

    # Pattern for Part headers in page headers/footers
    part_pattern = re.compile(r'Commentary on Part\s+(\d+)')
    # Pattern for Article references
    article_pattern = re.compile(r'\(Article\s+([\d.]+)\)')
    # Pattern for Examples
    example_pattern = re.compile(r'^Example\s+([\d-]+)')

    # First pass: identify Part boundaries from page headers
    page_to_part = {}
    for item in texts:
        if item.get('label') in ('page_header', 'section_header'):
            text = item.get('text', '')
            match = part_pattern.search(text)
            if match:
                prov = item.get('prov', [{}])[0]
                page = prov.get('page_no', 0)
                if page > 5:  # Skip TOC
                    page_to_part[page] = match.group(1)

    # Fill gaps
    if page_to_part:
        max_page = max(page_to_part.keys()) + 50
        current_p = None
        filled = {}
        for pg in range(1, max_page):
            if pg in page_to_part:
                current_p = page_to_part[pg]
            filled[pg] = current_p
        page_to_part = filled

    for item in texts:
        label = item.get('label', '')
        text = item.get('text', '').strip()
        prov = item.get('prov', [{}])[0]
        page = prov.get('page_no', 0)
        bbox = prov.get('bbox', None)

        # Skip early pages
        if page < 8:
            continue

        # Get current part from page mapping
        part_num = page_to_part.get(page)

        if label == 'section_header':
            # Skip Commentary on Part X headers (just page markers)
            if part_pattern.match(text):
                # Create Part entry if new
                if part_num and part_num != current_part:
                    current_part = part_num
                    section_id = f"Part{part_num}"
                    if section_id not in seen_ids:
                        section = {
                            "id": section_id,
                            "title": f"Part {part_num}",
                            "page": page,
                            "level": "part",
                            "bbox": bbox,
                        }
                        seen_ids[section_id] = len(sections)
                        sections.append(section)
                        current_section_idx = len(sections) - 1
                        section_contents.append("")
                continue

            # Skip common headers
            skip_patterns = [
                'Table of Contents', 'User\'s Guide', 'NRCC-CONST',
                'Energy', 'Introduction', 'Development', 'Overview',
                'Referenced Standards', 'Additional Information'
            ]
            if any(p in text for p in skip_patterns):
                continue

            if not part_num:
                continue

            # Check for Article reference in title
            article_match = article_pattern.search(text)
            example_match = example_pattern.match(text)

            if article_match:
                # Article-based section
                article_num = article_match.group(1)
                section_id = f"Part{part_num}-Article{article_num}"
                title = text
            elif example_match:
                # Example section
                example_num = example_match.group(1)
                section_id = f"Part{part_num}-Example{example_num}"
                title = text
            else:
                # General subsection
                slug = slugify(text)
                if not slug or len(slug) < 3:
                    continue
                section_id = f"Part{part_num}-{slug}"
                title = text

            # Handle duplicates
            if section_id in seen_ids:
                existing_idx = seen_ids[section_id]
                existing_page = sections[existing_idx]['page']
                if page > existing_page:
                    sections[existing_idx] = {
                        "id": section_id,
                        "title": title,
                        "page": page,
                        "level": "subsection",
                        "parent_id": f"Part{part_num}",
                        "bbox": bbox,
                    }
                continue

            section = {
                "id": section_id,
                "title": title,
                "page": page,
                "level": "subsection",
                "parent_id": f"Part{part_num}",
                "bbox": bbox,
            }
            seen_ids[section_id] = len(sections)
            sections.append(section)
            current_section_idx = len(sections) - 1
            section_contents.append("")

        # Collect content for keywords
        elif label in ('text', 'list_item', 'paragraph') and current_section_idx >= 0:
            if current_section_idx < len(section_contents):
                section_contents[current_section_idx] += " " + text

    # Add keywords
    for i, section in enumerate(sections):
        if i < len(section_contents):
            section['keywords'] = extract_keywords(section_contents[i])
        else:
            section['keywords'] = []

    return sections, data


def parse_iugp9(json_path: str) -> List[Dict]:
    """
    Parse IUGP9 (Illustrated User's Guide - Part 9).
    Structure: Section 9.x.x with subsections and examples.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    texts = data.get('texts', [])
    sections = []
    seen_ids = {}

    current_section_idx = -1
    section_contents = []

    # Pattern for Section headers like 9.1.1, 9.3.2.5, etc.
    section_pattern = re.compile(r'^(?:Section\s+)?(\d+\.\d+(?:\.\d+)*\.?)(?:\s+(.+))?$')
    # Pattern for Example
    example_pattern = re.compile(r'^Example\s*(\d+)', re.IGNORECASE)

    for item in texts:
        label = item.get('label', '')
        text = item.get('text', '').strip()
        prov = item.get('prov', [{}])[0]
        page = prov.get('page_no', 0)
        bbox = prov.get('bbox', None)

        # Skip early pages (TOC, intro before Part 9 content)
        if page < 26:
            continue

        if label == 'section_header':
            # Skip common non-content headers
            skip_patterns = [
                'Table of Contents', 'CANADIAN COMMISSION', 'NRCC-CONST',
                'Illustrated User', 'Housing and Small Buildings',
                'Division B', 'Standards Referenced', 'Notes to Table',
                'Notable Changes', 'Introduction'
            ]
            if any(p in text for p in skip_patterns):
                continue

            # Check for Section pattern
            section_match = section_pattern.match(text)
            example_match = example_pattern.match(text)

            if section_match:
                section_num = section_match.group(1).rstrip('.')
                title_part = section_match.group(2) or ""

                section_id = f"Section-{section_num}"
                title = f"Section {section_num}"
                if title_part:
                    title += f": {title_part}"

                # Determine level based on depth
                depth = section_num.count('.')
                if depth == 1:
                    level = "section"
                elif depth == 2:
                    level = "subsection"
                else:
                    level = "article"

                # Find parent
                parts = section_num.split('.')
                parent_id = None
                if len(parts) > 2:
                    parent_num = '.'.join(parts[:-1])
                    parent_id = f"Section-{parent_num}"

            elif example_match:
                example_num = example_match.group(1)
                section_id = f"Example-{example_num}"
                title = text
                level = "example"
                parent_id = None

            else:
                # General topic header
                slug = slugify(text)
                if not slug or len(slug) < 3:
                    continue
                section_id = f"Topic-{slug}"
                title = text
                level = "topic"
                parent_id = None

            # Handle duplicates - keep later occurrence with more content
            if section_id in seen_ids:
                existing_idx = seen_ids[section_id]
                existing_page = sections[existing_idx]['page']
                if page > existing_page:
                    sections[existing_idx].update({
                        "title": title,
                        "page": page,
                        "bbox": bbox,
                    })
                continue

            section = {
                "id": section_id,
                "title": title,
                "page": page,
                "level": level,
                "bbox": bbox,
            }
            if parent_id:
                section["parent_id"] = parent_id

            seen_ids[section_id] = len(sections)
            sections.append(section)
            current_section_idx = len(sections) - 1
            section_contents.append("")

        # Collect content for keywords
        elif label in ('text', 'list_item', 'paragraph') and current_section_idx >= 0:
            if current_section_idx < len(section_contents):
                section_contents[current_section_idx] += " " + text

    # Add keywords
    for i, section in enumerate(sections):
        if i < len(section_contents):
            section['keywords'] = extract_keywords(section_contents[i])
        else:
            section['keywords'] = []

    return sections, data


def generate_map(json_path: str, guide_type: str, code_name: str = None, code_version: str = None) -> Dict:
    """Generate map JSON from Docling JSON output."""
    json_path = Path(json_path)

    # Auto-detect from filename
    if code_name is None:
        name = json_path.stem.upper()
        code_name = re.sub(r'[\d_].*$', '', name) or name

    if code_version is None:
        match = re.search(r'(\d{4})', json_path.stem)
        code_version = match.group(1) if match else "unknown"

    print(f"Parsing: {json_path.name}")
    print(f"Guide: {code_name} {code_version} (type: {guide_type})")

    # Parse based on guide type
    if guide_type == 'ugp4':
        sections, raw_data = parse_ugp4(str(json_path))
    elif guide_type == 'ugnecb':
        sections, raw_data = parse_ugnecb(str(json_path))
    elif guide_type == 'iugp9':
        sections, raw_data = parse_iugp9(str(json_path))
    else:
        raise ValueError(f"Unknown guide type: {guide_type}")

    print(f"Found {len(sections)} sections")

    # Get source PDF metadata
    origin = raw_data.get('origin', {})
    source_pdf = {"filename": origin.get('filename', '')}

    # Build map
    map_data = {
        "code": code_name,
        "version": code_version,
        "document_type": "guide",  # Mark as guide!
        "generated": datetime.now().isoformat(),
        "source_pdf": source_pdf,
        "sections": sections
    }

    return map_data


def main():
    parser = argparse.ArgumentParser(
        description="Generate Map JSON for User's Guides (Commentary-based)"
    )
    parser.add_argument(
        "input",
        help="Docling JSON file or directory"
    )
    parser.add_argument(
        "--type", "-t",
        required=True,
        choices=['ugp4', 'ugnecb', 'iugp9'],
        help="Guide type: ugp4 (Structural Commentaries), ugnecb (Energy Guide), or iugp9 (Part 9 User's Guide)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file"
    )
    parser.add_argument(
        "--code", "-c",
        help="Code name (e.g., UGP4)"
    )
    parser.add_argument(
        "--version", "-v",
        help="Version (e.g., 2020)"
    )

    args = parser.parse_args()

    input_path = Path(args.input)

    # Find JSON file
    if input_path.is_dir():
        json_files = [f for f in input_path.glob("*.json") if not f.name.endswith('_meta.json')]
        if not json_files:
            print(f"No JSON files found in {input_path}")
            return
        json_path = json_files[0]
    else:
        json_path = input_path

    # Generate map
    map_data = generate_map(str(json_path), args.type, args.code, args.version)

    # Output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path("maps")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{map_data['code']}_{map_data['version']}.json"

    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(map_data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved: {output_path}")
    print(f"Sections: {len(map_data['sections'])}")

    # Show samples
    if map_data['sections']:
        print("\nSample sections:")
        for section in map_data['sections'][:10]:
            print(f"  {section['id']}: page {section['page']} - {section['title'][:50]}")

    # Stats by level
    levels = {}
    for s in map_data['sections']:
        lvl = s.get('level', 'unknown')
        levels[lvl] = levels.get(lvl, 0) + 1
    print(f"\nBy level: {levels}")


if __name__ == "__main__":
    main()
