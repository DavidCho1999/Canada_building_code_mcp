#!/usr/bin/env python3
"""
Enrich Keywords Script
숫자만 있는 제목의 섹션에 부모 제목 키워드를 상속
"""

import json
import re
import sys
from pathlib import Path
from collections import Counter

# Building code stopwords (generate_map.py에서 복사)
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
    'shall', 'must', 'except', 'unless', 'where', 'provided', 'required',
    'article', 'section', 'sentence', 'clause', 'subsection', 'part',
    'division', 'table', 'figure', 'note', 'appendix', 'annex',
}


def extract_keywords(text: str, max_keywords: int = 15) -> list:
    """Extract meaningful keywords from text."""
    if not text:
        return []
    words = re.findall(r'[a-z][a-z0-9-]*[a-z0-9]|[a-z]', text.lower())
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    counter = Counter(words)
    return [word for word, _ in counter.most_common(max_keywords)]


def is_numeric_title(title: str) -> bool:
    """Check if title is only numbers and dots."""
    if not title:
        return False
    return bool(re.match(r'^[\d.\s]+$', title.strip()))


def enrich_map(map_path: Path) -> dict:
    """Enrich keywords for sections with numeric-only titles."""
    with open(map_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sections = data.get('sections', [])
    if not sections:
        return {'code': map_path.stem, 'updated': 0, 'total_numeric': 0}

    # ID -> Section mapping
    id_to_section = {s['id']: s for s in sections}

    # Find sections with numeric titles and inherit parent keywords
    updated_count = 0
    numeric_count = 0

    for section in sections:
        if is_numeric_title(section.get('title', '')):
            numeric_count += 1
            parent_id = section.get('parent_id')

            if parent_id and parent_id in id_to_section:
                parent = id_to_section[parent_id]
                parent_title = parent.get('title', '')

                # Extract keywords from parent title
                parent_keywords = extract_keywords(parent_title)

                if parent_keywords:
                    # Merge with existing keywords
                    existing = set(section.get('keywords', []))
                    new_keywords = list(existing | set(parent_keywords))
                    section['keywords'] = new_keywords[:15]
                    updated_count += 1

    # Save updated map
    with open(map_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {
        'code': data.get('code', map_path.stem),
        'updated': updated_count,
        'total_numeric': numeric_count
    }


def main():
    maps_dir = Path(__file__).parent.parent / 'maps'

    if not maps_dir.exists():
        print(f"Maps directory not found: {maps_dir}")
        return

    print("=" * 50)
    print("Enriching keywords with parent titles")
    print("=" * 50)

    results = []
    for map_file in sorted(maps_dir.glob('*.json')):
        if map_file.name.endswith('.bak'):
            continue

        result = enrich_map(map_file)
        results.append(result)
        print(f"{result['code']}: {result['updated']}/{result['total_numeric']} sections updated")

    print("=" * 50)
    total_updated = sum(r['updated'] for r in results)
    total_numeric = sum(r['total_numeric'] for r in results)
    print(f"Total: {total_updated}/{total_numeric} sections updated across {len(results)} codes")


if __name__ == "__main__":
    main()
