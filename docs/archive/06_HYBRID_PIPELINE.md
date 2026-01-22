# 06. Hybrid Pipeline - 하이브리드 파이프라인

## 개요

Marker의 텍스트 추출 능력 + pdfplumber의 테이블 추출 능력을 결합한 파이프라인.

**핵심 발견:** Marker의 `meta.json`에 이미 페이지 정보가 있음 → PDF 전체 스캔 불필요!

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
│                    │  meta.json에서   │                          │
│                    │  Table→Page 맵핑 │                          │
│                    └────────┬────────┘                          │
│                              │                                   │
│                              ▼                                   │
│                    ┌─────────────────┐                          │
│                    │  2. SCANNER     │                          │
│                    │  MD에서 테이블   │                          │
│                    │  구간 추출      │                          │
│                    └────────┬────────┘                          │
│                              │                                   │
│                              ▼                                   │
│                    ┌─────────────────┐                          │
│                    │  3. JUDGE       │                          │
│                    │  6가지 기준으로  │                          │
│                    │  품질 검사      │                          │
│                    └────────┬────────┘                          │
│                           /   \                                  │
│                      OK /     \ BROKEN                          │
│                        ↓       ↓                                 │
│                     [유지]  ┌──────────────┐                    │
│                            │  4. SURGERY  │                     │
│                            │ INDEX에서 page │                    │
│                            │ 조회 → pdfplumber │                 │
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

## 페이지 찾기 전략 비교

| 방법 | 속도 | 정확도 | 노가다 | 추천 |
|------|------|--------|--------|------|
| A: PDF 전체 스캔 | 느림 | 높음 | 없음 | ❌ |
| B: 수동 매핑 | 빠름 | 높음 | 많음 | ❌ |
| **C: meta.json** | **빠름** | **높음** | **없음** | **✅** |

### 왜 C (meta.json)가 최고인가?

1. **Marker가 이미 작업 완료** - 중복 작업 없음
2. **polygon 좌표도 있음** - 나중에 Fast Mode에서 활용
3. **PDF 버전 바뀌어도 OK** - Marker 다시 돌리면 자동 갱신
4. **14개 코드 × 수백 테이블** - 자동화 필수

```json
// meta.json 예시
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

## 단계별 상세

### 1단계: Marker (전체 변환)

```bash
# 각 PDF에 대해 실행
marker_single "sources/NBC2025p1.pdf" --output_dir "marker/nbc_2025"
```

**출력물:**
- `nbc_2025.md` - 전체 Markdown
- `nbc_2025_meta.json` - 좌표 정보 (polygon)
- `*.jpeg` - 추출된 이미지들

**예상 시간:** PDF당 30분~1시간 (CPU)

---

### 2단계: Index Builder (meta.json → Table 맵)

```python
# scripts/index_builder.py

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
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"Saved index with {len(index)} tables")


def load_index(index_path: str) -> dict:
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)
```

---

### 3단계: Scanner (테이블 탐지)

```python
# scripts/scanner.py

import re
from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class TableLocation:
    """테이블 위치 정보"""
    table_id: str
    start_line: int
    end_line: int
    content: str
    page_num: int = 0  # Index에서 나중에 채움

