# 06. Hybrid Pipeline

## Overview

A pipeline combining Marker's text extraction ability + pdfplumber's table extraction ability.

**Key Discovery:** Marker's `meta.json` already has page information → No need to scan entire PDF!

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMART HYBRID PIPELINE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [PDF] ──→ [Marker] ──→ [MD + meta.json]                        │
│                              │                                   │
│                              ▼                                   │
│                    ┌─────────────────┐                          │
│                    │  1. BUILD INDEX │                          │
│                    │  Table→Page map │                          │
│                    │  from meta.json │                          │
│                    └────────┬────────┘                          │
│                              │                                   │
│                              ▼                                   │
│                    ┌─────────────────┐                          │
│                    │  2. SCANNER     │                          │
│                    │  Extract table  │                          │
│                    │  sections from MD│                         │
│                    └────────┬────────┘                          │
│                              │                                   │
│                              ▼                                   │
│                    ┌─────────────────┐                          │
│                    │  3. JUDGE       │                          │
│                    │  Quality check  │                          │
│                    │  (6 criteria)   │                          │
│                    └────────┬────────┘                          │
│                           /   \                                  │
│                      OK /     \ BROKEN                          │
│                        ↓       ↓                                 │
│                     [Keep]  ┌──────────────┐                    │
│                            │  4. SURGERY  │                     │
│                            │ Get page from │                    │
│                            │ INDEX → pdfplumber │               │
│                            └──────┬───────┘                     │
│                                   │                              │
│                                   ▼                              │
│                            [5. INJECTION]                        │
│                                   │                              │
│                                   ▼                              │
│                            [Final MD]                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Page Finding Strategy Comparison

| Method | Speed | Accuracy | Manual Work | Recommended |
|--------|-------|----------|-------------|-------------|
| A: Full PDF scan | Slow | High | None | No |
| B: Manual mapping | Fast | High | A lot | No |
| **C: meta.json** | **Fast** | **High** | **None** | **Yes** |

### Why C (meta.json) is Best?

1. **Marker already did the work** - No duplicate work
2. **Has polygon coordinates** - Can use for Fast Mode later
3. **OK when PDF version changes** - Just re-run Marker
4. **14 codes × hundreds of tables** - Automation required

```json
// meta.json example
{
  "table_of_contents": [
    {
      "title": "Table 9.10.14.4",
      "page_id": 245,
      "polygon": [[x1,y1], [x2,y2], ...]
    }
  ]
}
```

---

## Step-by-Step Details

### Step 1: Marker (Full Conversion)

```bash
# Run for each PDF
marker_single "sources/NBC2025p1.pdf" --output_dir "marker/nbc_2025"
```

**Output:**
- `nbc_2025.md` - Full Markdown
- `nbc_2025_meta.json` - Coordinate info (polygon)
- `*.jpeg` - Extracted images

**Expected Time:** 30min~1hour per PDF (CPU)

---

### Step 2: Index Builder (meta.json → Table Map)

```python
# scripts/index_builder.py

import json
import re
from pathlib import Path
from typing import Dict

def build_table_index(meta_json_path: str) -> Dict[str, int]:
    """
    Create Table ID → Page number index from Marker meta.json

    Returns:
        {"Table 9.10.14.4": 245, "Table 9.8.2.1": 123, ...}
    """
    with open(meta_json_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    index = {}

    # Find tables in table_of_contents
    for item in meta.get('table_of_contents', []):
        title = item.get('title', '')
        page = item.get('page_id', 0)

        # Match "Table X.X.X.X" pattern
        match = re.search(r'Table\s+(\d+\.\d+\.\d+\.\d+[A-Z]?(?:-[A-Z])?)', title)
        if match:
            table_id = f"Table {match.group(1)}"
            index[table_id] = page

    return index
```

---

### Step 3: Scanner (Table Detection)

