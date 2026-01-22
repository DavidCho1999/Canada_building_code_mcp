# 02. Implementation - Implementation Guide

## Development Environment Setup

### Required Packages

```bash
# Developer side (map generation)
pip install marker-pdf pymupdf

# User side (MCP server)
pip install mcp pymupdf
```

### Directory Structure

```
canadian-building-code-mcp/
├── scripts/                  # Developer scripts
│   ├── generate_map.py      # structure_map generation
│   ├── validate_map.py      # Map validation
│   └── extract_checksums.py # PDF hash extraction
│
├── maps/                     # Distribution map files
│   ├── obc_2024_map.json
│   └── checksums.json
│
├── src/                      # MCP server code
│   ├── __init__.py
│   ├── server.py            # MCP server main
│   ├── extractor.py         # PDF text extraction
│   ├── database.py          # SQLite management
│   └── config.py            # Configuration
│
└── tests/
    └── test_extraction.py
```

---

## Part 1: Map Generation (Developer Side)

### 1.1 Marker Execution and Coordinate Extraction

```python
# scripts/generate_map.py

import json
import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime
import hashlib

def calculate_pdf_hash(pdf_path: str) -> str:
    """Calculate MD5 hash of PDF file"""
    with open(pdf_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def extract_structure_from_marker(marker_output_dir: str) -> dict:
    """
    Extract structure information from Marker output
    - Uses polygon info from meta.json table_of_contents
    """
    meta_path = Path(marker_output_dir) / "meta.json"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    sections = []

    for item in meta.get('table_of_contents', []):
        # Convert polygon to bbox (4 points → [x1, y1, x2, y2])
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
```

### 1.2 Map Validation

```python
# scripts/validate_map.py

import json
import fitz

def validate_map(map_path: str, pdf_path: str) -> dict:
    """
    Validate that structure_map matches the PDF
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

    for section in structure_map['sections'][:50]:  # Sample validation
        try:
            page = doc[section['page'] - 1]  # 0-indexed

            if section['bbox']:
                rect = fitz.Rect(section['bbox'])
                text = page.get_text("text", clip=rect)

                # Check if ID is in extracted text
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

## Part 2: MCP Server (User Side)

### 2.1 PDF Text Extractor

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
        """Verify PDF hash"""
        expected_hash = self.structure_map.get('pdf_hash')

        with open(self.pdf_path, 'rb') as f:
            actual_hash = hashlib.md5(f.read()).hexdigest()

        if actual_hash == expected_hash:
            self.mode = "fast"
            return True
        else:
            self.mode = "slow"
            print(f"Warning: PDF hash mismatch. Using slow mode.")
            return False

    def extract_section(self, section_id: str) -> Optional[str]:
        """Extract specific section text"""
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
        """Coordinate-based extraction (Fast Mode)"""
        page = self.doc[section['page'] - 1]
        rect = fitz.Rect(section['bbox'])
        return page.get_text("text", clip=rect).strip()
```

### 2.2 Local Database

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

    def search(self, query: str, code: str = None, limit: int = 10) -> list:
        cursor = self.conn.cursor()
        sql = """
            SELECT s.id, s.title, s.type, s.page,
                   snippet(sections_fts, 2, '<mark>', '</mark>', '...', 32)
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
```

### 2.3 MCP Server

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
    Set up and index the Building Code PDF.

    Args:
        pdf_path: PDF file path
        code: Code type (OBC, NBC, BCBC, etc.)
    """
    # Load map
    map_path = Path(__file__).parent.parent / f"maps/{code.lower()}_2024_map.json"

    if not map_path.exists():
        return f"Error: Map for {code} not found"

    with open(map_path, 'r') as f:
        structure_map = json.load(f)

    # Initialize extractor
    extractor = PDFExtractor(pdf_path, structure_map)
    extractor.verify_pdf()
    extractor.open()

    # Extract text and save to DB
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
    Search the Building Code.

    Args:
        query: Search terms
        code: Limit to specific code (optional)
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
    Get the full content of a specific section.

    Args:
        section_id: Section ID (e.g., 9.8.2.1)
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
```

---

## Part 3: User Configuration

### Claude Desktop Configuration

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

### First Run

```
User: "Set up the OBC PDF"

Claude: [calls setup_code]
        "Successfully indexed 1,247 sections from OBC"

User: "Tell me the stair width requirements"

Claude: [calls search_code("stair width")]
        "According to 9.8.2.1..."
```

---

## Next Document

→ [03_LEGAL.md](./03_LEGAL.md) - Legal Analysis
