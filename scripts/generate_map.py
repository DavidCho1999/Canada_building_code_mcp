#!/usr/bin/env python3
"""
Map Generator for Canadian Building Codes
Extracts ID/Title/Page/BBox + Rich Keywords from Docling output
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import Counter
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict


# Building code stopwords (common words that don't help search)
STOPWORDS = {
    # General English
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
    'paragraph', 'subparagraph', 'item', 'items',
}


@dataclass
class Section:
    """A section/article in the building code."""
    id: str
    title: str
    page: int
    level: str  # 'division', 'part', 'section', 'subsection', 'article'
    parent_id: Optional[str] = None
    bbox: Optional[Dict] = None
    keywords: Optional[List[str]] = None
    content_preview: Optional[str] = None  # For keyword extraction, not exported


def extract_keywords(text: str, max_keywords: int = 15) -> List[str]:
    """
    Extract meaningful keywords from text using simple TF approach.
    Removes stopwords and common building code terms.
    """
    if not text:
        return []

    # Tokenize: lowercase, keep alphanumeric and hyphens
    words = re.findall(r'[a-z][a-z0-9-]*[a-z0-9]|[a-z]', text.lower())

    # Filter stopwords and short words
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]

    # Count frequency
    counter = Counter(words)

    # Get top keywords
    keywords = [word for word, _ in counter.most_common(max_keywords)]

    return keywords


def get_level_from_id(section_id: str) -> str:
    """Determine hierarchy level from ID pattern."""
    # Division A, B, C
    if re.match(r'^Division\s+[A-Z]', section_id, re.IGNORECASE):
        return 'division'

    # Part 1, Part 9, etc.
    if re.match(r'^Part\s+\d+', section_id, re.IGNORECASE):
        return 'part'

    # Count dots to determine level
    dots = section_id.count('.')

    if dots == 1:  # 9.1
        return 'section'
    elif dots == 2:  # 9.1.1
        return 'subsection'
    elif dots >= 3:  # 9.1.1.1
        return 'article'

    return 'unknown'


def get_parent_id(section_id: str) -> Optional[str]:
    """Calculate parent ID from section ID."""
    # For numeric IDs like 9.1.1.1
    if re.match(r'^\d+\.', section_id):
        parts = section_id.split('.')
        if len(parts) > 1:
            return '.'.join(parts[:-1])
    return None


def parse_markdown_sections(md_path: str) -> List[Section]:
    """
    Parse Markdown file to extract sections.
    Returns list of Section objects.
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = []

    # Pattern for headings with IDs
    # Matches: ## 1.1.1.1. Title or ## Section 1.1. Title
    heading_pattern = re.compile(
        r'^(#{1,6})\s+'  # Heading level
        r'(?:Section\s+)?'  # Optional "Section" prefix
        r'(\d+(?:\.\d+)*)\.\s*'  # ID like 1.1.1.1
        r'(.+?)$',  # Title
        re.MULTILINE
    )

    # Also match Division and Part headings
    div_pattern = re.compile(
        r'^(#{1,6})\s+(Division\s+[A-Z](?:[:\s].+)?|Part\s+\d+(?:[:\s].+)?)$',
        re.MULTILINE
    )

    # Find all matches with positions
    matches = []

    for m in heading_pattern.finditer(content):
        matches.append({
            'pos': m.start(),
            'level_md': len(m.group(1)),
            'id': m.group(2),
            'title': m.group(3).strip(),
        })

    for m in div_pattern.finditer(content):
        matches.append({
            'pos': m.start(),
            'level_md': len(m.group(1)),
            'id': m.group(2),
            'title': m.group(2),  # Title is same as ID for Division/Part
        })

    # Sort by position
    matches.sort(key=lambda x: x['pos'])

    # Extract content between sections for keyword extraction
    for i, match in enumerate(matches):
        # Get content until next heading
        start = match['pos']
        end = matches[i + 1]['pos'] if i + 1 < len(matches) else len(content)
        section_content = content[start:end]

        # Create Section object
        section = Section(
            id=match['id'],
            title=match['title'],
            page=0,  # Will be filled from JSON if available
            level=get_level_from_id(match['id']),
            parent_id=get_parent_id(match['id']),
            content_preview=section_content[:2000],  # For keyword extraction
        )

        # Extract keywords from content
        section.keywords = extract_keywords(section_content)

        sections.append(section)

    return sections


