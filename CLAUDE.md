# CLAUDE.md - Canadian Building Code MCP

## Project Information

- **Project Name**: Canadian Building Code MCP
- **Purpose**: MCP server enabling Claude to search/reference Canadian Building Codes
- **Strategy**: "Map & Territory" - Distribute coordinates only, text extracted from user's PDF
- **Status**: Phase 1-2 Complete (Docling + Map Generation)

---

## Core Concepts

### Legal Safety Strategy
```
Distributed: Coordinates (page, bbox), Section ID, structure type
NOT Distributed: Actual text, table data
→ 99% legally safe
```

### Current Pipeline (Docling-based)
```
[PDF] → [Docling] → [MD + JSON]
            ↓
    [generate_map.py] Section extraction + TF-IDF keywords
            ↓
    [maps/*.json] Coordinate map generation
            ↓
    [MCP Server] Mode A (map only) / Mode B (BYOD text)
```

---

## File Structure

```
building_code_mcp/
├── docs/               # Documentation
├── scripts/            # Pipeline scripts
├── src/                # MCP server code
├── marker/             # Marker output
├── sources/            # PDF files (gitignore)
└── maps/               # structure_map.json
```

---

## Development Rules

### 0. Memory Limitation (Important!)
- **User Environment: 16GB RAM laptop**
- Docling conversion must be run **one at a time** sequentially
- Parallel execution strictly prohibited → System crash from memory shortage
- Be especially careful with large PDFs (>50MB)

### 1. Never commit PDFs to git
- sources/ folder is included in .gitignore
- Copyright issues

### 2. Table Quality Assessment (6 Criteria)
1. NO_PIPES - Flat text
2. COL_MISMATCH - Column count mismatch
3. EMPTY_CELLS - Empty cells 25%+
4. ROWSPAN_BROKEN - First column empty cells repeated
5. NO_DATA - Header only
6. DUPLICATE_HEADER - Multi-page split

### 3. Use meta.json for Page Lookup
- Full PDF scan ❌
- Manual mapping ❌
- meta.json → Table Index ✅

---

## Target Documents (16)

**Codes (13):**
- National (4): NBC, NFC, NPC, NECB (2025)
- Provincial (9): OBC×2, BCBC, ABC, OFC, QCC, QECB, QPC, QSC

**User's Guides (3):**
- IUGP9: Part 9 Guide (Housing & Small Buildings)
- UGP4: Part 4 Guide (Structural Commentaries)
- UGNECB: Energy Code Guide

---

## Commands

```bash
# 1. PDF → MD/JSON conversion (one at a time!)
python scripts/convert_with_docling.py sources/NBC2025p1.pdf

# 2. Generate map for Building Codes (Division A/B/C structure)
python scripts/generate_map_v2.py docling_output/nbc2025p1/

# 3. Generate map for User's Guides (Commentary structure)
python scripts/generate_map_guide.py docling_output/ugp4_2020p1/ --type ugp4
python scripts/generate_map_guide.py docling_output/ugnecb_2020p1/ --type ugnecb

# 4. Run MCP server
python src/mcp_server.py
```

---

## Conversion Progress (Complete)

### Codes (13)
| Code | Sections |
|------|----------|
| NBC | 2,783 |
| NFC | 1,044 |
| NPC | 413 |
| NECB | 475 |
| ABC | 2,832 |
| BCBC | 2,584 |
| OBC Vol1 | 3,327 |
| OBC Vol2 | 781 |
| OFC | 1,906 |
| QCC | 2,726 |
| QECB | 384 |
| QPC | 428 |
| QSC | 1,063 |

### User's Guides (3)
| Guide | Sections |
|-------|----------|
| IUGP9 (Part 9) | 1,096 |
| UGP4 (Part 4) | 495 |
| UGNECB | 165 |

**Total: 22,502 sections indexed**

---

## Reference Documents

- `docs/PDF_DOWNLOAD_LINKS.md` - PDF download links
- `docs/archive/` - Previous documentation
