# 04. Roadmap - 개발 로드맵

## 전체 타임라인

```
Phase 0: 준비 ────────────────┐
                              │
Phase 1: Marker 배치 ─────────┼── 1일 (6~12시간 실행)
                              │
Phase 2: 하이브리드 파이프라인 ┼── 1일
                              │
Phase 3: MCP 서버 구현 ───────┼── 2~3일
                              │
Phase 4: 검증 & 개선 ─────────┼── 2~3일
                              │
Phase 5: 다중 코드 지원 ──────┼── 1주+
                              │
Phase 6: 배포 & 문서화 ───────┘
```

---

## Phase 0: 준비 (완료)

### 목표
- 프로젝트 구조 설정
- 필요 도구 확인
- Marker bbox 출력 검증

### 체크리스트

- [ ] GitHub 저장소 생성
- [ ] 기본 디렉토리 구조 생성
- [ ] Marker bbox 출력 테스트
- [ ] PyMuPDF clip 기능 테스트
- [ ] 개발 환경 문서화

### 핵심 검증

```python
# Marker bbox 테스트
# data/marker/chunk_01/301880/301880_meta.json에서
# polygon 데이터가 실제로 사용 가능한지 확인

import fitz
doc = fitz.open("source/.../301880.pdf")
page = doc[0]  # 첫 페이지

# meta.json의 polygon을 rect로 변환
polygon = [[66.6, 42.5], [254.0, 42.5], [254.0, 70.6], [66.6, 70.6]]
rect = fitz.Rect(polygon[0][0], polygon[0][1], polygon[2][0], polygon[2][1])

text = page.get_text("text", clip=rect)
print(text)  # "Ministry of..." 출력되어야 함
```

---

## Phase 1: Marker 배치 실행 (6~12시간)

### 목표
- 모든 PDF를 Marker로 변환
- MD + meta.json 생성

### 대상 PDF (12개)

| # | 파일 | Code |
|---|------|------|
| 1 | NBC2025p1.pdf | NBC 2025 |
| 2 | NFC2025p1.pdf | NFC 2025 |
| 3 | National Plumbing...2020.pdf | NPC 2020 |
| 4 | NECB2025p1.pdf | NECB 2025 |
| 5 | bcbc_2024_web_version.pdf | BCBC 2024 |
| 6 | 2023NBCAE-V1...Alberta.pdf | ABC 2023 |
| 7 | QCC_2020p1.pdf | Quebec Building |
| 8 | QECB_2020p1.pdf | Quebec Energy |
| 9 | QPC_2020p2.pdf | Quebec Plumbing |
| 10 | QSC_2020p1.pdf | Quebec Fire |
| 11 | UGNECB_2020p1.pdf | NECB Guide |
| 12 | UGP4_2020p1.pdf | NBC Part 4 Guide |

### 실행 명령

```bash
# 배치 실행
python scripts/batch_process.py marker

# 또는 개별 실행
marker_single "sources/NBC2025p1.pdf" --output_dir "marker/nbc_2025"
```

### 체크리스트

- [ ] NBC 2025 Marker 완료
- [ ] NFC 2025 Marker 완료
- [ ] NPC 2020 Marker 완료
- [ ] NECB 2025 Marker 완료
- [ ] BCBC 2024 Marker 완료
- [ ] ABC 2023 Marker 완료
- [ ] QCC Building Marker 완료
- [ ] QCC Energy Marker 완료
- [ ] QCC Plumbing Marker 완료
- [ ] QSC Fire Marker 완료
- [ ] NECB Guide Marker 완료
- [ ] NBC Part 4 Guide Marker 완료

### 산출물

```
marker/
├── nbc_2025/
│   ├── nbc_2025.md
│   └── nbc_2025_meta.json
├── nfc_2025/
├── bcbc_2024/
└── ...
```

---

## Phase 2: 하이브리드 파이프라인 (1~2시간)

### 목표
- 깨진 테이블 감지 및 수정
- pdfplumber로 고품질 테이블 추출

### 워크플로우

```
[1. Marker MD] → [2. Scanner] → [3. Judge] → [4. Surgery] → [5. Injection]
     ↓              ↓              ↓             ↓              ↓
   전체 MD      테이블 탐지    품질 검사    pdfplumber    HTML 교체
```

### 실행 명령

```bash
# 하이브리드 파이프라인 실행
python scripts/hybrid_pipeline.py sources/NBC2025p1.pdf marker/nbc_2025

# 또는 배치 실행
python scripts/batch_process.py
```

### 체크리스트

- [ ] Scanner 스크립트 작성
- [ ] Judge 스크립트 작성
- [ ] Surgery (pdfplumber) 스크립트 작성
- [ ] Injection 스크립트 작성
- [ ] 통합 파이프라인 테스트
- [ ] 모든 PDF에 대해 파이프라인 실행

### 산출물

```
marker/
├── nbc_2025/
│   ├── nbc_2025.md          # 원본
│   ├── nbc_2025_fixed.md    # 수정본
│   └── nbc_2025_meta.json
└── ...
```

→ 상세: [06_HYBRID_PIPELINE.md](./06_HYBRID_PIPELINE.md)

---

## Phase 3: MCP 서버 구현 (2~3일)

### 목표
- structure_map 생성
- MCP 서버 구현
- 로컬 테스트 완료

### Tasks

#### Day 1: 맵 생성

