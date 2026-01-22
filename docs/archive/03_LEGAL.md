# 03. Legal Analysis - 법적 분석

## 핵심 질문

> "좌표만 배포하면 법적 문제가 없는가?"

---

## 저작권법 기본 원칙

### 보호 대상 vs 비보호 대상

| 보호됨 (저작물) | 보호 안 됨 (사실/아이디어) |
|----------------|--------------------------|
| 창작적 표현 | 객관적 사실 |
| 문장, 문단 | 숫자, 좌표 |
| 테이블 데이터 | 페이지 번호 |
| 편집 저작물의 창작적 배열 | 기능적/기술적 구조 |

### Building Code의 특수성

```
Building Code는:
1. 법규 텍스트 = 정부 저작물 (일부 보호)
2. 구조 = 기술적 필요에 의한 배열 (창작성 낮음)
3. 섹션 번호 = 참조 체계 (사실)
```

---

## 좌표 오버레이 방식 분석

### 배포하는 데이터

```json
{
  "id": "9.8.2.1",
  "page": 245,
  "bbox": [50.0, 100.0, 550.0, 300.0]
}
```

### 법적 분석

| 데이터 | 성격 | 저작권 보호 |
|--------|------|-------------|
| `"id": "9.8.2.1"` | 참조 번호 (사실) | ❌ 보호 안 됨 |
| `"page": 245` | 물리적 위치 (사실) | ❌ 보호 안 됨 |
| `"bbox": [50, 100, 550, 300]` | 좌표 (숫자) | ❌ 보호 안 됨 |
| `"type": "article"` | 분류 (사실) | ❌ 보호 안 됨 |

### 법적 논거

#### 1. 사실/아이디어 불보호 원칙

```
저작권법은 "표현"을 보호하지, "사실"이나 "아이디어"를 보호하지 않음.

"9.8.2.1 조항이 245페이지에 있다"는 것은
누구나 PDF를 열어 확인할 수 있는 객관적 사실.

사실의 기록은 저작권 보호 대상이 아님.
```

#### 2. 합병 원칙 (Merger Doctrine)

```
아이디어를 표현하는 방법이 하나밖에 없으면,
그 표현은 아이디어와 "합병"되어 보호받지 못함.

"9.8.2.1이 245페이지에 있다"를 표현하는 방법은
{ "id": "9.8.2.1", "page": 245 } 외에 없음.

따라서 이 표현은 보호받지 못함.
```

#### 3. 기능적 저작물 제한

```
Building Code의 구조(Part → Section → Article)는
기술적/기능적 필요에 의한 것.

창작적 선택의 결과가 아니라 기능적 요구의 결과.
기능적 요소는 저작권 보호가 제한됨.
```

---

## 잠재적 리스크 분석

### 리스크 1: 편집 저작물 주장

```
주장: "전체 구조 맵은 편집 저작물이다"

반론:
- 편집 저작물은 "선택과 배열의 창작성"을 요구
- Building Code 구조는 기술적 필요에 의한 것
- 우리는 그 구조를 "복제"한 게 아니라 "기록"한 것
- 전화번호부 판례 (Feist v. Rural): 사실의 편집은 보호 안 됨
```

### 리스크 2: 파생 저작물 주장

```
주장: "structure_map은 PDF의 파생 저작물이다"

반론:
- 파생 저작물은 원저작물의 "표현"을 변형해야 함
- 우리는 표현(텍스트)을 포함하지 않음
- 좌표는 원저작물의 "위치 정보"일 뿐
- 책의 목차 페이지 번호를 기록하는 것과 같음
```

### 리스크 3: 데이터베이스 권리

```
EU: sui generis 데이터베이스 권리 존재
캐나다/미국: 해당 없음

캐나다 법에서는 데이터베이스 자체에 대한
별도의 권리가 인정되지 않음.
```

---

## 리스크 매트릭스

