#!/usr/bin/env python3
"""
Map Generator v2 for Canadian Building Codes
JSON-First approach: Directly parse Docling JSON output

Key improvements over v1:
- No MD parsing needed
- Accurate page numbers and bbox from JSON
- Division prefix for unique section IDs (A-1.1.1.1, B-1.1.1.1)
- TOC filtering via duplicate detection

v2.1 Updates:
- Table indexing: Parses tables from Docling output
- Table markdown: Converts tables to searchable markdown format
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


# ============================================
# Table Parsing Functions
# ============================================

# Regex pattern for Table IDs: "Table 4.1.5.3", "Table A-9.10.14.4", "Table D-1.1.2"
TABLE_ID_PATTERN = re.compile(
    r'Table\s+([A-D]-)?([\d]+(?:\.[\d]+)*(?:-[A-Z])?)',
    re.IGNORECASE
)

# Additional patterns for tables without "Table X.X.X" format
# "Forming Part of Sentence 3.3.1.5.(1)" or "Forming Part of Article 9.33.6.5."
FORMING_PART_PATTERN = re.compile(
    r'Forming Part of (Article|Sentences?)\s+([\d.()]+)',
    re.IGNORECASE
)

# "Detail EA-1", "Detail EB-2" (OBC Vol2 detail drawings)
DETAIL_PATTERN = re.compile(
    r'Detail\s+([A-Z]{1,2}-\d+)',
    re.IGNORECASE
)


def table_to_markdown(table: Dict, max_chars: int = 2000) -> str:
    """
    Convert Docling table data to markdown format.

    Args:
        table: Docling table object with 'data' containing grid
        max_chars: Maximum characters for markdown output

    Returns:
        Markdown formatted table string
    """
    data = table.get('data', {})

    # Use grid directly (preferred) or fall back to table_cells
    grid = data.get('grid', [])

    if not grid:
        return ""

    num_rows = len(grid)
    num_cols = len(grid[0]) if grid else 0

    if num_rows == 0 or num_cols == 0:
        return ""

    # Build markdown from grid
    lines = []
    for i, row in enumerate(grid):
        row_cells = []
        for cell in row:
            text = cell.get('text', '') if isinstance(cell, dict) else str(cell)
            text = text.replace('\n', ' ').replace('|', '/').strip()
            # Truncate long cell text
            if len(text) > 50:
                text = text[:47] + "..."
            row_cells.append(text if text else ' ')

        line = '| ' + ' | '.join(row_cells) + ' |'
        lines.append(line)
        if i == 0:  # Header separator after first row
            lines.append('|' + '---|' * len(row_cells))

    markdown = '\n'.join(lines)

    # Truncate if too long
    if len(markdown) > max_chars:
        markdown = markdown[:max_chars] + "\n...(truncated)"

    return markdown


def build_page_caption_map(texts: List[Dict]) -> Dict[int, List[Dict]]:
    """
    Build a mapping of page numbers to table caption elements.
    Checks both 'caption' AND 'section_header' labels for Table patterns.
    Also captures "Forming Part of" and "Detail" patterns.
    Includes bbox for proximity matching.

    Returns:
        Dict mapping page_no -> list of {text, table_id, title, bbox, ...}
    """
    page_captions = {}
    seen_table_ids_per_page = {}  # Track to avoid duplicates

    # Check both caption and section_header elements
    for t in texts:
        label = t.get('label', '')
        # Check both caption and section_header for Table patterns
        if label not in ('caption', 'section_header'):
            continue

        text = t.get('text', '')
        prov = t.get('prov', [{}])[0]
        page = prov.get('page_no', 0)
        bbox = prov.get('bbox', None)

        # Skip "Notes to Table" entries - these are not table captions
        if text.lower().startswith('notes to table'):
            continue

        table_id = None
        title = None
        is_continued = False

        # Pattern 1: Standard "Table X.X.X" pattern
        match = TABLE_ID_PATTERN.search(text)
        if match:
            prefix = match.group(1) or ''
            number = match.group(2)
            table_id = f"Table-{prefix}{number}"

            # Extract title
            title_start = match.end()
            title = text[title_start:].strip()
            title = re.sub(r'^[\.\s]+', '', title)
            title = re.sub(r'\(Continued\).*$', '', title, flags=re.IGNORECASE).strip()

            if not title:
                title = f"Table {prefix}{number}"
            else:
                title = f"Table {prefix}{number}. {title[:100]}"

            # Check if this is a (Continued) entry
            is_continued = bool(re.search(r'\(Continued\)', text, re.IGNORECASE))

        # Pattern 2: "Forming Part of Sentence/Article X.X.X"
        if not table_id:
            match = FORMING_PART_PATTERN.search(text)
            if match:
                ref_type = match.group(1)  # Article or Sentence
                ref_num = match.group(2).rstrip('.')
                table_id = f"Table-FP-{ref_num}"

                # Title is the text before "Forming Part of"
                title_text = text[:match.start()].strip()
                if title_text:
                    title = f"{title_text[:80]} (Forming Part of {ref_type} {ref_num})"
                else:
                    title = f"Table Forming Part of {ref_type} {ref_num}"

        # Pattern 3: "Detail EA-1" etc (OBC Vol2)
        if not table_id:
            match = DETAIL_PATTERN.search(text)
            if match:
                detail_num = match.group(1)
                table_id = f"Detail-{detail_num}"
                title = text[:100].strip()

        # Skip if no pattern matched
        if not table_id:
            continue

        # Avoid duplicates on the same page (same table_id at same position)
        page_key = (page, table_id, bbox.get('t', 0) if bbox else 0)
        if page_key in seen_table_ids_per_page:
            continue
        seen_table_ids_per_page[page_key] = True

        if page not in page_captions:
            page_captions[page] = []

        page_captions[page].append({
            'text': text,
            'table_id': table_id,
            'title': title,
            'is_continued': is_continued,
            'source_label': label,
            'bbox': bbox  # Include bbox for proximity matching
        })

    # Sort captions on each page by vertical position (top to bottom)
    for page in page_captions:
        page_captions[page].sort(key=lambda x: x['bbox'].get('t', 0) if x['bbox'] else 0)

    return page_captions


def extract_table_id_enhanced(table: Dict, texts: List[Dict], page_captions: Dict[int, List[Dict]]) -> Tuple[Optional[str], str, bool]:
    """
    Extract table ID and title using multiple strategies.

    Returns:
        (table_id, title, is_continued) tuple
    """
    prov = table.get('prov', [{}])[0]
    page = prov.get('page_no', 0)

    # Strategy 1: Check linked captions (original method)
    captions = table.get('captions', [])
    for cap in captions:
        if isinstance(cap, dict) and '$ref' in cap:
            ref = cap['$ref']
            try:
                idx = int(ref.split('/')[-1])
                if idx < len(texts):
                    caption_text = texts[idx].get('text', '')

                    # Pattern 1: Standard "Table X.X.X"
                    match = TABLE_ID_PATTERN.search(caption_text)
                    if match:
                        prefix = match.group(1) or ''
                        number = match.group(2)
                        table_id = f"Table-{prefix}{number}"

                        title_start = match.end()
                        title = caption_text[title_start:].strip()
                        title = re.sub(r'^[\.\s]+', '', title)
                        is_continued = bool(re.search(r'\(Continued\)', caption_text, re.IGNORECASE))
                        title = re.sub(r'\(Continued\).*$', '', title, flags=re.IGNORECASE).strip()

                        if not title:
                            title = f"Table {prefix}{number}"
                        else:
                            title = f"Table {prefix}{number}. {title[:100]}"

                        return table_id, title, is_continued

                    # Pattern 2: "Forming Part of Sentence/Article X.X.X"
                    match = FORMING_PART_PATTERN.search(caption_text)
                    if match:
                        ref_type = match.group(1)
                        ref_num = match.group(2).rstrip('.')
                        table_id = f"Table-FP-{ref_num}"

                        title_text = caption_text[:match.start()].strip()
                        if title_text:
                            title = f"{title_text[:80]} (Forming Part of {ref_type} {ref_num})"
                        else:
                            title = f"Table Forming Part of {ref_type} {ref_num}"

                        return table_id, title, False

                    # Pattern 3: "Detail EA-1" etc
                    match = DETAIL_PATTERN.search(caption_text)
                    if match:
                        detail_num = match.group(1)
                        table_id = f"Detail-{detail_num}"
                        title = caption_text[:100].strip()

                        return table_id, title, False

            except (ValueError, IndexError):
                pass

    # Strategy 2: Check nearby caption text elements on the same page using bbox proximity
    if page in page_captions:
        captions_on_page = page_captions[page]
        if captions_on_page:
            table_bbox = prov.get('bbox', {})
            table_top = table_bbox.get('t', 0) if table_bbox else 0

            # First pass: Find non-continued caption closest above the table
            best_caption = None
            best_continued = None  # Track best (Continued) caption as fallback

            for cap in captions_on_page:
                cap_bbox = cap.get('bbox', {})
                cap_bottom = cap_bbox.get('b', 0) if cap_bbox else 0

                # Caption should be above the table (or very close)
                if cap_bottom <= table_top + 50:  # 50 units tolerance
                    if cap['is_continued']:
                        best_continued = cap
                    else:
                        best_caption = cap
                else:
                    # Once we pass the table position, stop looking
                    break

            # If no non-continued caption found, try to find one by closest distance
            if not best_caption:
                non_continued = [c for c in captions_on_page if not c['is_continued']]
                if non_continued:
                    def distance(cap):
                        cap_bbox = cap.get('bbox', {})
                        cap_top = cap_bbox.get('t', 0) if cap_bbox else 0
                        return abs(cap_top - table_top)
                    best_caption = min(non_continued, key=distance)

            # Use non-continued caption if found, otherwise use continued caption
            if best_caption:
                return best_caption['table_id'], best_caption['title'], False
            elif best_continued:
                # This is a continuation page - return with is_continued=True
                return best_continued['table_id'], best_continued['title'], True

    # No valid table ID found
    return None, f"Table (page {page})", False


def extract_table_keywords(table: Dict) -> List[str]:
    """Extract keywords from table cells using grid data."""
    data = table.get('data', {})
    grid = data.get('grid', [])

    all_text = []
    for row in grid:
        for cell in row:
            if isinstance(cell, dict):
                all_text.append(cell.get('text', ''))
            else:
                all_text.append(str(cell))

    return extract_keywords(' '.join(all_text), max_keywords=20)


def parse_tables(data: Dict, page_division: Dict) -> List[Dict]:
    """
    Parse tables from Docling JSON and convert to section format.
    Uses enhanced caption matching for better table identification.

    Args:
        data: Full Docling JSON data
        page_division: Mapping of page numbers to Division letters

    Returns:
        List of table sections
    """
    tables = data.get('tables', [])
    texts = data.get('texts', [])

    # Build page -> caption mapping for enhanced matching
    page_captions = build_page_caption_map(texts)

    table_sections = []
    seen_ids = {}  # table_id -> first page seen
    continued_tables = []  # Tables marked as (Continued)

    for table in tables:
        prov = table.get('prov', [{}])[0]
        page = prov.get('page_no', 0)
        bbox = prov.get('bbox', None)

        # Skip tables on early pages (TOC, preface)
        if page < 20:
            continue

        # Skip very small tables (likely formatting artifacts)
        grid = table.get('data', {}).get('grid', [])
        if len(grid) < 2:
            continue

        # Get table ID and title using enhanced method
        table_id, title, is_continued = extract_table_id_enhanced(table, texts, page_captions)

        # Skip if no valid ID
        if not table_id:
            continue

        # Handle duplicates and continued tables
        if table_id in seen_ids:
            # If this is a later page, it might have additional data
            # We'll keep the first occurrence but note the page range
            if is_continued:
                continued_tables.append({
                    'table_id': table_id,
                    'page': page
                })
            continue

        seen_ids[table_id] = page

        # Get division for this page
        division = page_division.get(page, None)

        # Convert to markdown
        markdown = table_to_markdown(table)

        # Extract keywords
        keywords = extract_table_keywords(table)

        # Get table dimensions from grid
        num_rows = len(grid)
        num_cols = len(grid[0]) if grid else 0

        table_section = {
            "id": table_id,
            "title": title,
            "page": page,
            "bbox": bbox,
            "level": "table",
            "type": "table",
            "division": division,
            "keywords": keywords,
            "table_info": {
                "rows": num_rows,
                "cols": num_cols,
            },
            "markdown": markdown,
        }

        table_sections.append(table_section)

    # Mark tables that span multiple pages
    for cont in continued_tables:
        for section in table_sections:
            if section['id'] == cont['table_id']:
                if 'page_end' not in section:
                    section['page_end'] = cont['page']
                else:
                    section['page_end'] = max(section['page_end'], cont['page'])
                break  # Found the matching section, no need to continue inner loop

    # Count multi-page tables
    multi_page = sum(1 for s in table_sections if 'page_end' in s)
    print(f"  Found {len(table_sections)} tables with valid IDs (from {len(tables)} detected, {multi_page} multi-page)")
    return table_sections


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

    return sections, data, page_division


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

    sections, raw_data, page_division = parse_docling_json(str(json_path))
    print(f"Found {len(sections)} sections")

    # Parse tables
    table_sections = parse_tables(raw_data, page_division)

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
        "sections": [],
        "tables": [],  # Separate tables array for quick access
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

    # Add table sections to both sections and tables arrays
    for table in table_sections:
        # Add to sections (for unified search)
        section_dict = {
            "id": table['id'],
            "title": table['title'],
            "page": table['page'],
            "level": "table",
            "type": "table",
        }

        if table.get('bbox'):
            section_dict["bbox"] = table['bbox']

        if table.get('keywords'):
            section_dict["keywords"] = table['keywords']

        if table.get('division'):
            section_dict["division"] = table['division']

        if table.get('page_end'):
            section_dict["page_end"] = table['page_end']

        map_data["sections"].append(section_dict)

        # Add to tables array (with full markdown)
        table_entry = {
            "id": table['id'],
            "title": table['title'],
            "page": table['page'],
            "table_info": table.get('table_info', {}),
            "markdown": table.get('markdown', ''),
            "keywords": table.get('keywords', []),
        }

        if table.get('division'):
            table_entry["division"] = table['division']

        if table.get('page_end'):
            table_entry["page_end"] = table['page_end']

        map_data["tables"].append(table_entry)

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
    print(f"Sections: {len(map_data['sections'])} (including {len(map_data['tables'])} tables)")

    # Show sample sections
    if map_data['sections']:
        print("\nSample sections:")
        for section in map_data['sections'][:5]:
            print(f"  {section['id']}: page {section['page']} - {section['title'][:40]}")

    # Show sample tables
    if map_data['tables']:
        print("\nSample tables:")
        for table in map_data['tables'][:5]:
            info = table.get('table_info', {})
            print(f"  {table['id']}: page {table['page']} ({info.get('rows', '?')}x{info.get('cols', '?')}) - {table['title'][:40]}")

    # Show stats by division
    divisions = {}
    for s in map_data['sections']:
        div = s.get('division', 'None')
        divisions[div] = divisions.get(div, 0) + 1
    print(f"\nBy Division: {divisions}")


if __name__ == "__main__":
    main()
