"""
Index Builder - meta.json에서 Table → Page 인덱스 생성
"""

import json
import re
from pathlib import Path
from typing import Dict


def build_table_index(meta_json_path: str) -> Dict[str, int]:
    """
    Marker meta.json에서 Table ID → Page 번호 인덱스 생성

    Returns:
        {"Table 9.10.14.4": 245, "Table 9.8.2.1": 123, ...}
    """
    with open(meta_json_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    index = {}

    # table_of_contents에서 테이블 찾기
    for item in meta.get('table_of_contents', []):
        title = item.get('title', '')
        page = item.get('page_id', 0)

        # "Table X.X.X.X" 패턴 매칭
        match = re.search(r'Table\s+(\d+\.\d+\.\d+\.\d+[A-Z]?(?:-[A-Z])?)', title)
        if match:
            table_id = f"Table {match.group(1)}"
            index[table_id] = page

    # blocks에서도 테이블 찾기 (백업)
    for block in meta.get('blocks', []):
        if block.get('type') == 'Table':
            text = block.get('text', '')
            match = re.search(r'Table\s+(\d+\.\d+\.\d+\.\d+[A-Z]?(?:-[A-Z])?)', text)
            if match:
                table_id = f"Table {match.group(1)}"
                if table_id not in index:
                    index[table_id] = block.get('page_id', 0)

    return index


def build_table_index_fallback(pdf_path: str) -> Dict[str, int]:
    """
    meta.json에 테이블 정보 없을 때 pdfplumber로 빌드 (느림)
    """
    import pdfplumber

    index = {}

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ''

            for match in re.finditer(r'Table\s+(\d+\.\d+\.\d+\.\d+[A-Z]?(?:-[A-Z])?)', text):
                table_id = f"Table {match.group(1)}"
                if table_id not in index:
                    index[table_id] = i + 1  # 1-indexed

    return index


def save_index(index: dict, output_path: str):
    """인덱스를 JSON 파일로 저장"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"Saved index with {len(index)} tables to {output_path}")


def load_index(index_path: str) -> dict:
    """저장된 인덱스 로드"""
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python index_builder.py <meta_json_path> [output_path]")
        sys.exit(1)

    meta_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else meta_path.replace('_meta.json', '_table_index.json')

    index = build_table_index(meta_path)
    save_index(index, output_path)

    print(f"\nSample entries:")
    for table_id, page in list(index.items())[:5]:
        print(f"  {table_id}: page {page}")
