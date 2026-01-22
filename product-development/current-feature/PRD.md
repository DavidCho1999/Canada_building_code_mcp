# PRD: Canadian Building Code MCP Server

> Version: 1.0
> Date: 2026-01-21
> Status: Draft

---

## 1. Overview

### 1.1 Problem Statement

캐나다 건축 전문가들(건축사, 엔지니어, 계약자, 검사관)은 프로젝트 수행 시 **14개 이상의 Building Code**를 참조해야 한다. 현재 상황:

- **비효율적인 검색**: 1,000페이지 이상 PDF를 수동으로 탐색
- **버전 혼란**: National vs Provincial 코드 차이점 파악 어려움
- **테이블 접근성**: 복잡한 테이블 데이터(Fire Separation, Egress 등) 찾기 어려움
- **AI 활용 불가**: Claude 같은 AI 도구에서 Building Code 직접 참조 불가능

### 1.2 Target Users

| 사용자 유형 | 주요 니즈 | 사용 빈도 |
|------------|----------|----------|
| **건축사 (Architects)** | 설계 단계에서 코드 준수 확인 | 일일 |
| **건축 엔지니어** | 구조/화재/에너지 요구사항 확인 | 일일 |
| **계약자/시공자** | 현장 작업 기준 확인 | 주간 |
| **건축 검사관** | 준수 여부 검토 | 일일 |
| **건축 학생** | 학습 및 프로젝트 | 주간 |

**Primary Persona: Sarah - 캐나다 건축사**
- 10년 경력, 온타리오 소재
- 주로 주거용 프로젝트 진행
- Claude Desktop 사용 경험 있음
- OBC Part 9 (소규모 건물) 주로 참조

### 1.3 Product Vision

> "Claude에게 캐나다 Building Code를 가르쳐서, 건축 전문가가 자연어로 코드를 검색하고 참조할 수 있게 한다."

**핵심 가치:**
1. **접근성**: 복잡한 Building Code를 쉽게 검색
2. **정확성**: 공식 코드 텍스트 직접 참조 (환각 방지)
3. **법적 안전성**: 저작권 문제 없는 "좌표 오버레이" 방식

---

## 2. User Needs & JTBD

### 2.1 Jobs to be Done

**Job 1: 특정 요구사항 찾기**
> "내가 설계 중인 주거용 건물의 Fire Separation 요구사항이 무엇인지 알고 싶다"

- Trigger: 설계 검토 시
- 현재 방법: PDF 검색 또는 목차 탐색
- 원하는 결과: 관련 조항 및 테이블 즉시 확인

**Job 2: 코드 간 비교**
> "OBC와 NBC의 차이점을 알고 싶다"

- Trigger: 여러 주에서 프로젝트 진행 시
- 현재 방법: 두 PDF를 열어 수동 비교
- 원하는 결과: 동일 섹션 간 차이점 자동 표시

**Job 3: 컨텍스트 이해**
> "이 조항이 왜 이렇게 정해졌는지, 관련 조항은 무엇인지 알고 싶다"

- Trigger: 코드 해석 필요 시
- 현재 방법: User's Guide 참조, 전문가 상담
- 원하는 결과: 상위/하위 조항, 관련 조항 즉시 탐색

### 2.2 Pain Points

| Pain Point | 심각도 | 현재 해결책 |
|------------|--------|------------|
| PDF 검색 결과 부정확 | 높음 | 수동 탐색 |
| 테이블 데이터 복사 불가 | 높음 | 직접 타이핑 |
| 코드 업데이트 추적 어려움 | 중간 | 뉴스레터 구독 |
| AI 환각 (잘못된 코드 인용) | 높음 | 직접 검증 필수 |

### 2.3 Desired Outcomes

1. **검색 시간 단축**: 평균 5분 → 30초
2. **정확도 향상**: AI 환각 제거 (공식 텍스트 직접 참조)
3. **학습 곡선 감소**: 코드 구조 탐색 용이
4. **생산성 향상**: 코드 참조 작업 자동화

---

## 3. Feature Specifications

### 3.1 Core Features

| # | 기능 | 우선순위 | 설명 |
|---|------|---------|------|
| 1 | `list_codes` | P0 | 지원 코드 목록 조회 |
| 2 | `search_code` | P0 | 키워드 검색 |
| 3 | `get_section` | P0 | 섹션 ID로 조회 |
| 4 | `get_hierarchy` | P1 | 상위/하위 조항 탐색 |
| 5 | `set_pdf_path` | P1 | 사용자 PDF 연결 (BYOD) |
| 6 | `compare_codes` | P2 | 코드 간 비교 |

### 3.2 Feature Details

