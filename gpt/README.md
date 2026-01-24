# GPT App Files

ChatGPT GPTs 앱용 파일들

## 파일 구조

```
gpt/
├── README.md                    # 이 파일
├── GPT_INSTRUCTIONS_v2.6.md     # 최신! (Thorough + Tables)
├── GPT_INSTRUCTIONS_v2.5.md     # 이전 버전
├── GPT_INSTRUCTIONS_v2.4.md     # 이전 버전
├── GPT_SYSTEM_PROMPT.md         # 상세 문서 (참고용)
└── extractor.py                 # Python 헬퍼 (v2.6 - table 추출!)
```

## v2.6 설정 (최신 - Thorough + Tables)

### 1. Knowledge 업로드 파일
```
extractor.py          # Python 헬퍼 (필수!)
maps/OBC_Vol1.json
maps/OBC_Vol2.json
maps/NBC2025.json
... (필요한 JSON 파일들)
```

### 2. GPT 설정 순서
1. ChatGPT → Explore GPTs → Create
2. Configure 탭
3. Name: `Canadian Building Code Navigator`
4. Knowledge: `extractor.py` + JSON 파일들 업로드 (**v2.6 extractor.py 재업로드 필수!**)
5. Code Interpreter: ✅ 체크
6. Instructions: `GPT_INSTRUCTIONS_v2.6.md` 내용 복붙
7. Save → Anyone with link

## 버전별 차이

| 버전 | Time Budget | Search | Tables | 속도 | 정확도 |
|------|-------------|--------|--------|------|--------|
| v2.0-2.1 | 없음 | 제한없음 | ❌ | 느림 | 에러 잦음 |
| v2.2-2.3 | 없음 | 제한없음 | ❌ | 보통 | 높음 |
| v2.4 | 없음 | 제한없음 | ❌ | 3분+ | 보통 |
| v2.5 | 90초 | 1회 | ❌ | 56초 | 높음 (일부 놓침) |
| **v2.6** | **120초** | **2회** | **✅** | **1-2분** | **매우 높음** |

## v2.6 핵심 개선 (최신)

### 1. Time Budget 완화 + 2-Phase Search

**문제점 (v2.5):**
- 90초 Time Budget이 너무 촉박 → 정확한 검색 못 함
- 1회 검색 제한 → 중요한 섹션 놓침 (예: W360x41 steel section)

**해결책:**
- Time Budget: 90초 → **120초 (2분)**
- **2-Phase Search 전략**:
  - Phase 1: 구체적 키워드 검색
  - Phase 2: 결과 부족하면 broader 키워드로 재검색
  - "Better 2 min + accurate than 1 min + missing info"

```python
# Phase 1: Specific
results = search_json(data, "foundation column design")[:4]

# Phase 2: If < 3 good results
if len(results) < 3:
    results2 = search_json(data, "structural Part 4")[:4]
    results = results + results2
```

### 2. 테이블 데이터 지원

**Why:** AEC 전문가들이 테이블 데이터를 자주 필요로 함
- Live load tables, fire ratings, span tables, material properties

**구현:**
```python
# Extract table from JSON (fast!)
from extractor import extract_table

table = extract_table(data, "4.1.5.3")
print(table["markdown"])  # Formatted table

# Batch tables
from extractor import extract_tables_batch
tables = extract_tables_batch(data, ["4.1.5.3", "9.10.14.4"])
```

**Output 예시:**
```
**NBC Table 4.1.5.3** - Live Loads on Floors (p.452)

| Load Type | Residential | Office | Storage |
|-----------|-------------|--------|---------|
| Uniform   | 1.9 kPa     | 2.4 kPa | 4.8 kPa |

Source: JSON (pre-indexed)
```

**예상 효과:**
- 속도: 56초 (v2.5 간단) → 1-2분 (v2.6 복잡)
- 정확도: 높음 → **매우 높음** (놓치는 섹션 감소)
- 테이블: ❌ → ✅ (1,200+ 테이블 지원)

## 테스트

```
질문 1 (간단 - baseline):
"What is the guard height for stairs in OBC?"
→ 60초 이내, 섹션 ID + 페이지 + PDF 인용

질문 2 (복잡 - time budget test):
"New Brunswick 20층 residential foundation, column sizing 기준?"
→ 120초 이내, 4-6개 섹션 + PDF 인용
→ 2-phase search 작동 확인

질문 3 (follow-up - context retention):
"column sizing w 360x41 사용가능?"
→ 60초 이내
→ "W360x41 not standard, suggest W360x39/44" 검증 확인
→ 이전 답변 context 재사용

질문 4 (테이블 - new feature):
"Show me NBC live load table for residential buildings"
→ 60초 이내
→ Table 4.1.5.3 markdown 표시
→ Source: JSON 표시

질문 5 (multi-table - batch test):
"Compare fire resistance ratings for different construction types"
→ 90초 이내
→ 2-3개 테이블 markdown
→ extract_tables_batch() 사용 확인

확인 사항:
✅ 2-phase search 작동 (필요시)
✅ batch 추출 사용 (extract_sections_batch / extract_tables_batch)
✅ > "..." 형식 인용
✅ 테이블 markdown 표시
✅ 마지막 후속 질문 유도
```

## 참고

- 최신 Instructions: `GPT_INSTRUCTIONS_v2.6.md`
- 상세 문서: `GPT_SYSTEM_PROMPT.md`
- 버전 히스토리: v2.0 (bbox) → v2.3 (Section ID) → v2.5 (Batch) → v2.6 (Thorough + Tables)
- 테이블 인프라: 1,200+ 테이블 indexed (NBC, OBC 등 전체 코드)
