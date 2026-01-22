# 05. User Guide - 사용자 가이드

## 개요

Canadian Building Code MCP는 Claude가 캐나다 건축 코드를 직접 검색하고 참조할 수 있게 해주는 도구입니다.

**특징:**
- 로컬에서 실행 (데이터 외부 전송 없음)
- 사용자의 합법적 PDF에서 직접 추출
- 빠른 검색 (< 1초)

---

## 설치 요구사항

### 시스템 요구사항

```
- Python 3.10 이상
- 저장 공간: 500MB (PDF + DB)
- OS: Windows, macOS, Linux
```

### 필수 소프트웨어

```bash
# Python 패키지
pip install mcp pymupdf

# 선택: 개발/테스트용
pip install pytest
```

---

## 빠른 시작

### 1단계: MCP 다운로드

```bash
# GitHub에서 클론
git clone https://github.com/username/canadian-building-code-mcp.git
cd canadian-building-code-mcp
```

### 2단계: 의존성 설치

```bash
pip install -r requirements.txt
```

### 3단계: PDF 준비

**Ontario Building Code:**
1. https://www.ontario.ca/form/get-2024-building-code-compendium-non-commercial-use 방문
2. 양식 작성 후 다운로드 링크 수신
3. PDF를 `pdfs/` 폴더에 저장

**National Building Code:**
1. https://nrc-publications.canada.ca 방문
2. "National Building Code of Canada" 검색
3. 무료 전자 버전 다운로드
4. PDF를 `pdfs/` 폴더에 저장

### 4단계: 초기 설정

```bash
# 초기 설정 실행 (PDF에서 텍스트 추출 및 DB 생성)
python setup.py

# 예상 출력:
# ✓ PDF 해시 검증 완료 (OBC 2024)
# ✓ Fast Mode 사용 가능
# ✓ 텍스트 추출 중... (약 30초)
# ✓ 데이터베이스 생성 완료
# ✓ 검색 인덱스 생성 완료
#
# 설정 완료! Claude Desktop에 연결할 준비가 되었습니다.
```

### 5단계: Claude Desktop 연결

`~/.config/claude/claude_desktop_config.json` (Mac/Linux) 또는
`%APPDATA%\Claude\claude_desktop_config.json` (Windows) 수정:

```json
{
  "mcpServers": {
    "building-code": {
      "command": "python",
      "args": ["/path/to/canadian-building-code-mcp/src/server.py"],
      "env": {
        "PDF_PATH": "/path/to/pdfs"
      }
    }
  }
}
```

### 6단계: 테스트

Claude Desktop을 재시작하고 다음을 물어보세요:

```
"OBC 9.8.2.1 계단 너비 요구사항을 알려줘"
```

---

## 사용 예시

### 섹션 조회

```
사용자: "9.8.2.1 내용 보여줘"
Claude: [get_section 도구 호출]

응답:
9.8.2.1. Width
(1) Except as permitted by Sentences (2) to (5),
the width of stairs shall be not less than 860 mm.
...
```

### 키워드 검색

```
사용자: "fire separation 관련 조항 찾아줘"
Claude: [search_code 도구 호출]

응답:
검색 결과 (15건):
1. 9.10.9.6 - Fire Separations in Houses
2. 9.10.9.7 - Required Fire Separations
3. 9.10.9.8 - Fire Separation of Service Rooms
...
```

### 테이블 조회

```
사용자: "Table 9.10.14.4 내용은?"
Claude: [get_table 도구 호출]

응답:
Table 9.10.14.4
Maximum Aggregate Area of Unprotected Openings

| Limiting Distance | Residential | Other |
|-------------------|-------------|-------|
| Less than 1.2 m   | N.P.        | N.P.  |
| 1.2 m             | 0.2         | 0.1   |
...
```

### 다중 코드 비교 (NBC 포함 시)

```
사용자: "OBC와 NBC의 9.8.2.1 차이점은?"
Claude: [compare_codes 도구 호출]

응답:
비교: 9.8.2.1 계단 너비

OBC 2024:
- 최소 너비: 860 mm
- 예외: 860 mm 미만 허용 조건 5가지

NBC 2020:
- 최소 너비: 860 mm
- 예외 조건 동일

차이점: 실질적 차이 없음
```

---

## 문제 해결

### PDF 해시 불일치