#### 3.2.1 `list_codes` - 코드 목록 조회

**Input:** 없음
**Output:** 지원 코드 목록 (코드명, 버전, 상태)

```
사용자: "어떤 코드를 검색할 수 있어?"
Claude: [list_codes 호출]
응답: "현재 NBC 2025, OBC 2024, BCBC 2024... 총 14개 코드 지원"
```

#### 3.2.2 `search_code` - 키워드 검색

**Input:**
- `query`: 검색어 (필수)
- `code`: 코드 지정 (선택, 기본값: 전체)
- `limit`: 결과 수 (선택, 기본값: 10)

**Output:** 매칭 섹션 목록 (ID, 제목, 페이지, 관련도)

```
사용자: "garage fire separation 요구사항 찾아줘"
Claude: [search_code(query="fire separation garage", code="OBC")]
응답: "OBC 9.10.14.1에서 관련 내용을 찾았습니다..."
```

#### 3.2.3 `get_section` - 섹션 조회

**Input:**
- `id`: 섹션 ID (필수, 예: "9.10.14.1")
- `code`: 코드 지정 (필수)

**Output:**
- Mode A (Map Only): 제목, 페이지 번호, 키워드
- Mode B (BYOD): 위 항목 + 실제 텍스트 내용

```
사용자: "9.10.14.1 조항 내용 보여줘"
Claude: [get_section(id="9.10.14.1", code="OBC")]
응답: "[조항 내용...]"
```

#### 3.2.4 `get_hierarchy` - 계층 탐색

**Input:**
- `id`: 섹션 ID (필수)
- `code`: 코드 지정 (필수)

**Output:** 부모 섹션, 자식 섹션, 형제 섹션

```
사용자: "9.10.14 관련 조항들 전체 보여줘"
Claude: [get_hierarchy(id="9.10.14", code="OBC")]
응답: "상위: Section 9.10 Fire Protection
       하위: 9.10.14.1, 9.10.14.2, 9.10.14.3..."
```

#### 3.2.5 `set_pdf_path` - PDF 연결 (BYOD)

**Input:**
- `code`: 코드 지정 (필수)
- `path`: PDF 파일 경로 (필수)

**Output:** 연결 성공/실패, 버전 확인 결과

```
사용자: "내 OBC PDF 파일 연결해줘"
Claude: [set_pdf_path(code="OBC", path="C:/codes/OBC2024.pdf")]
응답: "OBC 2024 PDF 연결 완료. 이제 전체 텍스트를 조회할 수 있습니다."
```

### 3.3 Out of Scope (v1.0)

- 코드 해석 및 컨설팅 (AI 판단 필요)
- 도면 분석 연동
- 코드 변경 알림 기능
- 다국어 지원 (영어 외)
- 미국 코드 (ICC) 지원

---

## 4. User Experience

### 4.1 User Flow

```
[1. 설치]
└─> pip install → MCP 서버 설정 → Claude Desktop 연결

[2. 기본 사용 (Map Only)]
└─> 키워드 검색 → 섹션 ID 확인 → 페이지 번호로 PDF 직접 참조

[3. 고급 사용 (BYOD)]
└─> PDF 경로 설정 → 해시 검증 → 전체 텍스트 조회 가능
```

### 4.2 Key Interactions

**시나리오 1: 첫 사용**
```
사용자: "OBC에서 계단 너비 요구사항 찾아줘"
Claude: "OBC 9.8.2.1 'Width'에서 관련 내용을 찾았습니다.
        - 페이지: 245
        - 관련 키워드: stair, width, egress

        전체 텍스트를 보시려면 PDF 파일을 연결해주세요:
        set_pdf_path(code='OBC', path='your/path/to/obc.pdf')"
```

**시나리오 2: BYOD 모드**
```
사용자: "내 PDF 연결했어. 9.8.2.1 조항 내용 전체 보여줘"
Claude: [get_section 호출]
        "9.8.2.1. Width
        (1) Except as permitted by Sentences (2) and (3)...
        [전체 조항 텍스트 표시]"
```

### 4.3 Edge Cases

| 상황 | 처리 방법 |
|------|----------|
| PDF 버전 불일치 | Slow Mode로 전환, 경고 메시지 |
| 검색 결과 없음 | 유사 키워드 제안 |
| 잘못된 섹션 ID | 가장 가까운 섹션 제안 |
| PDF 파일 없음 | Map Only 모드로 동작 |

---

## 5. Technical Considerations

### 5.1 Architecture Overview

