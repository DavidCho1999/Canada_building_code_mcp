# 02. Implementation - 구현 가이드

## 개발 환경 설정

### 필수 패키지

```bash
# 개발자 측 (맵 생성)
pip install marker-pdf pymupdf

# 사용자 측 (MCP 서버)
pip install mcp pymupdf
```

### 디렉토리 구조

```
canadian-building-code-mcp/
├── scripts/                  # 개발자용 스크립트
│   ├── generate_map.py      # structure_map 생성
│   ├── validate_map.py      # 맵 검증
│   └── extract_checksums.py # PDF 해시 추출
│
├── maps/                     # 배포용 맵 파일
│   ├── obc_2024_map.json
│   └── checksums.json
│
├── src/                      # MCP 서버 코드
│   ├── __init__.py
│   ├── server.py            # MCP 서버 메인
│   ├── extractor.py         # PDF 텍스트 추출
│   ├── database.py          # SQLite 관리
│   └── config.py            # 설정
│
└── tests/
    └── test_extraction.py
```

---

## Part 1: 맵 생성 (개발자 측)

### 1.1 Marker 실행 및 좌표 추출

```python
# scripts/generate_map.py

import json
import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime
import hashlib

def calculate_pdf_hash(pdf_path: str) -> str:
    """PDF 파일의 MD5 해시 계산"""
    with open(pdf_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def extract_structure_from_marker(marker_output_dir: str) -> dict:
    """
    Marker 출력에서 구조 정보 추출
    - meta.json의 table_of_contents에서 polygon 정보 사용
    """
    meta_path = Path(marker_output_dir) / "meta.json"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    sections = []

    for item in meta.get('table_of_contents', []):
        # polygon을 bbox로 변환 (4점 → [x1, y1, x2, y2])
        polygon = item.get('polygon', [])
        if len(polygon) >= 4:
            bbox = [
                polygon[0][0],  # x1
                polygon[0][1],  # y1
                polygon[2][0],  # x2
                polygon[2][1]   # y2
            ]
        else:
            bbox = None

        sections.append({
            "title": item.get('title', ''),
            "page": item.get('page_id', 1),
            "bbox": bbox,
            "heading_level": item.get('heading_level')
        })

    return sections

def parse_section_id(title: str) -> dict:
    """
    제목에서 Section ID 파싱
    예: "9.8.2.1. Width" → {"id": "9.8.2.1", "type": "article"}
    """
    import re

    # 패턴: 9.X.X.X 형식
    match = re.match(r'^(\d+\.\d+(?:\.\d+)?(?:\.\d+)?[A-Z]?)\.?\s*(.*)$', title)

    if match:
        section_id = match.group(1)
        section_title = match.group(2).strip()

        # 타입 결정
        parts = section_id.split('.')
        if len(parts) == 1:
            section_type = "part"
        elif len(parts) == 2:
            section_type = "section"
        elif len(parts) == 3:
            section_type = "subsection"
        elif len(parts) == 4:
            section_type = "article"
        else:
            section_type = "clause"

        return {
            "id": section_id,
            "title": section_title,
            "type": section_type
        }

    # Table 패턴
    table_match = re.match(r'^Table\s+(\d+\.\d+\.\d+\.\d+[A-Z]?(?:-[A-Z])?)', title)
    if table_match:
        return {
            "id": f"Table {table_match.group(1)}",
            "title": title,
            "type": "table"
        }

    return None

def generate_structure_map(
    pdf_path: str,
    marker_output_dir: str,
    code_name: str,
    year: str
) -> dict:
    """전체 structure_map 생성"""

    # PDF 해시 계산
    pdf_hash = calculate_pdf_hash(pdf_path)

    # Marker 출력에서 구조 추출
    raw_sections = extract_structure_from_marker(marker_output_dir)

    # 구조화
    sections = []
    tables = []

    for item in raw_sections:
        parsed = parse_section_id(item['title'])

        if parsed:
            entry = {
                "id": parsed['id'],
                "type": parsed['type'],
                "title": parsed.get('title', ''),
                "page": item['page'],
                "bbox": item['bbox']
            }

            if parsed['type'] == 'table':
                tables.append(entry)
            else:
                sections.append(entry)

    # 계층 구조 생성 (parent_id, children)
    sections = build_hierarchy(sections)

    return {
        "version": "1.0.0",
        "code": code_name,
        "year": year,
        "pdf_hash": pdf_hash,
        "created_at": datetime.now().isoformat(),
        "sections": sections,
        "tables": tables
    }

def build_hierarchy(sections: list) -> list:
    """섹션 간 계층 관계 설정"""
    id_map = {s['id']: s for s in sections}

    for section in sections:
        # parent_id 찾기
        parts = section['id'].split('.')
        if len(parts) > 1:
            parent_id = '.'.join(parts[:-1])
            if parent_id in id_map:
                section['parent_id'] = parent_id

                # 부모의 children에 추가
                if 'children' not in id_map[parent_id]:
                    id_map[parent_id]['children'] = []
                id_map[parent_id]['children'].append(section['id'])

    return sections

# 실행
if __name__ == "__main__":
    structure_map = generate_structure_map(
        pdf_path="source/2024 Building Code Compendium/301880.pdf",
        marker_output_dir="data/marker/chunk_01/301880",
        code_name="OBC",
        year="2024"
    )

    with open("maps/obc_2024_map.json", 'w', encoding='utf-8') as f:
        json.dump(structure_map, f, indent=2, ensure_ascii=False)

    print(f"Generated map with {len(structure_map['sections'])} sections")
```