```python
# scripts/scanner.py

import re
from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class TableLocation:
    """Table location info"""
    table_id: str
    start_line: int
    end_line: int
    content: str
    page_num: int = 0  # Filled later from Index

def scan_tables(md_path: str) -> List[TableLocation]:
    """
    Find all table sections in MD file.
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    tables = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Find table heading
        table_match = re.match(r'^#{2,4}\s+(Table\s+\d+\.\d+\.\d+\.\d+[A-Z]?(?:-[A-Z])?)', line)

        if table_match:
            table_id = table_match.group(1)
            start_line = i

            # Find table end
            j = i + 1
            while j < len(lines):
                if lines[j].startswith('#'):
                    break
                j += 1

            end_line = j
            content = ''.join(lines[start_line:end_line])

            tables.append(TableLocation(
                table_id=table_id,
                start_line=start_line,
                end_line=end_line,
                content=content
            ))

            i = j
        else:
            i += 1

    return tables
```

---

### Step 4: Judge (Quality Assessment) - 6 Criteria

```python
# scripts/judge.py

from enum import Enum
from dataclasses import dataclass, field
from typing import List

class BrokenReason(Enum):
    NO_PIPES = "Flat text (no markdown table)"
    COL_MISMATCH = "Column count mismatch"
    EMPTY_CELLS = "Too many empty cells (>25%)"
    ROWSPAN_BROKEN = "Rowspan structure broken"
    NO_DATA = "No data rows"
    DUPLICATE_HEADER = "Multi-page split"
    TRUNCATED = "Content truncated"

@dataclass
class TableQuality:
    table_id: str
    is_broken: bool
    reasons: List[BrokenReason] = field(default_factory=list)
    confidence: float = 0.9

def judge_table(content: str, table_id: str = "") -> TableQuality:
    """
    Assess markdown table quality (6 criteria)

    Broken table signs:
    1. No pipes (|) → Flat Text
    2. Column count mismatch → Structure broken
    3. Empty cells 25%+ → Data loss
    4. Consecutive empty first column → Rowspan broken
    5. No data rows → Header only
    6. Duplicate headers → Multi-page split
    """
    result = TableQuality(table_id=table_id, is_broken=False)

    lines = content.strip().split('\n')
    table_lines = [l for l in lines if '|' in l and not l.strip().startswith('#')]

    # 1. Flat Text detection (no pipes)
    if len(table_lines) < 2:
        result.is_broken = True
        result.reasons.append(BrokenReason.NO_PIPES)
        return result

    # 2. Column count consistency
    col_counts = [l.count('|') - 1 for l in table_lines]
    if col_counts:
        variance = max(col_counts) - min(col_counts)
        if variance > 1:
            result.is_broken = True
            result.reasons.append(BrokenReason.COL_MISMATCH)

    # ... (remaining criteria)

    return result
```

---

### Step 5: Surgery (pdfplumber)

```python
# scripts/surgery.py

import pdfplumber
from typing import Optional

def extract_table_with_pdfplumber(
    pdf_path: str,
    page_num: int,
    table_id: str
) -> Optional[str]:
    """
    Extract table as HTML using pdfplumber.
    """
    with pdfplumber.open(pdf_path) as pdf:
        if page_num < 1 or page_num > len(pdf.pages):
            return None

        page = pdf.pages[page_num - 1]
        tables = page.extract_tables()

        if not tables:
            return None

        # Select largest table
        largest_table = max(tables, key=lambda t: len(t) * len(t[0]) if t and t[0] else 0)

        return convert_to_html(largest_table, table_id)


def convert_to_html(table_data: list, table_id: str) -> str:
    """Convert pdfplumber table data to HTML"""
    if not table_data or not table_data[0]:
        return ""

    html_lines = [f'<table class="building-code-table" id="{table_id.replace(" ", "-")}">']

    for i, row in enumerate(table_data):
        if i == 0:
            html_lines.append('  <thead>')
            html_lines.append('    <tr>')
            for cell in row:
                cell_text = escape_html(cell if cell else '')
                html_lines.append(f'      <th>{cell_text}</th>')
            html_lines.append('    </tr>')
            html_lines.append('  </thead>')
            html_lines.append('  <tbody>')
        else:
            html_lines.append('    <tr>')
            for cell in row:
                cell_text = escape_html(cell if cell else '')
                html_lines.append(f'      <td>{cell_text}</td>')
            html_lines.append('    </tr>')

    html_lines.append('  </tbody>')
    html_lines.append('</table>')

    return '\n'.join(html_lines)
```

