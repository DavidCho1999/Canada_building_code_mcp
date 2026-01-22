# PRD: Canadian Building Code MCP Server

> Version: 1.0
> Date: 2026-01-21
> Status: Draft

---

## 1. Overview

### 1.1 Problem Statement

Canadian construction professionals (architects, engineers, contractors, inspectors) need to reference **14+ Building Codes** during projects. Current situation:

- **Inefficient Search**: Manually navigating 1,000+ page PDFs
- **Version Confusion**: Difficulty identifying National vs Provincial code differences
- **Table Accessibility**: Hard to find complex table data (Fire Separation, Egress, etc.)
- **No AI Utilization**: Cannot directly reference Building Code in AI tools like Claude

### 1.2 Target Users

| User Type | Primary Needs | Usage Frequency |
|-----------|---------------|-----------------|
| **Architects** | Code compliance verification during design | Daily |
| **Building Engineers** | Structural/fire/energy requirements | Daily |
| **Contractors** | On-site work standards | Weekly |
| **Building Inspectors** | Compliance review | Daily |
| **Architecture Students** | Learning and projects | Weekly |

**Primary Persona: Sarah - Canadian Architect**
- 10 years experience, Ontario-based
- Mainly residential projects
- Has Claude Desktop experience
- Primarily references OBC Part 9 (small buildings)

### 1.3 Product Vision

> "Teach Claude about Canadian Building Codes so construction professionals can search and reference codes in natural language."

**Core Values:**
1. **Accessibility**: Easy search of complex Building Codes
2. **Accuracy**: Direct reference to official code text (hallucination prevention)
3. **Legal Safety**: "Coordinate overlay" approach with no copyright issues

---

## 2. User Needs & JTBD

### 2.1 Jobs to be Done

**Job 1: Find Specific Requirements**
> "I want to know the Fire Separation requirements for the residential building I'm designing"

- Trigger: During design review
- Current Method: PDF search or table of contents navigation
- Desired Outcome: Immediate access to relevant articles and tables

**Job 2: Compare Codes**
> "I want to know the differences between OBC and NBC"

- Trigger: Projects in multiple provinces
- Current Method: Open two PDFs and manually compare
- Desired Outcome: Automatic display of differences between same sections

**Job 3: Understand Context**
> "I want to know why this article exists and what related articles apply"

- Trigger: Code interpretation needed
- Current Method: Reference User's Guide, consult experts
- Desired Outcome: Immediate navigation of parent/child and related articles

### 2.2 Pain Points

| Pain Point | Severity | Current Solution |
|------------|----------|------------------|
| Inaccurate PDF search results | High | Manual navigation |
| Cannot copy table data | High | Manual typing |
| Difficulty tracking code updates | Medium | Newsletter subscription |
| AI hallucination (incorrect code citations) | High | Manual verification required |

### 2.3 Desired Outcomes

1. **Reduced Search Time**: Average 5 min → 30 sec
2. **Improved Accuracy**: Eliminate AI hallucination (direct official text reference)
3. **Reduced Learning Curve**: Easy code structure navigation
4. **Productivity Improvement**: Automated code reference tasks

---

## 3. Feature Specifications

### 3.1 Core Features

| # | Feature | Priority | Description |
|---|---------|----------|-------------|
| 1 | `list_codes` | P0 | List supported codes |
| 2 | `search_code` | P0 | Keyword search |
| 3 | `get_section` | P0 | Lookup by section ID |
| 4 | `get_hierarchy` | P1 | Parent/child article navigation |
| 5 | `set_pdf_path` | P1 | Connect user's PDF (BYOD) |
| 6 | `compare_codes` | P2 | Compare between codes |

### 3.2 Feature Details

#### 3.2.1 `list_codes` - List Codes

**Input:** None
**Output:** Supported code list (code name, version, status)

```
User: "What codes can I search?"
Claude: [calls list_codes]
Response: "Currently supporting NBC 2025, OBC 2024, BCBC 2024... 14 codes total"
```

#### 3.2.2 `search_code` - Keyword Search

**Input:**
- `query`: Search term (required)
- `code`: Code specification (optional, default: all)
- `limit`: Result count (optional, default: 10)

**Output:** Matching section list (ID, title, page, relevance)

```
User: "Find garage fire separation requirements"
Claude: [search_code(query="fire separation garage", code="OBC")]
Response: "Found relevant content in OBC 9.10.14.1..."
```

#### 3.2.3 `get_section` - Section Lookup

**Input:**
- `id`: Section ID (required, e.g., "9.10.14.1")
- `code`: Code specification (required)

**Output:**
- Mode A (Map Only): Title, page number, keywords
- Mode B (BYOD): Above + actual text content

```
User: "Show me article 9.10.14.1"
Claude: [get_section(id="9.10.14.1", code="OBC")]
Response: "[Article content...]"
```

#### 3.2.4 `get_hierarchy` - Hierarchy Navigation

**Input:**
- `id`: Section ID (required)
- `code`: Code specification (required)

**Output:** Parent section, child sections, sibling sections

```
User: "Show me all articles related to 9.10.14"
Claude: [get_hierarchy(id="9.10.14", code="OBC")]
Response: "Parent: Section 9.10 Fire Protection
         Children: 9.10.14.1, 9.10.14.2, 9.10.14.3..."
```

#### 3.2.5 `set_pdf_path` - PDF Connection (BYOD)

