# CLAUDE.md - Canadian Building Code MCP

## Project Information

- **Project Name**: Canadian Building Code MCP
- **Purpose**: MCP server enabling Claude to search/reference Canadian Building Codes
- **Strategy**: "Map & Territory" - Distribute coordinates only, text extracted from user's PDF
- **Status**: Phase 1-3 Complete (Docling + Map Generation + MCP Server with Prompts/Resources)
- **Current Version**: 1.2.0 (PyPI + Smithery)

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

### 4. Dev Server Must Run Externally (CRITICAL!)
- **Claude Code must NEVER run `npm run dev`**
- User must run it manually in a separate terminal
- Why:
  - Long-running dev server → Claude Code process killed (exit code 137, SIGKILL)
  - Same issue even with `run_in_background: true`
  - Caused by Next.js + Turbopack's complex subprocess tree
- Workflow:
  1. User: Open separate terminal and run `cd website && npm run dev`
  2. User: Keep terminal open (for hot reload verification)
  3. Claude: Only modify files
  4. Claude: Use `curl http://localhost:3000` to check server status if needed
- Troubleshooting:
  - Server not starting: Ask user to run manually
  - Port conflict: Check with `lsof -i :3000` or `tasklist | grep node`
  - Cache issue: `rm -rf .next` then restart

### 5. MCP Token Efficiency (v1.1.1+)

#### ⚠️ 3-Strike Rule (Critical for Token Efficiency)
- **Same topic: Maximum 3 searches**
- After 3 tries with no results → clearly state "not specified in code"
- Different approaches/topics count separately
- Exception: User explicitly requests more

#### Pre-Search Planning
1. Clarify goal: "What exactly am I looking for?"
2. Select keywords: 1-2 only
3. Estimate location: Part? Division?
4. Execute → Evaluate → Decide

#### Parameter Optimization
- `limit`: 5-10 (default, v1.1.1+)
- `verbose`: false (default, 99% of cases)
- verbose=true: Only when metadata truly needed

#### Token Budget
- Simple: 100-300 tokens (1-3 calls)
- Complex: 500-1000 tokens (3-5 calls)
- ⚠️ 1500+: Review strategy

#### Real Case Study
**Bad:** 29 searches, 5100 tokens → "not specified in OBC"
**Good:** 3 searches, 150 tokens → same conclusion (97% reduction)

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

## MCP Server Features

### Tools (10)
1. **list_codes** - List all available codes with download links
2. **search_code** - Search sections by keywords with TF-IDF ranking
3. **get_section** - Get section details (page, coords, text if BYOD)
4. **get_hierarchy** - Navigate parent/child/sibling sections
5. **verify_section** - Verify section exists (prevent hallucination)
6. **get_applicable_code** - Find which codes apply to location
7. **get_table** - Get table content by ID
8. **set_pdf_path** - Connect PDF for BYOD mode
9. **get_page** - Get full page text (BYOD mode)
10. **get_pages** - Get multi-page text (BYOD mode)

### Prompts (4)
1. **search_building_code** - Search for requirements/regulations
2. **verify_code_reference** - Confirm section references are valid
3. **find_applicable_code** - Determine jurisdiction
4. **explore_code_structure** - Navigate code hierarchy

### Resources (4)
1. **buildingcode://welcome** - Getting Started guide with legal notice, PDF sources
2. **buildingcode://codes** - List of all available codes
3. **buildingcode://stats** - Section counts and coverage stats
4. **buildingcode://code/{code}** - Metadata for specific code

### Operating Modes
- **Map-Only Mode** (Default): Returns page numbers + coordinates only
- **BYOD Mode** (Bring Your Own Document): Full text extraction after `set_pdf_path`

---

## Conversion Progress (Complete)

### Codes (13)
| Code | Sections |
|------|----------|
| NBC | 3,000+ |
| NFC | 1,000+ |
| NPC | 440+ |
| NECB | 530+ |
| ABC | 3,000+ |
| BCBC | 2,700+ |
| OBC Vol1 | 3,500+ |
| OBC Vol2 | 890+ |
| OFC | 1,900+ |
| QCC | 2,900+ |
| QECB | 420+ |
| QPC | 450+ |
| QSC | 1,000+ |

### User's Guides (3)
| Guide | Sections |
|-------|----------|
| IUGP9 (Part 9) | 1,400+ |
| UGP4 (Part 4) | 490+ |
| UGNECB | 160+ |

**Total: 24,000+ sections indexed**

---

## Reference Documents

- `docs/PDF_DOWNLOAD_LINKS.md` - PDF download links
- `docs/archive/` - Previous documentation

---

## Recent Updates

### v1.2.0 (2026-01-23)
- **Token Optimization**: Significant reduction in token usage
  - `list_codes`: Added verbose parameter (81% reduction, ~1,026 tokens)
  - `disclaimer`: Converted to resource, reference only (61% reduction)
- **"Did you mean?" suggestions**: Recommend similar keywords when no results
- **Logging system**: stderr output for debugging in MCP Inspector
- **Tool descriptions improved**: Clearer and more concise

### v1.0.8 (2026-01-22)
- Added **Welcome Resource** (buildingcode://welcome) with legal notice and PDF sources
- Added **4 Prompts** for common use cases
- Added **4 Resources** for code discovery
- Updated section counts to **24,000+** (improved map generation)
- Added **full tool schema** to smithery.yaml for better quality score
- README simplified with "##+" format for section counts

### Smithery Quality Score Improvements
- Tool Quality: Added ToolAnnotations (readOnlyHint, destructiveHint, idempotentHint, openWorldHint)
- Server Capabilities: Added Prompts and Resources (+10 points expected)
- Server Metadata: Added homepage, icon, displayName
- Full inputSchema for all 10 tools in smithery.yaml