def scan_tables(md_path: str) -> List[TableLocation]:
    """
    MD 파일에서 모든 테이블 구간을 찾습니다.
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    tables = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # 테이블 헤딩 찾기
        table_match = re.match(r'^#{2,4}\s+(Table\s+\d+\.\d+\.\d+\.\d+[A-Z]?(?:-[A-Z])?)', line)

        if table_match:
            table_id = table_match.group(1)
            start_line = i

            # 테이블 끝 찾기
            j = i + 1
            empty_count = 0

            while j < len(lines):
                if lines[j].startswith('#'):
                    break
                if lines[j].strip() == '':
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0
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

### 4단계: Judge (품질 판별) - 6가지 기준

```python
# scripts/judge.py

import re
from dataclasses import dataclass, field
from typing import List
from enum import Enum

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
    details: List[str] = field(default_factory=list)
    confidence: float = 0.9

    @property
    def summary(self) -> str:
        if not self.is_broken:
            return f"✅ {self.table_id}: OK"
        reasons_str = ", ".join(r.name for r in self.reasons)
        return f"❌ {self.table_id}: {reasons_str}"


def judge_table(content: str, table_id: str = "") -> TableQuality:
    """
    마크다운 테이블 품질 판별 (6가지 기준)

    깨진 테이블 징후:
    1. 파이프(|) 없음 → Flat Text
    2. 열 개수 불일치 → 구조 깨짐
    3. 빈 셀 25%+ → 데이터 손실
    4. 첫 열 연속 빈칸 → Rowspan 깨짐
    5. 데이터 행 없음 → 헤더만 있음
    6. 중복 헤더 → Multi-page 분리
    """
    result = TableQuality(table_id=table_id, is_broken=False)

    lines = content.strip().split('\n')
    table_lines = [l for l in lines if '|' in l and not l.strip().startswith('#')]

    # 1. Flat Text 감지 (파이프 없음)
    if len(table_lines) < 2:
        result.is_broken = True
        result.reasons.append(BrokenReason.NO_PIPES)
        result.details.append(f"Only {len(table_lines)} lines with pipes")
        result.confidence = 0.95
        return result

    # 2. 열 개수 일관성
    col_counts = [l.count('|') - 1 for l in table_lines]
    if col_counts:
        variance = max(col_counts) - min(col_counts)
        if variance > 1:
            result.is_broken = True
            result.reasons.append(BrokenReason.COL_MISMATCH)
            result.details.append(f"Columns vary: {min(col_counts)}~{max(col_counts)}")

    # 3. 빈 셀 비율 (25% 이상이면 의심)
    total_pipes = content.count('|')
    empty_patterns = content.count('| |') + content.count('||') + content.count('|  |')
    if total_pipes > 10:
        empty_ratio = empty_patterns / (total_pipes / 2)
        if empty_ratio > 0.25:
            result.is_broken = True
            result.reasons.append(BrokenReason.EMPTY_CELLS)
            result.details.append(f"Empty cell ratio: {empty_ratio:.0%}")

    # 4. Rowspan 깨짐 (첫 열이 연속으로 빈 경우)
    if len(table_lines) > 3:
        first_cells = []
        for line in table_lines[2:]:  # 헤더+구분선 제외
            parts = line.split('|')
            if len(parts) > 1:
                first_cells.append(parts[1].strip())

        if first_cells:
            empty_first = sum(1 for c in first_cells if c == '')
            if empty_first / len(first_cells) > 0.4:
                result.is_broken = True
                result.reasons.append(BrokenReason.ROWSPAN_BROKEN)
                result.details.append(f"{empty_first}/{len(first_cells)} empty first cells")

    # 5. 데이터 행 부족
    data_rows = len(table_lines) - 2
    if data_rows < 1:
        result.is_broken = True
        result.reasons.append(BrokenReason.NO_DATA)
        result.details.append("Header only, no data")

    # 6. 중복 헤더 (Multi-page 분리)
    if table_lines:
        header = table_lines[0]
        header_count = sum(1 for l in table_lines if l == header)
        if header_count > 1:
            result.is_broken = True
            result.reasons.append(BrokenReason.DUPLICATE_HEADER)
            result.details.append(f"Header repeated {header_count} times")

    # 7. 내용 잘림 감지
    if '...' in content or 'truncated' in content.lower():
        result.is_broken = True
        result.reasons.append(BrokenReason.TRUNCATED)

    # Confidence 계산
    if result.is_broken:
        result.confidence = min(0.5 + len(result.reasons) * 0.12, 0.95)

    return result
```

---

### 5단계: Surgery (pdfplumber 수술)

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
    pdfplumber로 테이블을 HTML로 추출합니다.
    """
    with pdfplumber.open(pdf_path) as pdf:
        if page_num < 1 or page_num > len(pdf.pages):
            return None

        page = pdf.pages[page_num - 1]
        tables = page.extract_tables()

        if not tables:
            return None

        # 가장 큰 테이블 선택
        largest_table = max(tables, key=lambda t: len(t) * len(t[0]) if t and t[0] else 0)

        return convert_to_html(largest_table, table_id)


def convert_to_html(table_data: list, table_id: str) -> str:
    """pdfplumber 테이블 데이터를 HTML로 변환"""
    if not table_data or not table_data[0]:
        return ""

    html_lines = [f'<table class="obc-table" id="{table_id.replace(" ", "-")}">']

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


