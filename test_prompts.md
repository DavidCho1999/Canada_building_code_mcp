# MCP Server Test Prompts

이 파일은 Building Code MCP 서버를 테스트하기 위한 prompt 모음입니다.

## ✅ 정상 작동해야 하는 케이스

### 1. 기본 검색 (search_code)
```
NBC 2025에서 mass timber 관련 섹션을 찾아줘
```
**예상 결과**: Section 3.2.2.55, 3.2.2.56 등 mass timber 관련 섹션들 반환

### 2. 섹션 조회 (get_section)
```
NBC 2025의 Section 3.2.2.55를 보여줘
```
**예상 결과**: 섹션 정보 + 페이지 번호 + 좌표 반환

### 3. 계층 구조 탐색 (get_hierarchy)
```
NBC 2025의 Section 3.2.2.55의 하위 섹션들을 보여줘
```
**예상 결과**: 3.2.2.55.1, 3.2.2.55.2 등 하위 섹션들 반환

### 4. 지역별 코드 확인 (get_applicable_code)
```
Ontario에서 적용되는 building code가 뭐야?
```
**예상 결과**: OBC (Ontario Building Code) 반환

### 5. 코드 목록 조회 (list_codes)
```
사용 가능한 모든 building code 목록을 보여줘
```
**예상 결과**: 16개 코드 목록 (NBC, NFC, OBC, BCBC 등)

---

## ❌ 에러가 발생할 수 있는 케이스

### 1. 존재하지 않는 섹션 조회
```
NBC 2025의 Section 9.99.99.99를 보여줘
```
**예상 에러**: "Section not found: 9.99.99.99"

### 2. 존재하지 않는 코드 검색
```
Manitoba Building Code에서 fire rating을 검색해줘
```
**예상 에러**: "Code not found: manitoba" 또는 지원하지 않는 코드 안내

### 3. 잘못된 섹션 형식
```
NBC 2025의 Section ABC-123을 보여줘
```
**예상 에러**: Invalid section format 또는 섹션을 찾을 수 없음

### 4. BYOD 모드 없이 전체 텍스트 요청
```
NBC 2025의 Section 3.2.2.55의 전체 텍스트를 보여줘
```
**예상 동작**:
- Map-Only 모드: 페이지 번호 + 좌표만 반환
- "PDF를 직접 참조하세요" 안내

### 5. 빈 검색어
```
NBC 2025에서 검색해줘 (키워드 없음)
```
**예상 에러**: "No search keywords provided" 또는 빈 결과

### 6. 특수문자/이상한 입력
```
NBC 2025의 Section '; DROP TABLE sections; --를 보여줘
```
**예상 동작**: SQL injection 방지되어야 함, 섹션을 찾을 수 없음 반환

### 7. 너무 일반적인 검색어
```
NBC 2025에서 "building"을 검색해줘
```
**예상 동작**: 결과가 너무 많거나, TF-IDF로 필터링되어 관련성 낮은 결과 제외

### 8. 존재하지 않는 테이블 ID
```
Table ID table_99999를 보여줘
```
**예상 에러**: "Table not found: table_99999"

### 9. 잘못된 페이지 범위 (get_pages)
```
NBC 2025의 1000-2000 페이지를 보여줘
```
**예상 에러**: "Page range out of bounds" 또는 PDF가 그렇게 길지 않음

### 10. 혼합된 코드 요청
```
NBC 2025과 OBC를 동시에 검색해줘
```
**예상 동작**: 각 코드를 별도로 처리하거나, 하나의 코드만 선택하도록 안내

---

## 🔍 Edge Case 테스트

### 1. 유사 섹션 번호
```
NBC 2025의 Section 3.2.2.5와 3.2.2.55는 다른 섹션이야?
```
**예상 동작**: 두 개의 서로 다른 섹션 반환

### 2. 대소문자 구분
```
nbc 2025에서 FIRE RATING을 검색해줘
```
**예상 동작**: 대소문자 무관하게 검색되어야 함

### 3. 오타 처리
```
NBC 2025에서 "seperation"을 검색해줘 (separation 오타)
```
**예상 동작**:
- 정확한 매칭 없으면 빈 결과
- 또는 "Did you mean 'separation'?" 제안 (구현되어 있다면)

### 4. 한글 검색
```
NBC 2025에서 "화재 등급"을 검색해줘
```
**예상 동작**: 한글은 키워드에 없으므로 빈 결과

### 5. 부분 섹션 번호
```
NBC 2025의 Section 3.2를 보여줘
```
**예상 동작**: Division/Subsection 정보 반환

---

## 🧪 성능 테스트

### 1. 여러 검색어
```
NBC 2025에서 "fire rating separation residential commercial sprinkler exit"를 검색해줘
```
**예상 동작**: TF-IDF 랭킹으로 가장 관련성 높은 섹션들 반환

### 2. 모든 코드에서 검색
```
모든 코드에서 "mass timber"를 검색해줘
```
**예상 동작**: 16개 코드를 순회하며 검색 (시간 소요)

---

## 📝 테스트 방법

### Option 1: Claude Desktop에서 직접 테스트
1. Claude Desktop 실행
2. MCP 서버 연결 확인
3. 위 prompt들을 하나씩 입력
4. 결과 확인

### Option 2: Python으로 직접 테스트
```bash
# MCP 서버 실행
python src/mcp_server.py

# 별도 터미널에서 MCP Inspector 사용
npx @modelcontextprotocol/inspector python src/mcp_server.py
```

### Option 3: cURL로 툴 직접 호출 (구현되어 있다면)
```bash
# 예시 (실제 MCP는 JSON-RPC 프로토콜 사용)
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "search_code",
      "arguments": {
        "code": "nbc",
        "keywords": "mass timber"
      }
    }
  }'
```

---

## ✅ 체크리스트

테스트할 때 다음 항목들을 확인하세요:

- [ ] 정상 케이스가 예상대로 작동하는가?
- [ ] 에러 케이스에서 적절한 에러 메시지가 나오는가?
- [ ] 에러가 발생해도 서버가 죽지 않는가?
- [ ] SQL injection, XSS 등 보안 취약점이 없는가?
- [ ] 빈 입력, null, undefined 처리가 되는가?
- [ ] 성능이 적절한가? (검색 시간 <1초)
- [ ] 메모리 누수가 없는가?
- [ ] 여러 요청을 연속으로 보내도 문제없는가?

---

## 🐛 발견된 버그 기록

이곳에 테스트하면서 발견한 버그를 기록하세요:

```
날짜: YYYY-MM-DD
Prompt: "..."
예상 결과: ...
실제 결과: ...
에러 메시지: ...
재현 방법: ...
```