- [ ] `generate_map.py` 작성
- [ ] Marker 출력에서 좌표 추출 로직 구현
- [ ] Section ID 파싱 로직 구현
- [ ] 각 코드별 map.json 생성

#### Day 2: 추출기 & DB

- [ ] `extractor.py` 작성
- [ ] Fast Mode (bbox 기반) 구현
- [ ] Slow Mode (패턴 매칭) 구현
- [ ] `database.py` SQLite + FTS5 구현

#### Day 3: MCP 서버

- [ ] `server.py` MCP 서버 구현
- [ ] Claude Desktop 연동 테스트
- [ ] 버그 수정

### 산출물

```
maps/
├── nbc_2025_map.json
├── obc_2024_map.json
├── bcbc_2024_map.json
└── checksums.json

src/
├── server.py
├── extractor.py
├── database.py
└── config.py
```

---

## Phase 4: 검증 & 개선 (2~3일)

### 목표
- 추출 정확도 검증
- 누락 섹션 보완
- 성능 최적화

### Tasks

#### 검증

- [ ] 전체 섹션 추출 테스트
- [ ] 테이블 추출 검증
- [ ] 수식 영역 처리 확인
- [ ] 다중 페이지 콘텐츠 처리

#### 보완

- [ ] 누락된 섹션 수동 추가
- [ ] 테이블 특수 처리 로직
- [ ] 에러 핸들링 강화

#### 최적화

- [ ] 추출 속도 측정 및 개선
- [ ] 메모리 사용량 최적화
- [ ] 캐싱 전략 구현

### 품질 기준

| 항목 | 목표 |
|------|------|
| 섹션 커버리지 | > 95% |
| 추출 정확도 | > 98% |
| 설정 시간 | < 2분 |
| 검색 응답 | < 1초 |

---

## Phase 3: NBC 확장 (3-5일)

### 목표
- National Building Code 지원 추가
- 다중 코드 아키텍처 검증

### 선행 조건

```
Option A: NRC 허가 받음 → 텍스트 직접 저장 가능
Option B: 허가 없음 → 좌표 방식으로 진행
```

### Tasks

- [ ] NBC PDF 획득 (NRC 아카이브)
- [ ] Marker로 NBC 파싱
- [ ] `nbc_2025_map.json` 생성
- [ ] 다중 코드 검색 로직 구현
- [ ] 코드 간 상호 참조 기능

### 구조 변경

```python
# 다중 코드 지원
@server.tool()
async def search_code(
    query: str,
    codes: list = ["OBC", "NBC"],  # 다중 코드 검색
    province: str = None           # 주별 필터
) -> str:
    ...
```

---

## Phase 4: 다중 코드 지원 (1주+)

### 목표
- BC, Alberta, Quebec 코드 추가
- 코드 비교 기능 구현

### 우선순위

| 순위 | 코드 | 이유 |
|------|------|------|
| 1 | NBC | 8개 주 커버 |
| 2 | BCBC | 캐나다 3번째 큰 주 |
| 3 | ABC (Alberta) | 에너지 산업 중심지 |
| 4 | QCC (Quebec) | 불어권, 별도 시장 |

### 고급 기능

```python
@server.tool()
async def compare_codes(
    section_id: str,
    codes: list = ["OBC", "NBC"]
) -> str:
    """
    여러 코드 간 동일 섹션 비교
    예: "9.8.2.1 OBC vs NBC 차이점"
    """
    ...

@server.tool()
async def get_provincial_requirements(
    topic: str,
    province: str
) -> str:
    """
    특정 주의 요구사항 조회
    예: "Ontario 에너지 효율 요구사항"
    """
    ...
```

---

## Phase 5: 배포 & 문서화 (3-5일)

### 목표
- GitHub 공개 배포
- 사용자 문서 완성
- 커뮤니티 피드백 수집

### Tasks

#### 문서화

- [ ] README.md (설치 가이드)
- [ ] CONTRIBUTING.md
- [ ] API 문서
- [ ] 튜토리얼 영상/GIF

#### 배포

- [ ] PyPI 패키지 등록 (선택)
- [ ] GitHub Releases 생성
- [ ] Anthropic MCP 레지스트리 등록 (가능하면)

#### 홍보

- [ ] Reddit (r/architecture, r/engineering)
- [ ] LinkedIn 포스트
- [ ] Anthropic Discord/Forum

---

## 마일스톤 요약

| 마일스톤 | 목표 날짜 | 산출물 |
|----------|----------|--------|
| **M1: OBC MVP** | +1주 | 작동하는 OBC MCP |
| **M2: 검증 완료** | +2주 | 95% 커버리지 달성 |
| **M3: NBC 추가** | +3주 | 다중 코드 지원 |
| **M4: 공개 배포** | +4주 | GitHub v1.0 릴리스 |

---

## 리스크 & 대응

| 리스크 | 확률 | 대응 |
|--------|------|------|
| Marker bbox 불완전 | 중간 | PyMuPDF로 보완 |
| PDF 버전 다양성 | 높음 | 여러 해시 지원 |
| NRC 허가 거절 | 낮음 | 좌표 방식으로 진행 |
| 성능 문제 | 낮음 | 캐싱, 인덱싱 최적화 |

---

## 다음 문서

→ [05_USER_GUIDE.md](./05_USER_GUIDE.md) - 사용자 가이드
