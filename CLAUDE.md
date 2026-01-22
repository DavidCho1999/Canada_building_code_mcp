# CLAUDE.md - Canadian Building Code MCP

## 프로젝트 정보

- **프로젝트명**: Canadian Building Code MCP
- **목적**: 캐나다 Building Code를 Claude에서 검색/참조할 수 있는 MCP 서버
- **전략**: "Map & Territory" - 좌표만 배포, 텍스트는 사용자 PDF에서 추출
- **상태**: Phase 1-2 완료 (Docling + Map 생성)

---

## 핵심 개념

### 법적 안전 전략
```
배포: 좌표 (page, bbox), Section ID, 구조 타입
배포 안 함: 실제 텍스트, 테이블 데이터
→ 99% 법적 안전
```

### 현재 파이프라인 (Docling 기반)
```
[PDF] → [Docling] → [MD + JSON]
            ↓
    [generate_map.py] Section 추출 + TF-IDF 키워드
            ↓
    [maps/*.json] 좌표 맵 생성
            ↓
    [MCP Server] Mode A (맵만) / Mode B (BYOD 텍스트)
```

---

## 파일 구조

```
building_code_mcp/
├── docs/               # 문서
├── scripts/            # 파이프라인 스크립트
├── src/                # MCP 서버 코드 (나중에)
├── marker/             # Marker 출력물
├── sources/            # PDF (gitignore)
└── maps/               # structure_map.json
```

---

## 개발 규칙

### 0. 메모리 제한 (중요!)
- **사용자 환경: 16GB RAM 랩탑**
- Docling 변환은 **반드시 하나씩** 순차 실행
- 병렬 실행 절대 금지 → 메모리 부족으로 시스템 크래시
- 큰 PDF (>50MB)는 특히 주의

### 1. PDF는 절대 git에 올리지 않음
- sources/ 폴더는 .gitignore에 포함
- 저작권 문제

### 2. 테이블 품질 판별 6가지 기준
1. NO_PIPES - Flat text
2. COL_MISMATCH - 열 개수 불일치
3. EMPTY_CELLS - 빈 셀 25%+
4. ROWSPAN_BROKEN - 첫 열 빈 셀 반복
5. NO_DATA - 헤더만
6. DUPLICATE_HEADER - Multi-page 분리

### 3. 페이지 찾기는 meta.json 사용
- PDF 전체 스캔 ❌
- 수동 매핑 ❌
- meta.json → Table Index ✅

---

## 대상 코드 (14개)

**National (4):** NBC, NFC, NPC, NECB (2025)
**Provincial (7):** OBC, BCBC, ABC, QCC×4
**User's Guides (3):** NBC Part 9, Part 4, NECB

---

## 실행 명령

```bash
# 1. PDF → MD/JSON 변환 (하나씩!)
python scripts/convert_with_docling.py sources/NBC2025p1.pdf

# 2. Map 생성
python scripts/generate_map.py docling_output/nbc2025p1/

# 3. MCP 서버 실행
python src/mcp_server.py
```

---

## 변환 진행 상황 (완료)

| 코드 | Docling | Map | Sections |
|------|---------|-----|----------|
| NPC2025 | ✅ | ✅ | 595 |
| NFC2025 | ✅ | ✅ | 1,407 |
| NBC2025 | ✅ | ✅ | 4,213 |
| NECB2025 | ✅ | ✅ | 777 |
| BCBC2024 | ✅ | ✅ | 2,645 |
| OBC Vol1 | ✅ | ✅ | 3,580 |
| OBC Vol2 | ✅ | ✅ | 345 |
| QCC2020 | ✅ | ✅ | 3,925 |
| QECB2020 | ✅ | ✅ | 612 |
| QPC2020 | ✅ | ✅ | 615 |
| QSC2020 | ✅ | ✅ | 1,408 |
| UGP4 | ✅ | ✅ | 21 |
| IUGP9 | ✅ | ✅ | 1,399 |
| UGNECB2020 | ✅ | ✅ | 0 |
| Alberta | ✅ | ✅ | 4,165 |

**Total: 25,707 sections indexed**

---

## 참고 문서

- `docs/PDF_DOWNLOAD_LINKS.md` - PDF 다운로드 링크
- `docs/archive/` - 이전 문서들
