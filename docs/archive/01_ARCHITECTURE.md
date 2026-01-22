# 01. Architecture - 상세 아키텍처

## 핵심 개념: Map & Territory

```
Map (지도)     = structure_map.json (좌표, 페이지, ID)
Territory (땅) = 사용자의 PDF 파일 (실제 콘텐츠)
```

**비유:**
> 구글 지도가 "서울역은 북위 37.5°에 있다"고 알려주는 것처럼,
> 우리는 "9.8.2.1 조항은 245페이지, 좌표 [50,100]에 있다"고 알려줌.
>
> 실제로 서울역에 가는 건 사용자 몫.
> 실제로 텍스트를 읽는 건 사용자의 PDF에서.

---

## 데이터 흐름

### Phase 1: 개발자 측 (맵 생성)

```
┌─────────────────────────────────────────────────────────┐
│                    개발자 컴퓨터                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────┐                                            │
│  │ OBC PDF │                                            │
│  └────┬────┘                                            │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────────────────────────────────────────┐       │
│  │              Marker 파싱                     │       │
│  │  - 구조 분석 (Section, Article, Table)       │       │
│  │  - bbox 좌표 추출                            │       │
│  │  - 페이지 번호 기록                          │       │
│  │  (시간: 30분 ~ 1시간)                        │       │
│  └────┬────────────────────────────────────────┘       │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────────────────────────────────────────┐       │
│  │           structure_map.json                 │       │
│  │  - 텍스트 내용 없음 (저작권 안전)            │       │
│  │  - 좌표만 포함                               │       │
│  │  - 용량: 수백 KB                             │       │
│  └────┬────────────────────────────────────────┘       │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────┐                                            │
│  │ GitHub  │ ← 배포                                     │
│  └─────────┘                                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Phase 2: 사용자 측 (텍스트 추출)

```
┌─────────────────────────────────────────────────────────┐
│                     사용자 컴퓨터                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐    ┌──────────────────────┐       │
│  │ 사용자 OBC PDF  │    │ structure_map.json   │       │
│  │ (합법 취득)     │    │ (GitHub에서 다운)    │       │
│  └────────┬────────┘    └──────────┬───────────┘       │
│           │                        │                    │
│           │    ┌───────────────────┘                    │
│           ▼    ▼                                        │
│  ┌─────────────────────────────────────────────┐       │
│  │            PDF 해시 검증                     │       │
│  │  - 사용자 PDF 해시 계산                      │       │
│  │  - checksums.json과 비교                    │       │
│  │  - 일치: Fast Mode / 불일치: Slow Mode      │       │
│  └────┬────────────────────────────────────────┘       │
│       │                                                 │
│       ▼ (일치 시)                                       │
│  ┌─────────────────────────────────────────────┐       │
│  │         PyMuPDF 좌표 기반 추출               │       │
│  │                                              │       │
│  │  for item in structure_map:                 │       │
│  │      page = doc[item.page]                  │       │
│  │      text = page.get_text(clip=item.bbox)   │       │
│  │                                              │       │
│  │  (시간: 10초 ~ 1분)                          │       │
│  └────┬────────────────────────────────────────┘       │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────────────────────────────────────────┐       │
│  │              로컬 SQLite DB                  │       │
│  │  - section_id, content, type, page          │       │
│  │  - 검색 인덱스 생성                          │       │
│  └────┬────────────────────────────────────────┘       │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────────────────────────────────────────┐       │
│  │              MCP 서버 실행                   │       │
│  │  - search_code(query)                       │       │
│  │  - get_section(id)                          │       │
│  │  - get_table(id)                            │       │
│  └────┬────────────────────────────────────────┘       │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────┐                                            │
│  │ Claude  │ ← MCP 연결                                 │
│  └─────────┘                                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## structure_map.json 스키마

### 기본 구조

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

### 타입 정의

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
  title?: string;       // 제목 (좌표로 추출 가능하면 생략)
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
  spans_pages?: number[];  // 여러 페이지에 걸친 테이블
}
```

---

## PDF 버전 검증

### 왜 필요한가?

```
문제: 사용자 PDF가 개발자 PDF와 다른 버전이면?
     → 좌표가 전부 어긋남
     → 잘못된 텍스트 추출
```

### 검증 로직

```python
import hashlib

def verify_pdf(user_pdf_path: str, expected_hash: str) -> bool:
    """PDF 파일의 해시값 검증"""
    with open(user_pdf_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    return file_hash == expected_hash

def get_extraction_mode(user_pdf: str, checksums: dict) -> str:
    """추출 모드 결정"""
    user_hash = calculate_hash(user_pdf)

    if user_hash in checksums.values():
        return "fast"   # 좌표 기반 추출
    else:
        return "slow"   # 패턴 매칭 추출 (fallback)
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
    "note": "오타 수정 버전"
  }
}
```

---

## Fallback 모드

### 해시 불일치 시

```python
def slow_mode_extraction(pdf_path: str, structure_map: dict) -> dict:
    """
    해시 불일치 시 패턴 매칭으로 추출
    좌표 대신 텍스트 패턴 사용
    """
    doc = fitz.open(pdf_path)
    results = {}

    for section in structure_map['sections']:
        # 좌표 대신 ID 패턴으로 검색
        pattern = rf"^{re.escape(section['id'])}\.\s+"

        for page_num, page in enumerate(doc):
            text = page.get_text()
            if re.search(pattern, text, re.MULTILINE):
                # 해당 섹션 텍스트 추출
                results[section['id']] = extract_section_text(page, pattern)
                break

    return results
```

---

## 성능 비교

| 모드 | 방식 | 시간 | 정확도 |
|------|------|------|--------|
| **Fast** | 좌표 기반 | 10초 ~ 1분 | 100% (검수된 좌표) |
| **Slow** | 패턴 매칭 | 5분 ~ 10분 | 95% (패턴 의존) |
| **Full** | Marker 재실행 | 30분 ~ 1시간 | 98% (Marker 품질) |

---

## 다음 문서

→ [02_IMPLEMENTATION.md](./02_IMPLEMENTATION.md) - 구현 가이드
