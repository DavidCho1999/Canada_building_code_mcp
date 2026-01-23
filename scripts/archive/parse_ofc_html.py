#!/usr/bin/env python3
"""
Parse Ontario Fire Code HTML to generate map JSON.
"""

import re
import json
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from collections import Counter


# Stopwords for keyword extraction
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
    'those', 'it', 'its', 'if', 'then', 'than', 'so', 'such', 'no', 'not',
    'only', 'same', 'other', 'into', 'over', 'under', 'after', 'before',
    'shall', 'must', 'except', 'unless', 'where', 'provided', 'required',
    'article', 'section', 'sentence', 'clause', 'subsection', 'part',
    'division', 'table', 'figure', 'note', 'applicable', 'apply',
}


def extract_keywords(text: str, max_keywords: int = 10) -> list:
    """Extract meaningful keywords from text."""
    if not text:
        return []
    words = re.findall(r'[a-z][a-z0-9-]*[a-z0-9]|[a-z]', text.lower())
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    counter = Counter(words)
    return [word for word, _ in counter.most_common(max_keywords)]


def parse_ofc_html(html_path: str) -> dict:
    """Parse OFC HTML and extract sections."""

    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    sections = []
    current_division = None
    current_part = None
    current_section = None
    current_subsection = None

    # Pattern for article IDs: 1.1.1.1, 2.3.4.5, etc.
    article_pattern = re.compile(r'^\s*(\d+\.\d+\.\d+\.\d+\.?)\s*(.*)$', re.DOTALL)

    # Find all relevant elements
    for elem in soup.find_all(['p']):
        class_name = ' '.join(elem.get('class', []))
        text = elem.get_text(strip=True)

        # Division: "division a compliance, objectives..."
        if 'partnum-e' in class_name and text.lower().startswith('division'):
            match = re.match(r'division\s+([a-c])\s*(.*)', text, re.IGNORECASE)
            if match:
                current_division = match.group(1).upper()
                title = match.group(2).strip()
                sections.append({
                    'id': f'Division-{current_division}',
                    'title': title or f'Division {current_division}',
                    'level': 'division',
                    'division': current_division,
                })

        # Part: "PART 1 compliance and General"
        elif 'partnum-e' in class_name and text.upper().startswith('PART'):
            match = re.match(r'PART\s+(\d+)\s*(.*)', text, re.IGNORECASE)
            if match:
                part_num = match.group(1)
                title = match.group(2).strip()
                current_part = part_num
                part_id = f'{current_division}-Part{part_num}' if current_division else f'Part{part_num}'
                sections.append({
                    'id': part_id,
                    'title': title or f'Part {part_num}',
                    'level': 'part',
                    'division': current_division,
                    'parent_id': f'Division-{current_division}' if current_division else None,
                })

        # Section: "SECTION 1.1 organization of this code"
        elif 'rulel-e' in class_name:
            match = re.match(r'SECTION\s+(\d+\.\d+)\s*(.*)', text, re.IGNORECASE)
            if match:
                sec_num = match.group(1)
                title = match.group(2).strip()
                current_section = sec_num
                sec_id = f'{current_division}-{sec_num}' if current_division else sec_num
                parent = f'{current_division}-Part{current_part}' if current_division and current_part else None
                sections.append({
                    'id': sec_id,
                    'title': title or f'Section {sec_num}',
                    'level': 'section',
                    'division': current_division,
                    'parent_id': parent,
                    'keywords': extract_keywords(title),
                })

        # Subsection: "Subsection 1.1.1. General"
        elif 'paranoindt-e' in class_name:
            match = re.match(r'Subsection\s+(\d+\.\d+\.\d+)\.\s*(.*)', text, re.IGNORECASE)
            if match:
                subsec_num = match.group(1)
                title = match.group(2).strip()
                current_subsection = subsec_num
                subsec_id = f'{current_division}-{subsec_num}' if current_division else subsec_num
                parent = f'{current_division}-{current_section}' if current_division and current_section else current_section
                sections.append({
                    'id': subsec_id,
                    'title': title or f'Subsection {subsec_num}',
                    'level': 'subsection',
                    'division': current_division,
                    'parent_id': parent,
                    'keywords': extract_keywords(title),
                })

        # Article: "1.1.1.1. Division A contains..."
        elif 'section' in class_name and class_name.strip() == 'section':
            match = article_pattern.match(text)
            if match:
                art_num = match.group(1).rstrip('.')
                content = match.group(2).strip()

                # Get title from content (first sentence or portion)
                title = content[:100].split('.')[0] if content else ''

                art_id = f'{current_division}-{art_num}' if current_division else art_num
                parent = f'{current_division}-{current_subsection}' if current_division and current_subsection else current_subsection

                sections.append({
                    'id': art_id,
                    'title': title,
                    'level': 'article',
                    'division': current_division,
                    'parent_id': parent,
                    'keywords': extract_keywords(content[:500]),
                })

    return sections


def main():
    html_path = Path(__file__).parent.parent / 'sources' / 'ofc.html'
    output_path = Path(__file__).parent.parent / 'maps' / 'OFC.json'

    print(f'Parsing: {html_path}')
    sections = parse_ofc_html(str(html_path))
    print(f'Found {len(sections)} sections')

    # Build map
    map_data = {
        'code': 'OFC',
        'name': 'Ontario Fire Code',
        'version': 'O. Reg. 213/07 (current to Jan 2026)',
        'source': 'Ontario e-Laws',
        'source_url': 'https://www.ontario.ca/laws/regulation/070213',
        'generated': datetime.now().isoformat(),
        'sections': sections,
    }

    # Save
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(map_data, f, ensure_ascii=False, indent=2)

    print(f'Saved: {output_path}')

    # Stats
    levels = {}
    for s in sections:
        level = s.get('level', 'unknown')
        levels[level] = levels.get(level, 0) + 1
    print(f'By level: {levels}')

    # Sample
    print('\nSample sections:')
    for s in sections[:10]:
        print(f"  {s['id']}: {s['title'][:50]}")


if __name__ == '__main__':
    main()