```
⚠️ PDF 해시 불일치
예상: a1b2c3d4...
실제: f6e5d4c3...

Slow Mode로 전환합니다. (시간이 더 소요됩니다)
```

**원인:** 다른 버전의 PDF를 사용 중

**해결:**
1. 공식 소스에서 최신 PDF 다운로드
2. 또는 Slow Mode 사용 (정확도 95%)

### 섹션을 찾을 수 없음

```
❌ 섹션 '9.99.99.99'를 찾을 수 없습니다
```

**원인:** 존재하지 않는 섹션 ID

**해결:**
1. 섹션 ID 형식 확인 (예: 9.8.2.1)
2. 검색 기능으로 관련 섹션 찾기

### MCP 서버 연결 실패

```
❌ MCP 서버에 연결할 수 없습니다
```

**원인:** 설정 파일 오류 또는 Python 경로 문제

**해결:**
1. `claude_desktop_config.json` 경로 확인
2. Python 절대 경로 사용
3. Claude Desktop 재시작

---

## 고급 설정

### 여러 코드 동시 사용

```json
{
  "mcpServers": {
    "building-code": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "CODES": "OBC,NBC,BCBC",
        "PDF_PATH": "/path/to/pdfs"
      }
    }
  }
}
```

### 캐시 설정

```python
# config.py
CACHE_SIZE = 1000      # 캐시할 섹션 수
CACHE_TTL = 3600       # 캐시 유효 시간 (초)
```

### 로깅 설정

```python
# config.py
LOG_LEVEL = "INFO"     # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "mcp.log"   # 로그 파일 경로
```

---

## CLI 명령어

### 상태 확인

```bash
python cli.py status

# 출력:
# Building Code MCP Status
# ========================
# OBC 2024: ✓ 설정됨 (Fast Mode)
# NBC 2020: ✓ 설정됨 (Fast Mode)
# BCBC 2024: ✗ PDF 없음
#
# 데이터베이스: 15,234 섹션
# 마지막 업데이트: 2026-01-21
```

### 데이터베이스 재생성

```bash
python cli.py rebuild --code OBC

# PDF가 업데이트되었을 때 사용
```

### 검색 테스트

```bash
python cli.py search "fire separation"

# MCP 서버 없이 직접 검색 테스트
```

---

## FAQ

### Q: 인터넷 연결이 필요한가요?

**A:** 아니요. 초기 설치 후에는 모든 데이터가 로컬에 저장됩니다.
Claude Desktop과의 통신도 로컬에서 이루어집니다.

### Q: PDF를 배포해도 되나요?

**A:** 아니요. PDF는 각 사용자가 공식 소스에서 직접 다운로드해야 합니다.
이 MCP는 좌표 정보만 배포하며, 실제 텍스트는 사용자의 PDF에서 추출됩니다.

### Q: 다른 국가의 Building Code도 지원하나요?

**A:** 현재는 캐나다 코드만 지원합니다.
동일한 아키텍처로 다른 코드도 추가할 수 있습니다.

### Q: 업데이트는 어떻게 하나요?

**A:**
```bash
git pull origin main
pip install -r requirements.txt --upgrade
python setup.py --update
```

### Q: 오프라인에서 작동하나요?

**A:** 네, 완전히 오프라인으로 작동합니다.
Claude Desktop은 로컬 MCP 서버와 통신합니다.

---

## 지원 및 기여

### 버그 신고

GitHub Issues에서 버그를 신고해주세요:
https://github.com/username/canadian-building-code-mcp/issues

### 기여

1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

### 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 법적 고지

```
이 도구는 교육 및 전문가 참조 목적으로만 사용해야 합니다.

실제 건축 프로젝트에서는 반드시 공식 Building Code 문서를
참조하고, 관할 기관의 검토를 받으세요.

모든 저작권은 원 저작권자에게 있습니다:
- Ontario Building Code: © King's Printer for Ontario
- National Building Code: © National Research Council of Canada

이 도구는 좌표 정보만 배포하며,
실제 콘텐츠는 사용자가 합법적으로 취득한 PDF에서 추출됩니다.
```

---

## 다음 단계

1. **피드백 제공**: 사용 경험을 공유해주세요
2. **기여**: 새로운 코드 지원을 추가해주세요
3. **커뮤니티**: Discord/Forum에서 토론에 참여하세요