---

### Step 6: Injection (Insert into MD)

```python
# scripts/injection.py

import re
from typing import Dict

def inject_tables(
    md_path: str,
    replacements: Dict[str, str],
    output_path: str = None
) -> str:
    """Replace broken tables in MD file with HTML"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for table_id, html in replacements.items():
        # Replace table heading + entire content
        pattern = rf'(#{2,4}\s+{re.escape(table_id)}.*?)(?=\n#{2,4}\s|\Z)'
        replacement = f'#### {table_id}\n\n{html}\n\n'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    output = output_path or md_path
    with open(output, 'w', encoding='utf-8') as f:
        f.write(content)

    return output
```

---

## Integrated Pipeline

```python
# scripts/smart_hybrid_pipeline.py

def run_smart_pipeline(
    pdf_path: str,
    marker_md_path: str,
    marker_meta_path: str,
    output_path: str
) -> dict:
    """
    Smart Hybrid Pipeline

    1. INDEX: Build Table→Page map from meta.json
    2. SCAN: Extract table sections from MD
    3. JUDGE: Quality check (6 criteria)
    4. SURGERY: Broken tables → pdfplumber
    5. INJECT: Insert into MD
    """
    stats = {
        "total": 0, "ok": 0, "broken": 0, "fixed": 0, "failed": 0
    }

    # STEP 1: BUILD INDEX
    table_index = build_table_index(marker_meta_path)

    # STEP 2: SCAN TABLES
    tables = scan_tables(marker_md_path)

    # STEP 3: JUDGE QUALITY
    broken_tables = []
    for table in tables:
        quality = judge_table(table.content, table.table_id)
        if quality.is_broken:
            table.page_num = table_index.get(table.table_id, 0)
            broken_tables.append((table, quality))

    # STEP 4: SURGERY
    replacements = {}
    for table, quality in broken_tables:
        html = extract_table_with_pdfplumber(pdf_path, table.page_num, table.table_id)
        if html:
            replacements[table.table_id] = html

    # STEP 5: INJECTION
    inject_tables(marker_md_path, replacements, output_path)

    return stats
```

---

## Execution Order

```bash
# 1. Marker batch execution (6~12 hours)
python scripts/batch_process.py marker

# 2. Hybrid pipeline (1~2 hours)
python scripts/batch_process.py

# 3. Check results
ls -la marker/*/
```

---

## Quality Criteria

| Item | Target |
|------|--------|
| Table detection rate | > 95% |
| Broken table detection accuracy | > 90% |
| pdfplumber extraction success rate | > 85% |
| Final table quality | > 95% |

---

## Broken Table Pattern Summary

| Pattern | Example | Detection Criteria |
|---------|---------|-------------------|
| **Flat Text** | `Row1 Col1 Col2 Row2...` | No pipes |
| **Column Mismatch** | Header 4 cols, body 3 cols | Column count diff > 1 |
| **Excessive Empty Cells** | `\| \| \| \|` | Empty cells 25%+ |
| **Rowspan Broken** | Repeated empty first column | Empty first col 40%+ |
| **Multi-page Split** | Duplicate headers | Same header 2+ times |
| **No Data** | Header only | Data rows < 1 |

---

## Next Document

→ [04_ROADMAP.md](./04_ROADMAP.md) - Development Roadmap
