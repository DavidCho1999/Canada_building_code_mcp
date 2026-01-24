# MCP Project Conversation Log

> As of 2026-01-21

---

## Key Decisions

### 1. "Coordinate Overlay" (Map & Territory) Strategy Adopted

**Concept:**
- Distributed: Coordinates (page, bbox), Section ID, structure type
- NOT Distributed: Actual text, table data
- User extracts text from their legally obtained PDF

**Legal Safety: 99%**
- Coordinates are "facts" → Not protected by copyright
- "Give the map, user brings the territory"

### 2. Fast Mode vs Slow Mode

| Mode | Condition | Method |
|------|-----------|--------|
| **Fast Mode** | PDF hash matches | Coordinate (bbox) based extraction |
| **Slow Mode** | PDF hash mismatch | Pattern matching extraction |

### 3. Target Codes: 14 Confirmed

**National (4):** NBC, NFC, NPC, NECB (all 2025)
**Provincial (7):** OBC, BCBC, ABC, QCC×4
**User's Guides (3):** NBC Part 9, NBC Part 4, NECB Guide

---

## Key Findings

### Marker polygon Data Confirmed

In `data/marker/chunk_01/301880/301880_meta.json`:
```json
{
  "title": "TO: BUILDING CODE USERS",
  "page_id": 1,
  "polygon": [
    [66.33984375, 204.56146240234375],
    [232.76397705078125, 204.56146240234375],
    [232.76397705078125, 216.56146240234375],
    [66.33984375, 216.56146240234375]
  ]
}
```

→ Extractable with PyMuPDF `page.get_text("text", clip=rect)`

### Marker Takes the Longest Time

| Step | Time |
|------|------|
| Marker PDF parsing | 30min~1hr+ (CPU) |
| polygon → structure_map | seconds |
| DB creation | seconds |
| MCP server setup | minutes |

---

## Legal Analysis

### Canadian Code Status

| Code | Status | Basis |
|------|--------|-------|
| OBC | ✅ Explicitly permitted | "non-commercial use" stated |
| NBC/NFC/NPC/NECB | ✅ Coordinates only = safe | NRC provides free PDF |
| BCBC | ✅ Coordinates only = safe | BC Gov provides free |
| ABC | ✅ Coordinates only = safe | NRC provides free PDF |
| Quebec | ✅ Coordinates only = safe | NRC provides free PDF |

### US vs Canada

- **US**: ICC copyright disputes, ongoing litigation
- **Canada**: Legally clearer, safer

---

## Architecture Summary

```
[Developer Side]
PDF → Marker → polygon extraction → structure_map.json
                                    ↓
                              Distribution (GitHub)

[User Side]
Official PDF download ← User
        ↓
structure_map.json + PDF → Text extraction → SQLite DB
                                            ↓
                                      MCP Server
                                            ↓
                                      Claude Desktop
```

---

## Next Steps

1. **Download PDFs** - 14 codes
2. **Run Marker** - Parse each PDF (30min~1hr × 14)
3. **Generate structure_map** - polygon → bbox conversion
4. **Extraction test** - PyMuPDF clip validation
5. **Implement MCP server** - Python MCP SDK

---

## Contact (If Permission Needed)

| Organization | Email |
|--------------|-------|
| NRC (National) | Codes@nrc-cnrc.gc.ca |
| BC (Provincial) | ipp@mail.qp.gov.bc.ca |

---

## Hybrid Pipeline (Added)

Marker + pdfplumber Combined Strategy:

```
[PDF] → [1. Marker] → [MD]
              ↓
        [2. Scanner] - "### Table" detection
              ↓
        [3. Judge] - Quality check
           /    \
       Good    Broken
         │       │
        Keep  [4. Surgery] - pdfplumber
                 │
        [5. Injection] - HTML replace
              ↓
        [Final MD]
```

→ Details: `06_HYBRID_PIPELINE.md`

---

## File Structure

```
H:\My Drive\lab\building_code_mcp\
├── README.md                 # Project overview
├── 01_ARCHITECTURE.md        # Architecture details
├── 02_IMPLEMENTATION.md      # Implementation code
├── 03_LEGAL.md               # Legal analysis
├── 04_ROADMAP.md             # Development roadmap (updated)
├── 05_USER_GUIDE.md          # User guide
├── 06_HYBRID_PIPELINE.md     # Hybrid pipeline (NEW)
├── PDF_DOWNLOAD_LINKS.md     # PDF link list
├── CONVERSATION_LOG.md       # This file
├── marker/
│   └── obc_part9/
│       ├── 301880_full.md    # OBC Part 9 Marker output
│       └── 301880_meta.json  # Coordinate info
└── sources/                  # PDF storage folder (12 downloaded)
```