| 리스크 | 발생 가능성 | 영향도 | 종합 |
|--------|------------|--------|------|
| 저작권 침해 소송 | 🟢 매우 낮음 | 🔴 높음 | 🟢 낮음 |
| 중단 요청 (C&D) | 🟡 낮음 | 🟡 중간 | 🟢 낮음 |
| 법적 방어 성공 | 🟢 매우 높음 | N/A | N/A |

### 종합 평가

```
텍스트 배포: 🔴 확실한 저작권 침해
좌표만 배포: 🟢 99% 안전 (법적 방어 가능)
```

---

## 안전장치

### 1. 면책조항 (Disclaimer)

```markdown
## Legal Notice

This tool provides structural coordinate information only.
No copyrighted content is distributed.

Actual text content is extracted from PDF files that users
must obtain through legitimate means from official sources.

All copyrights belong to their respective owners:
- Ontario Building Code: © King's Printer for Ontario
- National Building Code: © National Research Council of Canada

This tool is for educational and professional reference purposes only.
```

### 2. 사용자 동의

```python
def first_run_agreement():
    print("""
    ============================================
    Canadian Building Code MCP - Legal Agreement
    ============================================

    This tool requires you to provide your own legally
    obtained PDF copy of the building code.

    By continuing, you confirm that:
    1. You have legally obtained the PDF file
    2. You will use this tool for legitimate purposes
    3. You understand that this tool does not provide
       official legal advice

    Do you agree? (yes/no):
    """)
```

### 3. PDF 출처 안내

```markdown
## How to Obtain Official PDFs

### Ontario Building Code
- Request from: https://www.ontario.ca/form/get-2024-building-code-compendium-non-commercial-use
- Free for non-commercial use

### National Building Code
- Download from: https://nrc-publications.canada.ca
- Free electronic access

### BC Building Code
- Available from: BC Laws website
```

---

## 선제적 조치 (권장)

### NRC에 사전 문의

```
To: Codes@nrc-cnrc.gc.ca
Subject: Inquiry about coordinate-based reference tool

Dear Codes Canada Team,

I am developing an educational tool that provides
structural coordinate information for building codes
(page numbers, bounding boxes) without distributing
the actual text content.

Users would need to obtain their own official PDF
copies and the tool would help them navigate the
document more efficiently.

Does this approach require any permission from NRC?

Thank you for your guidance.
```

### 예상 답변

```
가능성 높은 답변들:

1. "텍스트를 배포하지 않으면 허가 필요 없습니다" ✅
2. "공식 답변을 드리기 어렵습니다" (묵인)
3. "법률 자문을 받으세요" (중립)

가능성 낮은 답변:
4. "좌표 배포도 허가가 필요합니다" ⚠️
```

---

## 유사 판례/사례

### 1. Google Books 판결 (미국)

```
Google이 책을 스캔하여 "snippet"만 보여준 것은 fair use.
전체 텍스트가 아닌 일부 정보만 제공하면 허용될 수 있음.
```

### 2. 전화번호부 판례 (Feist v. Rural)

```
전화번호부의 이름+번호 목록은 저작권 보호 안 됨.
사실의 편집은 창작성이 없으면 보호되지 않음.
```

### 3. API 저작권 (Oracle v. Google)

```
API 구조는 fair use로 복제 가능 (최종 판결).
기능적 구조의 복제는 허용될 수 있음.
```

---

## 결론

### 법적 안전성 평가

```
┌─────────────────────────────────────────┐
│                                         │
│   텍스트 배포     ████████████ 🔴 위험  │
│                                         │
│   좌표만 배포     ██ 🟢 안전            │
│                                         │
│   아무것도 안 함  █ 🟢 완전 안전        │
│                                         │
└─────────────────────────────────────────┘
```

### 권장 사항

1. **좌표만 배포** - 99% 안전
2. **면책조항 포함** - 추가 보호
3. **NRC 사전 문의** - 명시적 확인 (선택)
4. **법률 자문** - 100% 확신 필요 시 (비용 발생)

---

## 다음 문서

→ [04_ROADMAP.md](./04_ROADMAP.md) - 개발 로드맵