### 1.2 맵 검증

```python
# scripts/validate_map.py

import json
import fitz

def validate_map(map_path: str, pdf_path: str) -> dict:
    """
    structure_map이 PDF와 일치하는지 검증
    """
    with open(map_path, 'r') as f:
        structure_map = json.load(f)

    doc = fitz.open(pdf_path)

    results = {
        "total": len(structure_map['sections']),
        "valid": 0,
        "invalid": 0,
        "errors": []
    }

    for section in structure_map['sections'][:50]:  # 샘플 검증
        try:
            page = doc[section['page'] - 1]  # 0-indexed

            if section['bbox']:
                rect = fitz.Rect(section['bbox'])
                text = page.get_text("text", clip=rect)

                # ID가 추출된 텍스트에 포함되어 있는지 확인
                if section['id'] in text or section.get('title', '') in text:
                    results['valid'] += 1
                else:
                    results['invalid'] += 1
                    results['errors'].append({
                        "id": section['id'],
                        "expected": section.get('title', ''),
                        "got": text[:100]
                    })
        except Exception as e:
            results['invalid'] += 1
            results['errors'].append({
                "id": section['id'],
                "error": str(e)
            })

    return results
```

---

## Part 2: MCP 서버 (사용자 측)

### 2.1 PDF 텍스트 추출기

```python
# src/extractor.py

import fitz
import hashlib
from pathlib import Path
from typing import Optional

class PDFExtractor:
    def __init__(self, pdf_path: str, structure_map: dict):
        self.pdf_path = pdf_path
        self.structure_map = structure_map
        self.doc = None
        self.mode = "fast"  # or "slow"

    def verify_pdf(self) -> bool:
        """PDF 해시 검증"""
        expected_hash = self.structure_map.get('pdf_hash')

        with open(self.pdf_path, 'rb') as f:
            actual_hash = hashlib.md5(f.read()).hexdigest()

        if actual_hash == expected_hash:
            self.mode = "fast"
            return True
        else:
            self.mode = "slow"
            print(f"Warning: PDF hash mismatch. Using slow mode.")
            print(f"Expected: {expected_hash}")
            print(f"Got: {actual_hash}")
            return False

    def open(self):
        """PDF 열기"""
        self.doc = fitz.open(self.pdf_path)

    def close(self):
        """PDF 닫기"""
        if self.doc:
            self.doc.close()

    def extract_section(self, section_id: str) -> Optional[str]:
        """특정 섹션 텍스트 추출"""
        # 섹션 찾기
        section = None
        for s in self.structure_map['sections']:
            if s['id'] == section_id:
                section = s
                break

        if not section:
            return None

        if self.mode == "fast" and section.get('bbox'):
            return self._extract_by_bbox(section)
        else:
            return self._extract_by_pattern(section)

    def _extract_by_bbox(self, section: dict) -> str:
        """좌표 기반 추출 (Fast Mode)"""
        page = self.doc[section['page'] - 1]
        rect = fitz.Rect(section['bbox'])
        return page.get_text("text", clip=rect).strip()

    def _extract_by_pattern(self, section: dict) -> str:
        """패턴 기반 추출 (Slow Mode)"""
        import re

        page = self.doc[section['page'] - 1]
        text = page.get_text()

        # 섹션 시작 패턴
        start_pattern = rf"(?:^|\n){re.escape(section['id'])}\.\s+"

        match = re.search(start_pattern, text)
        if match:
            start_pos = match.end()

            # 다음 섹션까지 추출 (간단한 버전)
            end_pos = len(text)
            next_section_match = re.search(r'\n\d+\.\d+\.\d+\.\d+\.', text[start_pos:])
            if next_section_match:
                end_pos = start_pos + next_section_match.start()

            return text[start_pos:end_pos].strip()

        return ""

    def extract_all(self) -> dict:
        """전체 텍스트 추출"""
        results = {}

        for section in self.structure_map['sections']:
            text = self.extract_section(section['id'])
            if text:
                results[section['id']] = {
                    "content": text,
                    "type": section['type'],
                    "page": section['page']
                }

        return results
```

### 2.2 로컬 데이터베이스