```
[배포 패키지]
├── maps/              # structure_map.json (좌표 데이터)
├── checksums.json     # PDF 해시 검증용
└── src/mcp_server.py  # MCP 서버

[사용자 로컬]
├── 사용자 PDF        # 합법 취득
└── local.db          # 추출된 텍스트 (SQLite + FTS5)
```

### 5.2 Dependencies

| 의존성 | 용도 | 버전 |
|--------|------|------|
| `mcp` | MCP 서버 SDK | latest |
| `pymupdf` | PDF 텍스트 추출 | 1.26+ |
| `sqlite3` | 로컬 DB | built-in |

### 5.3 Constraints

- **저작권**: 텍스트 직접 배포 불가 → 좌표만 배포
- **PDF 버전**: 공식 PDF와 해시 일치 필요 (Fast Mode)
- **테이블**: Marker 품질 이슈 → Hybrid Pipeline으로 보완

---

## 6. Success Metrics

### 6.1 KPIs

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| **검색 정확도** | > 90% | 관련 결과 비율 |
| **섹션 커버리지** | > 95% | 인덱싱된 섹션 / 전체 섹션 |
| **테이블 품질** | > 95% | 정상 렌더링 테이블 비율 |
| **설정 시간** | < 5분 | 설치 → 첫 검색까지 |
| **검색 응답 시간** | < 1초 | 검색 쿼리 처리 시간 |

### 6.2 Acceptance Criteria

**P0 기능 (Must Have)**
- [ ] `list_codes`가 모든 지원 코드 반환
- [ ] `search_code`가 키워드로 관련 섹션 찾음
- [ ] `get_section`이 섹션 메타데이터 반환
- [ ] Claude Desktop에서 MCP 서버 연결 성공

**P1 기능 (Should Have)**
- [ ] `get_hierarchy`가 상하위 조항 반환
- [ ] `set_pdf_path`로 PDF 연결 시 전체 텍스트 조회 가능
- [ ] PDF 해시 불일치 시 Slow Mode로 자동 전환

**P2 기능 (Nice to Have)**
- [ ] `compare_codes`로 두 코드 간 동일 섹션 비교
- [ ] 검색 결과 관련도 순 정렬

---

## 7. Risks & Mitigations

### 7.1 Known Risks

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| **저작권 이슈** | 낮음 | 높음 | 좌표만 배포, 법률 검토 완료 |
| **Marker 품질** | 중간 | 중간 | Hybrid Pipeline으로 보완 |
| **PDF 버전 다양성** | 높음 | 중간 | 여러 해시 지원 + Slow Mode |
| **사용자 채택 저조** | 중간 | 높음 | 튜토리얼, 데모 영상 제작 |

### 7.2 Mitigation Strategies

**저작권 보호:**
1. 텍스트 절대 배포하지 않음
2. 좌표(사실 정보)만 배포
3. 사용자가 합법적으로 취득한 PDF 사용

**품질 보증:**
1. 6가지 기준으로 테이블 품질 판별
2. pdfplumber로 깨진 테이블 수정
3. 수동 검수 병행

**사용자 경험:**
1. 설치 가이드 상세 제공
2. 데모 영상 제작
3. 예제 쿼리 제공

---

## Appendix

### A. 지원 코드 목록

| Code | Version | Description |
|------|---------|-------------|
| NBC | 2025 | National Building Code |
| NPC | 2025 | National Plumbing Code |
| NFC | 2025 | National Fire Code |
| NECB | 2025 | National Energy Code for Buildings |
| OBC | 2024 | Ontario Building Code |
| BCBC | 2024 | British Columbia Building Code |
| ABC | 2023 | Alberta Building Code |
| QCC | 2020 | Quebec Construction Code |
| QPC | 2020 | Quebec Plumbing Code |
| QSC | 2020 | Quebec Safety Code |
| QECB | 2020 | Quebec Energy Code |
| UG-NBC-P9 | 2020 | User's Guide NBC Part 9 |
| UG-NBC-P4 | 2020 | User's Guide NBC Part 4 |
| UG-NECB | 2020 | User's Guide NECB |

### B. 섹션 ID 체계

```
Part 9       → 9
 └─ Section  → 9.8
     └─ Subsection → 9.8.2
         └─ Article → 9.8.2.1
             └─ Sentence → 9.8.2.1.(1)
                 └─ Clause → 9.8.2.1.(1)(a)
```

### C. 관련 문서

- [01_ARCHITECTURE.md](../../docs/archive/01_ARCHITECTURE.md) - 상세 아키텍처
- [06_HYBRID_PIPELINE.md](../../docs/archive/06_HYBRID_PIPELINE.md) - 하이브리드 파이프라인
- [04_ROADMAP.md](../../docs/archive/04_ROADMAP.md) - 개발 로드맵