def load_docling_json(json_path: str) -> Dict:
    """Load Docling JSON output."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def enrich_with_coordinates(sections: List[Section], docling_json: Dict) -> List[Section]:
    """
    Enrich sections with page numbers and bboxes from Docling JSON.
    """
    # Build a lookup from text content to coordinates
    # Docling JSON structure varies, so we need to handle it carefully

    # Try to find text elements with provenance info
    texts = docling_json.get('texts', [])
    pages = docling_json.get('pages', {})

    for section in sections:
        # Try to find matching text in Docling output
        search_text = f"{section.id}."

        for text_item in texts:
            if isinstance(text_item, dict):
                text_content = text_item.get('text', '')
                if search_text in text_content[:50]:
                    prov = text_item.get('prov', {})
                    if prov:
                        # Handle different prov formats
                        if isinstance(prov, list) and len(prov) > 0:
                            prov = prov[0]

                        page_no = prov.get('page_no', prov.get('page', 0))
                        bbox = prov.get('bbox', None)

                        section.page = page_no
                        if bbox:
                            # Normalize bbox format
                            if isinstance(bbox, dict):
                                section.bbox = bbox
                            elif isinstance(bbox, list) and len(bbox) == 4:
                                section.bbox = {
                                    'x0': bbox[0],
                                    'y0': bbox[1],
                                    'x1': bbox[2],
                                    'y1': bbox[3]
                                }
                        break

    return sections


def generate_map(
    md_path: str,
    json_path: Optional[str] = None,
    code_name: str = None,
    code_version: str = None,
) -> Dict:
    """
    Generate map JSON from Docling output.

    Args:
        md_path: Path to Markdown file
        json_path: Path to Docling JSON file (for coordinates)
        code_name: Code name (e.g., "NBC", "OBC")
        code_version: Code version (e.g., "2025")

    Returns:
        Map dictionary ready for JSON export
    """
    md_path = Path(md_path)

    # Auto-detect code name from filename if not provided
    if code_name is None:
        # Extract from filename: NBC2025.md -> NBC
        name = md_path.stem.upper()
        # Remove year suffix
        code_name = re.sub(r'\d{4}.*$', '', name) or name

    if code_version is None:
        # Extract year from filename
        match = re.search(r'(\d{4})', md_path.stem)
        code_version = match.group(1) if match else "unknown"

    print(f"Parsing: {md_path.name}")
    print(f"Code: {code_name} {code_version}")

    # Parse sections from Markdown
    sections = parse_markdown_sections(str(md_path))
    print(f"Found {len(sections)} sections")

    # Enrich with coordinates if JSON available
    if json_path and Path(json_path).exists():
        print(f"Loading coordinates from: {json_path}")
        docling_json = load_docling_json(json_path)

        # Get source PDF metadata
        source_pdf = docling_json.get('_source_pdf', {})

        sections = enrich_with_coordinates(sections, docling_json)
    else:
        source_pdf = {}

    # Build map structure
    map_data = {
        "code": code_name,
        "version": code_version,
        "generated": __import__('datetime').datetime.now().isoformat(),
        "source_pdf": source_pdf,
        "sections": []
    }

    # Convert sections to dict format
    for section in sections:
        section_dict = {
            "id": section.id,
            "title": section.title,
            "page": section.page,
            "level": section.level,
        }

        if section.parent_id:
            section_dict["parent_id"] = section.parent_id

        if section.bbox:
            section_dict["bbox"] = section.bbox

        if section.keywords:
            section_dict["keywords"] = section.keywords

        map_data["sections"].append(section_dict)

    return map_data


def main():
    parser = argparse.ArgumentParser(
        description="Generate Map JSON from Docling output"
    )
    parser.add_argument(
        "input_dir",
        help="Docling output directory (containing .md and .json files)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file (default: maps/<code_name>.json)"
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

    input_dir = Path(args.input_dir)

    # Find MD and JSON files
    md_files = list(input_dir.glob("*.md"))
    json_files = list(input_dir.glob("*.json"))

    if not md_files:
        print(f"No .md files found in {input_dir}")
        return

    md_path = md_files[0]

    # Find corresponding JSON (not _meta.json)
    json_path = None
    for jf in json_files:
        if not jf.name.endswith('_meta.json') and not jf.name.endswith('_summary.json'):
            json_path = jf
            break

    # Generate map
    map_data = generate_map(
        str(md_path),
        str(json_path) if json_path else None,
        args.code,
        args.version,
    )

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
        print("\nSample section:")
        sample = map_data['sections'][min(10, len(map_data['sections']) - 1)]
        print(json.dumps(sample, indent=2))


if __name__ == "__main__":
    main()
