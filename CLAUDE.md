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
- **Claude Code는 절대 `npm run dev` 실행 금지**
- User가 별도 터미널에서 직접 실행해야 함
- Why:
  - Long-running dev server → Claude Code 프로세스 종료 (exit code 137, SIGKILL)
  - `run_in_background: true` 사용해도 동일하게 종료됨
  - Next.js + Turbopack의 복잡한 subprocess tree가 원인
- Workflow:
  1. User: 별도 터미널 열어서 `cd website && npm run dev`
  2. User: 터미널 열어둔 상태 유지 (hot reload 확인용)
  3. Claude: 파일 수정만 담당
  4. Claude: 서버 상태 확인 필요시 `curl http://localhost:3000` 사용
- Troubleshooting:
  - Server 안뜨면: User에게 직접 실행하도록 안내
  - Port 충돌: `lsof -i :3000` 또는 `tasklist | grep node` 확인
  - Cache 문제: `rm -rf .next` 후 재시작

### 5. MCP 토큰 효율화 (v1.1.1+)

#### ⚠️ 3-Strike Rule (Critical for Token Efficiency)
- **같은 주제: 최대 3번 검색**
- 3번 후 답 없으면 → "규정 없음" 명확히 인정
- 다른 접근/다른 주제는 별도 카운트
- 예외: 사용자 명시적 요청

#### 검색 전 계획
1. 목표 명확화: "정확히 무엇을 찾는가?"
2. 키워드 선정: 1-2개만
3. 예상 위치: Part? Division?
4. 실행 → 평가 → 결정

#### 파라미터 최적화
- `limit`: 5-10 (기본값, v1.1.1+)
- `verbose`: false (기본값, 99% 경우)
- verbose=true: 메타데이터 정말 필요할 때만

#### 토큰 예산
- 간단: 100-300 tokens (1-3회)
- 복잡: 500-1000 tokens (3-5회)
- ⚠️ 1500+: 전략 재검토

#### 실제 사례
**Bad:** 29회 검색, 5100 tokens → "OBC에 명시 없음"
**Good:** 3회 검색, 150 tokens → 동일한 결론 (97% 절감)

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
- **Token Optimization**: 토큰 사용량 대폭 절감
  - `list_codes`: verbose 파라미터 추가 (81% 절감, ~1,026 tokens)
  - `disclaimer`: 리소스화로 참조만 전달 (61% 절감)
- **"Did you mean?" 제안**: 검색 결과 없을 때 유사 키워드 추천
- **로깅 시스템**: stderr 출력으로 MCP Inspector에서 디버깅 가능
- **도구 설명 개선**: 더 명확하고 간결한 description

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
