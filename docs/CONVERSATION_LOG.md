# MCP 프로젝트 대화 기록

> 2026-01-21 기준

---

## 핵심 결정사항

### 1. "좌표 오버레이" (Map & Territory) 전략 채택

**개념:**
- 배포: 좌표(page, bbox), Section ID, 구조 타입
- 배포 안 함: 실제 텍스트, 테이블 데이터
- 사용자가 자신의 합법적 PDF에서 텍스트 추출

**법적 안전성: 99%**
- 좌표는 "사실(fact)" → 저작권 보호 대상 아님
- "지도를 주고, 땅은 사용자가 가져옴"

### 2. Fast Mode vs Slow Mode

| Mode | 조건 | 방식 |
|------|------|------|
| **Fast Mode** | PDF 해시 일치 | 좌표(bbox) 기반 추출 |
| **Slow Mode** | PDF 해시 불일치 | 패턴 매칭 추출 |

### 3. 대상 코드 14개 확정

**National (4):** NBC, NFC, NPC, NECB (전부 2025)
**Provincial (7):** OBC, BCBC, ABC, QCC×4
**User's Guides (3):** NBC Part 9, NBC Part 4, NECB Guide

---

## 주요 발견

### Marker polygon 데이터 확인

`data/marker/chunk_01/301880/301880_meta.json`에서:
```json
{
  "title": "TO: BUILDING CODE USERS",
  "page_id": 1,
  "polygon": [
    [66.33984375, 204.56146240234375],
    [232.76397705078125, 204.56146240234375],
    [232.76397705078125, 216.56146240234375],
    [66.33984375, 216.56146240234375]
  ]
}
```

→ PyMuPDF `page.get_text("text", clip=rect)` 로 추출 가능

### Marker가 가장 시간 오래 걸림

| 단계 | 시간 |
|------|------|
| Marker PDF 파싱 | 30분~1시간+ (CPU) |
| polygon → structure_map | 몇 초 |
| DB 생성 | 몇 초 |
| MCP 서버 설정 | 몇 분 |

---

## 법적 분석

### 캐나다 코드 상태

| Code | 상태 | 근거 |
|------|------|------|
| OBC | ✅ 명시적 허용 | "non-commercial use" 명시 |
| NBC/NFC/NPC/NECB | ✅ 좌표만 = 안전 | NRC 무료 PDF 제공 |
| BCBC | ✅ 좌표만 = 안전 | BC Gov 무료 제공 |
| ABC | ✅ 좌표만 = 안전 | NRC 무료 PDF 제공 |
| Quebec | ✅ 좌표만 = 안전 | NRC 무료 PDF 제공 |

### 미국 vs 캐나다

- **미국**: ICC 저작권 분쟁, 소송 진행 중
- **캐나다**: 법적으로 더 명확, 안전

---

## 아키텍처 요약

```
[개발자 측]
PDF → Marker → polygon 추출 → structure_map.json
                                    ↓
                              배포 (GitHub)

[사용자 측]
공식 PDF 다운로드 ← 사용자
        ↓
structure_map.json + PDF → 텍스트 추출 → SQLite DB
                                            ↓
                                      MCP Server
                                            ↓
                                      Claude Desktop
```

---

## 다음 단계

1. **PDF 다운로드** - 14개 코드
2. **Marker 실행** - 각 PDF 파싱 (30분~1시간 × 14)
3. **structure_map 생성** - polygon → bbox 변환
4. **추출 테스트** - PyMuPDF clip 검증
5. **MCP 서버 구현** - Python MCP SDK

---

## 연락처 (허가 필요시)

| 기관 | 이메일 |
|------|--------|
| NRC (National) | Codes@nrc-cnrc.gc.ca |
| BC (Provincial) | ipp@mail.qp.gov.bc.ca |

---

## 하이브리드 파이프라인 (추가됨)

Marker + pdfplumber 결합 전략:

```
[PDF] → [1. Marker] → [MD]
              ↓
        [2. Scanner] - "### Table" 탐지
              ↓
        [3. Judge] - 품질 검사
           /    \
       멀쩡함   깨짐
         │       │
        유지   [4. Surgery] - pdfplumber
                 │
        [5. Injection] - HTML 교체
              ↓
        [Final MD]
```

→ 상세: `06_HYBRID_PIPELINE.md`

---

## 파일 구조

```
H:\My Drive\lab\building_code_mcp\
├── README.md                 # 프로젝트 개요
├── 01_ARCHITECTURE.md        # 아키텍처 상세
├── 02_IMPLEMENTATION.md      # 구현 코드
├── 03_LEGAL.md               # 법적 분석
├── 04_ROADMAP.md             # 개발 로드맵 (업데이트됨)
├── 05_USER_GUIDE.md          # 사용자 가이드
├── 06_HYBRID_PIPELINE.md     # 하이브리드 파이프라인 (NEW)
├── PDF_DOWNLOAD_LINKS.md     # PDF 링크 목록
├── CONVERSATION_LOG.md       # 이 파일
├── marker/
│   └── obc_part9/
│       ├── 301880_full.md    # OBC Part 9 Marker 출력
│       └── 301880_meta.json  # 좌표 정보
└── sources/                  # PDF 저장 폴더 (12개 다운로드 완료)
```
