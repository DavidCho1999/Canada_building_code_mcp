# Product Overview: Canadian Building Code MCP

## What is This Product?

Canadian Building Code MCP는 Claude Desktop과 연동되는 MCP(Model Context Protocol) 서버로, 캐나다 건축 코드를 AI를 통해 검색하고 참조할 수 있게 해주는 도구입니다.

## Core Value Proposition

> "Claude에게 캐나다 Building Code를 가르쳐서, 건축 전문가가 자연어로 코드를 검색하고 참조할 수 있게 한다."

## Key Differentiators

### 1. Map & Territory 전략
- 저작권 문제 없이 좌표(coordinates)만 배포
- 실제 텍스트는 사용자의 합법적 PDF에서 추출
- 법적으로 99% 안전

### 2. BYOD (Bring Your Own Document)
- 사용자가 공식 채널에서 다운로드한 PDF 연결
- PDF 해시 검증으로 버전 호환성 확인
- Fast Mode (좌표 기반) vs Slow Mode (패턴 매칭)

### 3. 하이브리드 파이프라인
- Marker의 텍스트 추출 능력 활용
- pdfplumber로 테이블 품질 보완
- 6가지 기준으로 자동 품질 판별

## Target Market

- 캐나다 건축사
- 건축 엔지니어
- 계약자/시공자
- 건축 검사관
- 건축 학생

## Supported Codes

**National (4):** NBC, NFC, NPC, NECB
**Provincial (7):** OBC, BCBC, ABC, QCC×4
**User's Guides (3):** NBC Part 9, Part 4, NECB Guide

## Technology Stack

- Python MCP SDK
- PyMuPDF (텍스트 추출)
- SQLite + FTS5 (검색)
- Marker (PDF 파싱)
- pdfplumber (테이블 추출)
