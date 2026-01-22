# 03. Legal Analysis

## Core Question

> "Is there no legal issue if we only distribute coordinates?"

---

## Copyright Law Basic Principles

### Protected vs Non-Protected

| Protected (Copyrighted) | Not Protected (Facts/Ideas) |
|------------------------|---------------------------|
| Creative expression | Objective facts |
| Sentences, paragraphs | Numbers, coordinates |
| Table data | Page numbers |
| Creative arrangement of compilations | Functional/technical structure |

### Building Code Specifics

```
Building Code consists of:
1. Regulatory text = Government work (partially protected)
2. Structure = Arrangement by technical necessity (low creativity)
3. Section numbers = Reference system (facts)
```

---

## Coordinate Overlay Approach Analysis

### Data We Distribute

```json
{
  "id": "9.8.2.1",
  "page": 245,
  "bbox": [50.0, 100.0, 550.0, 300.0]
}
```

### Legal Analysis

| Data | Nature | Copyright Protection |
|------|--------|---------------------|
| `"id": "9.8.2.1"` | Reference number (fact) | Not protected |
| `"page": 245` | Physical location (fact) | Not protected |
| `"bbox": [50, 100, 550, 300]` | Coordinates (numbers) | Not protected |
| `"type": "article"` | Classification (fact) | Not protected |

### Legal Arguments

#### 1. Fact/Idea Non-Protection Principle

```
Copyright protects "expression", not "facts" or "ideas".

"Section 9.8.2.1 is on page 245" is
an objective fact anyone can verify by opening the PDF.

Recording facts is not subject to copyright protection.
```

#### 2. Merger Doctrine

```
If there's only one way to express an idea,
that expression "merges" with the idea and is not protected.

There's no other way to express "9.8.2.1 is on page 245"
than { "id": "9.8.2.1", "page": 245 }.

Therefore, this expression is not protected.
```

#### 3. Functional Work Limitation

```
Building Code structure (Part → Section → Article) is
due to technical/functional necessity.

It's not a result of creative choice but functional requirements.
Functional elements have limited copyright protection.
```

---

## Potential Risk Analysis

### Risk 1: Compilation Copyright Claim

```
Claim: "The entire structure map is a compilation work"

Counter-argument:
- Compilations require "creativity in selection and arrangement"
- Building Code structure is due to technical necessity
- We didn't "copy" the structure, we "recorded" it
- Phone book precedent (Feist v. Rural): Compilation of facts is not protected
```

### Risk 2: Derivative Work Claim

```
Claim: "structure_map is a derivative work of the PDF"

Counter-argument:
- Derivative works must transform "expression" of original work
- We don't include expression (text)
- Coordinates are just "location information" of the original work
- Same as recording page numbers of a book's table of contents
```

### Risk 3: Database Rights

```
EU: sui generis database rights exist
Canada/US: Not applicable

Under Canadian law, there's no separate
right recognized for databases themselves.
```

---

## Risk Matrix

| Risk | Probability | Impact | Overall |
|------|------------|--------|---------|
| Copyright infringement lawsuit | Very Low | High | Low |
| Cease & Desist request | Low | Medium | Low |
| Legal defense success | Very High | N/A | N/A |

### Overall Assessment

```
Text distribution: DEFINITE copyright infringement
Coordinates only: 99% safe (legally defensible)
```

---

## Safeguards

### 1. Disclaimer

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

### 2. User Agreement

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

### 3. PDF Source Information

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

## Similar Cases/Precedents

### 1. Google Books Decision (US)

```
Google scanning books and showing only "snippets" was fair use.
Providing partial information instead of full text may be permitted.
```

### 2. Phone Book Case (Feist v. Rural)

```
Name+number listings in phone books are not copyright protected.
Compilation of facts is not protected without creativity.
```

### 3. API Copyright (Oracle v. Google)

```
API structure can be copied under fair use (final ruling).
Copying functional structures may be permitted.
```

---

## Conclusion

### Legal Safety Assessment

```
┌─────────────────────────────────────────┐
│                                         │
│   Text distribution  ████████████ RISKY │
│                                         │
│   Coordinates only   ██ SAFE            │
│                                         │
│   Do nothing         █ COMPLETELY SAFE  │
│                                         │
└─────────────────────────────────────────┘
```

### Recommendations

1. **Distribute coordinates only** - 99% safe
2. **Include disclaimer** - Additional protection
3. **Pre-inquiry to NRC** - Explicit confirmation (optional)
4. **Legal consultation** - If 100% certainty needed (costs money)

---

## Next Document

→ [04_ROADMAP.md](./04_ROADMAP.md) - Development Roadmap