def escape_html(text: str) -> str:
    return (text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
    )
```

---

### 6단계: Injection (MD에 삽입)

```python
# scripts/injection.py

import re
from typing import Dict

def inject_tables(
    md_path: str,
    replacements: Dict[str, str],
    output_path: str = None
) -> str:
    """MD 파일의 깨진 테이블을 HTML로 교체"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for table_id, html in replacements.items():
        # 테이블 헤딩 + 내용 전체 교체
        pattern = rf'(#{2,4}\s+{re.escape(table_id)}.*?)(?=\n#{2,4}\s|\Z)'
        replacement = f'#### {table_id}\n\n{html}\n\n'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    output = output_path or md_path
    with open(output, 'w', encoding='utf-8') as f:
        f.write(content)

    return output
```

---

## 통합 파이프라인

```python
# scripts/smart_hybrid_pipeline.py

import json
from pathlib import Path
from typing import Dict, List

from index_builder import build_table_index, build_table_index_fallback, save_index, load_index
from scanner import scan_tables
from judge import judge_table
from surgery import extract_table_with_pdfplumber
from injection import inject_tables


def run_smart_pipeline(
    pdf_path: str,
    marker_md_path: str,
    marker_meta_path: str,
    output_path: str,
    index_cache_path: str = None
) -> dict:
    """
    스마트 하이브리드 파이프라인

    1. INDEX: meta.json에서 Table→Page 맵 빌드
    2. SCAN: MD에서 테이블 구간 추출
    3. JUDGE: 품질 검사 (6가지 기준)
    4. SURGERY: 깨진 테이블 → pdfplumber
    5. INJECT: MD에 삽입
    """
    stats = {
        "total": 0, "ok": 0, "broken": 0, "fixed": 0, "failed": 0
    }

    # ═══════════════════════════════════════════════════════════
    # STEP 1: BUILD INDEX
    # ═══════════════════════════════════════════════════════════
    print("📇 Building table index...")

    if index_cache_path and Path(index_cache_path).exists():
        table_index = load_index(index_cache_path)
        print(f"   Loaded cached index: {len(table_index)} tables")
    elif Path(marker_meta_path).exists():
        table_index = build_table_index(marker_meta_path)
        print(f"   Built from meta.json: {len(table_index)} tables")
        if index_cache_path:
            save_index(table_index, index_cache_path)
    else:
        print("   ⚠️ meta.json not found, scanning PDF (slow)...")
        table_index = build_table_index_fallback(pdf_path)
        print(f"   Built from PDF: {len(table_index)} tables")

    # ═══════════════════════════════════════════════════════════
    # STEP 2: SCAN TABLES
    # ═══════════════════════════════════════════════════════════
    print("\n📋 Scanning tables...")
    tables = scan_tables(marker_md_path)
    stats["total"] = len(tables)
    print(f"   Found {len(tables)} tables")

    # ═══════════════════════════════════════════════════════════
    # STEP 3: JUDGE QUALITY
    # ═══════════════════════════════════════════════════════════
    print("\n🔍 Judging quality...")

    broken_tables = []

    for table in tables:
        quality = judge_table(table.content, table.table_id)

        if quality.is_broken:
            table.page_num = table_index.get(table.table_id, 0)
            broken_tables.append((table, quality))
            print(f"   ❌ {table.table_id} (p.{table.page_num})")
            stats["broken"] += 1
        else:
            print(f"   ✅ {table.table_id}")
            stats["ok"] += 1

    # ═══════════════════════════════════════════════════════════
    # STEP 4: SURGERY
    # ═══════════════════════════════════════════════════════════
    print("\n🔧 Fixing broken tables...")

    replacements: Dict[str, str] = {}

    for table, quality in broken_tables:
        if table.page_num == 0:
            print(f"   ⚠️ {table.table_id}: Page unknown, skipping")
            stats["failed"] += 1
            continue

        html = extract_table_with_pdfplumber(pdf_path, table.page_num, table.table_id)

        if html:
            replacements[table.table_id] = html
            print(f"   ✅ Fixed: {table.table_id}")
            stats["fixed"] += 1
        else:
            print(f"   ❌ Failed: {table.table_id}")
            stats["failed"] += 1

    # ═══════════════════════════════════════════════════════════
    # STEP 5: INJECTION
    # ═══════════════════════════════════════════════════════════
    print("\n💉 Injecting fixes...")
    inject_tables(marker_md_path, replacements, output_path)

    # Summary
    print(f"\n{'='*50}")
    print("✨ COMPLETE")
    print(f"{'='*50}")
    print(f"   Total:  {stats['total']}")
    print(f"   OK:     {stats['ok']}")
    print(f"   Broken: {stats['broken']}")
    print(f"   Fixed:  {stats['fixed']}")
    print(f"   Failed: {stats['failed']}")
    print(f"\n   Output: {output_path}")

    return stats


# CLI
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python smart_hybrid_pipeline.py <pdf_path> <marker_dir>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    marker_dir = Path(sys.argv[2])
    stem = Path(pdf_path).stem

    run_smart_pipeline(
        pdf_path=pdf_path,
        marker_md_path=str(marker_dir / f"{stem}.md"),
        marker_meta_path=str(marker_dir / f"{stem}_meta.json"),
        output_path=str(marker_dir / f"{stem}_fixed.md"),
        index_cache_path=str(marker_dir / f"{stem}_table_index.json")
    )
```

---

## 배치 실행

```python
# scripts/batch_process.py

from pathlib import Path
import subprocess

PDFS = [
    ("sources/NBC2025p1.pdf", "marker/nbc_2025"),
    ("sources/NFC2025p1.pdf", "marker/nfc_2025"),
    ("sources/bcbc_2024_web_version_20240409.pdf", "marker/bcbc_2024"),
    ("sources/2023NBCAE-V1_National_Building_Code2023_Alberta_Edition.pdf", "marker/abc_2023"),
    # ... 나머지
]

def batch_marker():
    """모든 PDF에 대해 Marker 실행"""
    for pdf_path, output_dir in PDFS:
        print(f"\n{'='*60}")
        print(f"Processing: {pdf_path}")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        subprocess.run(["marker_single", pdf_path, "--output_dir", output_dir])

def batch_hybrid():
    """모든 Marker 출력에 대해 파이프라인 실행"""
    from smart_hybrid_pipeline import run_smart_pipeline

    for pdf_path, marker_dir in PDFS:
        if Path(marker_dir).exists():
            stem = Path(pdf_path).stem
            run_smart_pipeline(
                pdf_path=pdf_path,
                marker_md_path=f"{marker_dir}/{stem}.md",
                marker_meta_path=f"{marker_dir}/{stem}_meta.json",
                output_path=f"{marker_dir}/{stem}_fixed.md",
                index_cache_path=f"{marker_dir}/{stem}_table_index.json"
            )

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "marker":
        batch_marker()
    else:
        batch_hybrid()
```

---

## 실행 순서

```bash
# 1. Marker 배치 실행 (6~12시간)
python scripts/batch_process.py marker

# 2. 하이브리드 파이프라인 (1~2시간)
python scripts/batch_process.py

# 3. 결과 확인
ls -la marker/*/
```

---

## 품질 기준

| 항목 | 목표 |
|------|------|
| 테이블 감지율 | > 95% |
| 깨진 테이블 판별 정확도 | > 90% |
| pdfplumber 추출 성공률 | > 85% |
| 최종 테이블 품질 | > 95% |

---

## 깨진 테이블 패턴 정리

| 패턴 | 예시 | 감지 기준 |
|------|------|----------|
| **Flat Text** | `Row1 Col1 Col2 Row2...` | 파이프 없음 |
| **열 불일치** | 헤더 4열, 바디 3열 | 열 개수 차이 > 1 |
| **빈 셀 과다** | `\| \| \| \|` | 빈 셀 25%+ |
| **Rowspan 깨짐** | 첫 열 빈 셀 반복 | 빈 첫 열 40%+ |
| **Multi-page 분리** | 헤더 중복 | 같은 헤더 2회+ |
| **데이터 없음** | 헤더만 | 데이터 행 < 1 |

---

## 다음 문서

→ [04_ROADMAP.md](./04_ROADMAP.md) - 개발 로드맵