```python
# src/database.py

import sqlite3
from pathlib import Path

class LocalDB:
    def __init__(self, db_path: str = "~/.building-code-mcp/codes.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(str(self.db_path))
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sections (
                id TEXT PRIMARY KEY,
                code TEXT,
                type TEXT,
                title TEXT,
                content TEXT,
                page INTEGER,
                parent_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS sections_fts
            USING fts5(id, title, content, tokenize='porter')
        """)

        self.conn.commit()

    def insert_section(self, section: dict, code: str):
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO sections
            (id, code, type, title, content, page, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            section['id'],
            code,
            section.get('type'),
            section.get('title', ''),
            section.get('content', ''),
            section.get('page'),
            section.get('parent_id')
        ))

        # FTS 업데이트
        cursor.execute("""
            INSERT OR REPLACE INTO sections_fts (id, title, content)
            VALUES (?, ?, ?)
        """, (
            section['id'],
            section.get('title', ''),
            section.get('content', '')
        ))

        self.conn.commit()

    def search(self, query: str, code: str = None, limit: int = 10) -> list:
        cursor = self.conn.cursor()

        sql = """
            SELECT s.id, s.title, s.type, s.page,
                   snippet(sections_fts, 2, '<mark>', '</mark>', '...', 32) as snippet
            FROM sections_fts
            JOIN sections s ON sections_fts.id = s.id
            WHERE sections_fts MATCH ?
        """
        params = [query]

        if code:
            sql += " AND s.code = ?"
            params.append(code)

        sql += " LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        return cursor.fetchall()

    def get_section(self, section_id: str) -> dict:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, code, type, title, content, page, parent_id
            FROM sections WHERE id = ?
        """, (section_id,))

        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "code": row[1],
                "type": row[2],
                "title": row[3],
                "content": row[4],
                "page": row[5],
                "parent_id": row[6]
            }
        return None
```

### 2.3 MCP 서버

```python
# src/server.py

from mcp.server import Server
from mcp.types import Tool, TextContent
import json
from pathlib import Path

from .database import LocalDB
from .extractor import PDFExtractor

server = Server("canadian-building-code")
db = LocalDB()

@server.tool()
async def setup_code(pdf_path: str, code: str = "OBC") -> str:
    """
    Building Code PDF를 설정하고 인덱싱합니다.

    Args:
        pdf_path: PDF 파일 경로
        code: 코드 종류 (OBC, NBC, BCBC 등)
    """
    # 맵 로드
    map_path = Path(__file__).parent.parent / f"maps/{code.lower()}_2024_map.json"

    if not map_path.exists():
        return f"Error: Map for {code} not found"

    with open(map_path, 'r') as f:
        structure_map = json.load(f)

    # 추출기 초기화
    extractor = PDFExtractor(pdf_path, structure_map)
    extractor.verify_pdf()
    extractor.open()

    # 텍스트 추출 및 DB 저장
    db.connect()

    sections = extractor.extract_all()
    for section_id, data in sections.items():
        db.insert_section({
            "id": section_id,
            **data
        }, code)

    extractor.close()

    return f"Successfully indexed {len(sections)} sections from {code}"

@server.tool()
async def search_code(query: str, code: str = None) -> str:
    """
    Building Code에서 검색합니다.

    Args:
        query: 검색어
        code: 특정 코드로 제한 (선택)
    """
    db.connect()
    results = db.search(query, code)

    if not results:
        return "No results found"

    output = []
    for r in results:
        output.append(f"**{r[0]}** ({r[2]}, p.{r[3]})\n{r[4]}")

    return "\n\n---\n\n".join(output)

@server.tool()
async def get_section(section_id: str) -> str:
    """
    특정 섹션의 전체 내용을 가져옵니다.

    Args:
        section_id: 섹션 ID (예: 9.8.2.1)
    """
    db.connect()
    section = db.get_section(section_id)

    if not section:
        return f"Section {section_id} not found"

    return f"""# {section['id']} - {section['title']}

**Type:** {section['type']}
**Page:** {section['page']}
**Code:** {section['code']}

---

{section['content']}
"""

@server.tool()
async def get_table(table_id: str) -> str:
    """
    특정 테이블을 가져옵니다.

    Args:
        table_id: 테이블 ID (예: Table 9.10.14.4)
    """
    return await get_section(table_id)

# 서버 실행
if __name__ == "__main__":
    import asyncio
    asyncio.run(server.run())
```

---

## Part 3: 사용자 설정

### Claude Desktop 설정

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "building-code": {
      "command": "python",
      "args": ["-m", "canadian_building_code_mcp.server"],
      "env": {
        "PDF_PATH": "C:/path/to/OBC_2024.pdf"
      }
    }
  }
}
```

### 첫 실행 시

```
사용자: "OBC PDF를 설정해줘"

Claude: [setup_code 호출]
        "Successfully indexed 1,247 sections from OBC"

사용자: "계단 너비 규정 알려줘"

Claude: [search_code("계단 너비") 또는 search_code("stair width")]
        "9.8.2.1에 따르면..."
```

---

## 다음 문서

→ [03_LEGAL.md](./03_LEGAL.md) - 법적 분석
