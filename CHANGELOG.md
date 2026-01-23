# Changelog

All notable changes to this project will be documented in this file.

## [1.1.1] - 2026-01-23

### Changed
- Re-release of 1.1.0 with proper PyPI distribution

## [1.1.0] - 2026-01-23

### Added - Token Efficiency Optimization (70% reduction)

**New Parameters for Token Control:**
- `search_code`: Added `limit` (default: 10, max: 50) and `verbose` (default: false) parameters
- `get_section`: Added `verbose` (default: false) parameter

**Benefits:**
- 70% token reduction in typical workflows
- Compact responses by default (id, title, page, score, citation)
- Full metadata available via `verbose=true` when needed

**What's Included in Compact Mode:**
- Essential fields: id, title, page, citation, score
- Total result count with hint message
- Code field (when searching all codes)

**What's in Verbose Mode Only:**
- Extended metadata: document_type, match_type, type, level
- Keywords array for context
- Bounding box coordinates (bbox)
- Mode info and detailed status

**Breaking Changes:**
- None - backwards compatible. Default behavior is now more efficient.

**Migration Guide:**
```python
# Before (still works, but uses more tokens)
search_code("fire", "NBC")  # Returns 20 results with all metadata

# After (recommended - 70% fewer tokens)
search_code("fire", "NBC")  # Returns 10 results, compact format
search_code("fire", "NBC", limit=20, verbose=True)  # Old behavior
```

**Test Results:**
- Real AEC workflow (5 steps): 619 tokens (compact) vs 2075 tokens (verbose)
- Core functionality: 100% preserved
- Search accuracy: Unchanged

---

## [1.0.8] - 2026-01-22

### Added
- Welcome Resource (`buildingcode://welcome`) with legal notice and PDF sources
- 4 Prompts for common use cases (search, verify, find applicable, explore)
- 4 Resources for code discovery
- Tool quality annotations (readOnlyHint, idempotentHint, etc.)

### Changed
- Updated section counts to 24,000+ (improved map generation)
- Simplified README with "##+" format for section counts
- Added full tool schema to smithery.yaml

---

## [1.0.0] - 2026-01-20

### Initial Release
- MCP server for 16 Canadian Building Codes (13 codes + 3 guides)
- 24,000+ indexed sections
- Map-Only mode (default) and BYOD mode
- 10 tools, 4 prompts, 4 resources
- TF-IDF search with synonym expansion and fuzzy matching
- Jurisdiction detection for applicable codes
- PyPI and Smithery distribution
