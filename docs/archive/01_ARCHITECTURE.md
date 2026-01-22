# 01. Architecture - Detailed Architecture

## Core Concept: Map & Territory

```
Map (coordinate)  = structure_map.json (coordinates, pages, IDs)
Territory (data)  = User's PDF file (actual content)
```

**Analogy:**
> Just like Google Maps tells you "Seoul Station is at 37.5° N latitude",
> we tell you "Section 9.8.2.1 is at page 245, coordinates [50,100]".
>
> Actually going to Seoul Station is up to the user.
> Actually reading the text is from the user's PDF.

---

## Data Flow

### Phase 1: Developer Side (Map Generation)

```
┌─────────────────────────────────────────────────────────┐
│                    Developer Computer                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────┐                                            │
│  │ OBC PDF │                                            │
│  └────┬────┘                                            │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────────────────────────────────────────┐       │
│  │              Marker Parsing                  │       │
│  │  - Structure analysis (Section, Article)     │       │
│  │  - bbox coordinate extraction                │       │
│  │  - Page number recording                     │       │
│  │  (Time: 30min ~ 1hour)                       │       │
│  └────┬────────────────────────────────────────┘       │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────────────────────────────────────────┐       │
│  │           structure_map.json                 │       │
│  │  - No text content (copyright safe)          │       │
│  │  - Coordinates only                          │       │
│  │  - Size: hundreds of KB                      │       │
│  └────┬────────────────────────────────────────┘       │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────┐                                            │
│  │ GitHub  │ ← Distribution                             │
│  └─────────┘                                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Phase 2: User Side (Text Extraction)

```
┌─────────────────────────────────────────────────────────┐
│                     User Computer                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐    ┌──────────────────────┐       │
│  │ User's OBC PDF  │    │ structure_map.json   │       │
│  │ (legally obtained)│   │ (downloaded from GitHub)│    │
│  └────────┬────────┘    └──────────┬───────────┘       │
│           │                        │                    │
│           │    ┌───────────────────┘                    │
│           ▼    ▼                                        │
│  ┌─────────────────────────────────────────────┐       │
│  │            PDF Hash Verification             │       │
│  │  - Calculate user's PDF hash                 │       │
│  │  - Compare with checksums.json               │       │
│  │  - Match: Fast Mode / Mismatch: Slow Mode    │       │
│  └────┬────────────────────────────────────────┘       │
│       │                                                 │
│       ▼ (on match)                                      │
│  ┌─────────────────────────────────────────────┐       │
│  │         PyMuPDF Coordinate-based Extraction  │       │
│  │                                              │       │
│  │  for item in structure_map:                  │       │
│  │      page = doc[item.page]                   │       │
│  │      text = page.get_text(clip=item.bbox)    │       │
│  │                                              │       │
│  │  (Time: 10sec ~ 1min)                        │       │
│  └────┬────────────────────────────────────────┘       │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────────────────────────────────────────┐       │
│  │              Local SQLite DB                 │       │
│  │  - section_id, content, type, page           │       │
│  │  - Search index creation                     │       │
│  └────┬────────────────────────────────────────┘       │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────────────────────────────────────────┐       │
│  │              MCP Server Running              │       │
│  │  - search_code(query)                        │       │
│  │  - get_section(id)                           │       │
│  │  - get_table(id)                             │       │
│  └────┬────────────────────────────────────────┘       │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────┐                                            │
│  │ Claude  │ ← MCP Connection                           │
│  └─────────┘                                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## structure_map.json Schema

### Basic Structure