**Input:**
- `code`: Code specification (required)
- `path`: PDF file path (required)

**Output:** Connection success/failure, version verification result

```
User: "Connect my OBC PDF file"
Claude: [set_pdf_path(code="OBC", path="C:/codes/OBC2024.pdf")]
Response: "OBC 2024 PDF connected. You can now view full text."
```

### 3.3 Out of Scope (v1.0)

- Code interpretation and consulting (requires AI judgment)
- Drawing analysis integration
- Code change notification feature
- Multi-language support (other than English)
- US Code (ICC) support

---

## 4. User Experience

### 4.1 User Flow

```
[1. Installation]
└─> pip install → MCP server setup → Claude Desktop connection

[2. Basic Usage (Map Only)]
└─> Keyword search → Check section ID → Reference PDF directly with page number

[3. Advanced Usage (BYOD)]
└─> Set PDF path → Hash verification → Full text lookup available
```

### 4.2 Key Interactions

**Scenario 1: First Use**
```
User: "Find stair width requirements in OBC"
Claude: "Found relevant content in OBC 9.8.2.1 'Width'.
        - Page: 245
        - Related keywords: stair, width, egress

        To view full text, please connect your PDF file:
        set_pdf_path(code='OBC', path='your/path/to/obc.pdf')"
```

**Scenario 2: BYOD Mode**
```
User: "I've connected my PDF. Show me the full content of 9.8.2.1"
Claude: [calls get_section]
        "9.8.2.1. Width
        (1) Except as permitted by Sentences (2) and (3)...
        [Full article text displayed]"
```

### 4.3 Edge Cases

| Situation | Handling |
|-----------|----------|
| PDF version mismatch | Switch to Slow Mode, warning message |
| No search results | Suggest similar keywords |
| Invalid section ID | Suggest closest section |
| No PDF file | Operate in Map Only mode |

---

## 5. Technical Considerations

### 5.1 Architecture Overview

```
[Distribution Package]
├── maps/              # structure_map.json (coordinate data)
├── checksums.json     # PDF hash verification
└── src/mcp_server.py  # MCP server

[User Local]
├── User PDF          # Legally obtained
└── local.db          # Extracted text (SQLite + FTS5)
```

### 5.2 Dependencies

| Dependency | Purpose | Version |
|------------|---------|---------|
| `mcp` | MCP Server SDK | latest |
| `pymupdf` | PDF text extraction | 1.26+ |
| `sqlite3` | Local DB | built-in |

### 5.3 Constraints

- **Copyright**: Cannot distribute text directly → Distribute coordinates only
- **PDF Version**: Must match official PDF hash (Fast Mode)
- **Tables**: Marker quality issues → Supplement with Hybrid Pipeline

---

## 6. Success Metrics

### 6.1 KPIs

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Search Accuracy** | > 90% | Relevant results ratio |
| **Section Coverage** | > 95% | Indexed sections / Total sections |
| **Table Quality** | > 95% | Properly rendered tables ratio |
| **Setup Time** | < 5 min | Installation → First search |
| **Search Response Time** | < 1 sec | Search query processing time |

### 6.2 Acceptance Criteria

**P0 Features (Must Have)**
- [ ] `list_codes` returns all supported codes
- [ ] `search_code` finds relevant sections by keyword
- [ ] `get_section` returns section metadata
- [ ] MCP server connects successfully to Claude Desktop

**P1 Features (Should Have)**
- [ ] `get_hierarchy` returns parent/child articles
- [ ] Full text lookup available when PDF connected via `set_pdf_path`
- [ ] Auto-switch to Slow Mode on PDF hash mismatch

**P2 Features (Nice to Have)**
- [ ] `compare_codes` compares same sections between two codes
- [ ] Search results sorted by relevance

---

## 7. Risks & Mitigations

### 7.1 Known Risks

| Risk | Probability | Impact | Response |
|------|-------------|--------|----------|
| **Copyright Issues** | Low | High | Distribute coordinates only, legal review completed |
| **Marker Quality** | Medium | Medium | Supplement with Hybrid Pipeline |
| **PDF Version Diversity** | High | Medium | Support multiple hashes + Slow Mode |
| **Low User Adoption** | Medium | High | Create tutorials, demo videos |

### 7.2 Mitigation Strategies

**Copyright Protection:**
1. Never distribute text
2. Distribute only coordinates (factual information)
3. Users use legally obtained PDFs

**Quality Assurance:**
1. 6 criteria for table quality assessment
2. Fix broken tables with pdfplumber
3. Parallel manual review

**User Experience:**
1. Detailed installation guide
2. Demo video production
3. Example queries provided

---

## Appendix

### A. Supported Codes List

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

### B. Section ID System

```
Part 9       → 9
 └─ Section  → 9.8
     └─ Subsection → 9.8.2
         └─ Article → 9.8.2.1
             └─ Sentence → 9.8.2.1.(1)
                 └─ Clause → 9.8.2.1.(1)(a)
```

### C. Related Documents

- [01_ARCHITECTURE.md](../../docs/archive/01_ARCHITECTURE.md) - Detailed Architecture
- [06_HYBRID_PIPELINE.md](../../docs/archive/06_HYBRID_PIPELINE.md) - Hybrid Pipeline
- [04_ROADMAP.md](../../docs/archive/04_ROADMAP.md) - Development Roadmap
