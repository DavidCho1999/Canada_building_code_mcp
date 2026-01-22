# Feature: Building Code MCP Server v1.0

## Feature Summary

캐나다 Building Code를 Claude Desktop에서 검색하고 참조할 수 있는 MCP 서버 구현.

## Problem Being Solved

건축 전문가들이 1,000페이지 이상의 Building Code PDF를 수동으로 탐색해야 하는 비효율성 해결.

## Proposed Solution

### Core MCP Tools

1. **list_codes**: 지원 코드 목록 조회
2. **search_code**: 키워드 검색
3. **get_section**: 섹션 ID로 상세 조회
4. **get_hierarchy**: 상하위 조항 탐색
5. **set_pdf_path**: 사용자 PDF 연결

### Operation Modes

| Mode | 조건 | 기능 |
|------|------|------|
| Map Only | PDF 없음 | 메타데이터만 (ID, 페이지, 키워드) |
| BYOD Fast | PDF 해시 일치 | 좌표 기반 전체 텍스트 추출 |
| BYOD Slow | PDF 해시 불일치 | 패턴 매칭 텍스트 추출 |

## User Stories

1. As a 건축사, I want to 자연어로 코드를 검색 so that 관련 조항을 빠르게 찾을 수 있다.
2. As a 엔지니어, I want to 섹션 ID로 직접 조회 so that 정확한 조항 내용을 확인할 수 있다.
3. As a 검사관, I want to 여러 코드를 비교 so that 준수 여부를 검토할 수 있다.

## Success Criteria

- 검색 정확도 > 90%
- 섹션 커버리지 > 95%
- 설정 시간 < 5분
- 검색 응답 시간 < 1초