```json
{
  "version": "1.0.0",
  "code": "OBC",
  "year": "2024",
  "pdf_hash": "a1b2c3d4e5f6...",
  "created_at": "2026-01-21T12:00:00Z",

  "sections": [
    {
      "id": "9.8.2.1",
      "type": "article",
      "title": "Width",
      "page": 245,
      "bbox": [50.0, 100.0, 550.0, 300.0],
      "parent_id": "9.8.2",
      "children": ["9.8.2.1.(1)", "9.8.2.1.(2)"]
    },
    {
      "id": "Table 9.10.14.4",
      "type": "table",
      "title": "Maximum Aggregate Area of Unprotected Openings",
      "page": 287,
      "bbox": [50.0, 150.0, 550.0, 600.0],
      "parent_id": "9.10.14.4",
      "spans_pages": [287, 288]
    }
  ],

  "tables": [
    {
      "id": "Table 9.10.14.4",
      "page": 287,
      "header_bbox": [50.0, 150.0, 550.0, 180.0],
      "body_bbox": [50.0, 180.0, 550.0, 600.0],
      "columns": 15,
      "rows": 12
    }
  ]
}
```

### Type Definitions

```typescript
interface StructureMap {
  version: string;
  code: "OBC" | "NBC" | "BCBC" | "ABC";
  year: string;
  pdf_hash: string;
  created_at: string;

  sections: Section[];
  tables: Table[];
}

interface Section {
  id: string;           // "9.8.2.1"
  type: "part" | "section" | "subsection" | "article" | "clause";
  title?: string;       // Title (omit if extractable by coordinates)
  page: number;         // 1-indexed
  bbox: [number, number, number, number];  // [x1, y1, x2, y2]
  parent_id?: string;
  children?: string[];
}

interface Table {
  id: string;           // "Table 9.10.14.4"
  page: number;
  header_bbox: [number, number, number, number];
  body_bbox: [number, number, number, number];
  columns: number;
  rows: number;
  spans_pages?: number[];  // Multi-page tables
}
```

---

## PDF Version Verification

### Why Is It Needed?

```
Problem: What if user's PDF is a different version than developer's?
     → All coordinates are misaligned
     → Wrong text extraction
```

### Verification Logic

```python
import hashlib

def verify_pdf(user_pdf_path: str, expected_hash: str) -> bool:
    """Verify PDF file hash"""
    with open(user_pdf_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    return file_hash == expected_hash

def get_extraction_mode(user_pdf: str, checksums: dict) -> str:
    """Determine extraction mode"""
    user_hash = calculate_hash(user_pdf)

    if user_hash in checksums.values():
        return "fast"   # Coordinate-based extraction
    else:
        return "slow"   # Pattern matching extraction (fallback)
```

### checksums.json

```json
{
  "OBC_2024_v1": {
    "hash": "a1b2c3d4e5f6...",
    "source": "ontario.ca",
    "date": "2024-01-01",
    "pages": 1200
  },
  "OBC_2024_v2": {
    "hash": "f6e5d4c3b2a1...",
    "source": "ontario.ca",
    "date": "2024-06-15",
    "pages": 1200,
    "note": "Typo correction version"
  }
}
```

---

## Fallback Mode

### When Hash Mismatch

```python
def slow_mode_extraction(pdf_path: str, structure_map: dict) -> dict:
    """
    Pattern matching extraction when hash doesn't match
    Uses text patterns instead of coordinates
    """
    doc = fitz.open(pdf_path)
    results = {}

    for section in structure_map['sections']:
        # Search by ID pattern instead of coordinates
        pattern = rf"^{re.escape(section['id'])}\.\s+"

        for page_num, page in enumerate(doc):
            text = page.get_text()
            if re.search(pattern, text, re.MULTILINE):
                # Extract section text
                results[section['id']] = extract_section_text(page, pattern)
                break

    return results
```

---

## Performance Comparison

| Mode | Method | Time | Accuracy |
|------|--------|------|----------|
| **Fast** | Coordinate-based | 10sec ~ 1min | 100% (verified coordinates) |
| **Slow** | Pattern matching | 5min ~ 10min | 95% (pattern dependent) |
| **Full** | Re-run Marker | 30min ~ 1hour | 98% (Marker quality) |

---

## Next Document

→ [02_IMPLEMENTATION.md](./02_IMPLEMENTATION.md) - Implementation Guide
