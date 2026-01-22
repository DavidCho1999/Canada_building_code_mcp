# 04. Roadmap - Development Roadmap

## Overall Timeline

```
Phase 0: Preparation ─────────────┐
                                  │
Phase 1: Marker Batch ────────────┼── 1 day (6~12 hours runtime)
                                  │
Phase 2: Hybrid Pipeline ─────────┼── 1 day
                                  │
Phase 3: MCP Server Implementation┼── 2~3 days
                                  │
Phase 4: Validation & Improvement ┼── 2~3 days
                                  │
Phase 5: Multi-Code Support ──────┼── 1 week+
                                  │
Phase 6: Deployment & Documentation┘
```

---

## Phase 0: Preparation (Complete)

### Goals
- Project structure setup
- Required tools verification
- Marker bbox output verification

### Checklist

- [ ] Create GitHub repository
- [ ] Create basic directory structure
- [ ] Test Marker bbox output
- [ ] Test PyMuPDF clip feature
- [ ] Document development environment

---

## Phase 1: Marker Batch Execution (6~12 hours)

### Goals
- Convert all PDFs with Marker
- Generate MD + meta.json

### Target PDFs (12)

| # | File | Code |
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

### Execution Commands

```bash
# Batch execution
python scripts/batch_process.py marker

# Or individual execution
marker_single "sources/NBC2025p1.pdf" --output_dir "marker/nbc_2025"
```

### Output

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

## Phase 2: Hybrid Pipeline (1~2 hours)

### Goals
- Detect and fix broken tables
- Extract high-quality tables with pdfplumber

### Workflow

```
[1. Marker MD] → [2. Scanner] → [3. Judge] → [4. Surgery] → [5. Injection]
     ↓              ↓              ↓             ↓              ↓
   Full MD      Table detection  Quality check  pdfplumber   HTML replace
```

### Execution Commands

```bash
# Hybrid pipeline execution
python scripts/hybrid_pipeline.py sources/NBC2025p1.pdf marker/nbc_2025

# Or batch execution
python scripts/batch_process.py
```

→ Details: [06_HYBRID_PIPELINE.md](./06_HYBRID_PIPELINE.md)

---

## Phase 3: MCP Server Implementation (2~3 days)

### Goals
- Generate structure_map
- Implement MCP server
- Complete local testing

### Tasks

#### Day 1: Map Generation

- [ ] Write `generate_map.py`
- [ ] Implement coordinate extraction logic from Marker output
- [ ] Implement Section ID parsing logic
- [ ] Generate map.json for each code

#### Day 2: Extractor & DB

- [ ] Write `extractor.py`
- [ ] Implement Fast Mode (bbox-based)
- [ ] Implement Slow Mode (pattern matching)
- [ ] Implement `database.py` SQLite + FTS5

#### Day 3: MCP Server

- [ ] Implement `server.py` MCP server
- [ ] Test Claude Desktop integration
- [ ] Bug fixes

### Output

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

## Phase 4: Validation & Improvement (2~3 days)

### Goals
- Validate extraction accuracy
- Fill in missing sections
- Performance optimization

### Tasks

#### Validation

- [ ] Test full section extraction
- [ ] Verify table extraction
- [ ] Check formula area handling
- [ ] Handle multi-page content

#### Improvement

- [ ] Manually add missing sections
- [ ] Table special handling logic
- [ ] Strengthen error handling

#### Optimization

- [ ] Measure and improve extraction speed
- [ ] Optimize memory usage
- [ ] Implement caching strategy

### Quality Criteria

| Item | Target |
|------|--------|
| Section coverage | > 95% |
| Extraction accuracy | > 98% |
| Setup time | < 2 min |
| Search response | < 1 sec |

---

## Phase 5: Multi-Code Support (1 week+)

### Goals
- Add BC, Alberta, Quebec codes
- Implement code comparison feature

### Priority

| Priority | Code | Reason |
|----------|------|--------|
| 1 | NBC | Covers 8 provinces |
| 2 | BCBC | Canada's 3rd largest province |
| 3 | ABC (Alberta) | Energy industry hub |
| 4 | QCC (Quebec) | French market, separate |

### Advanced Features

```python
@server.tool()
async def compare_codes(
    section_id: str,
    codes: list = ["OBC", "NBC"]
) -> str:
    """
    Compare same section across multiple codes
    e.g., "9.8.2.1 OBC vs NBC differences"
    """
    ...

@server.tool()
async def get_provincial_requirements(
    topic: str,
    province: str
) -> str:
    """
    Get requirements for specific province
    e.g., "Ontario energy efficiency requirements"
    """
    ...
```

---

## Phase 6: Deployment & Documentation (3-5 days)

### Goals
- Public GitHub release
- Complete user documentation
- Collect community feedback

### Tasks

#### Documentation

- [ ] README.md (Installation guide)
- [ ] CONTRIBUTING.md
- [ ] API documentation
- [ ] Tutorial video/GIF

#### Deployment

- [ ] PyPI package registration (optional)
- [ ] Create GitHub Releases
- [ ] Register with Anthropic MCP registry (if possible)

#### Promotion

- [ ] Reddit (r/architecture, r/engineering)
- [ ] LinkedIn post
- [ ] Anthropic Discord/Forum

---

## Milestone Summary

| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| **M1: OBC MVP** | +1 week | Working OBC MCP |
| **M2: Validation Complete** | +2 weeks | 95% coverage achieved |
| **M3: NBC Added** | +3 weeks | Multi-code support |
| **M4: Public Release** | +4 weeks | GitHub v1.0 release |

---

## Risks & Mitigation

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Marker bbox incomplete | Medium | Supplement with PyMuPDF |
| PDF version diversity | High | Support multiple hashes |
| NRC permission denied | Low | Proceed with coordinate approach |
| Performance issues | Low | Caching, indexing optimization |

---

## Next Document

→ [05_USER_GUIDE.md](./05_USER_GUIDE.md) - User Guide
