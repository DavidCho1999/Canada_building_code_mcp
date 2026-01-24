# Canadian Building Code MCP

[![PyPI version](https://badge.fury.io/py/building-code-mcp.svg)](https://pypi.org/project/building-code-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Smithery](https://smithery.ai/badge/davidcho/ca-building-code-mcp)](https://smithery.ai/server/davidcho/ca-building-code-mcp)

**AI-powered search for 24,000+ Canadian building code sections.**

Enable AI assistants to search, navigate, and cite building regulations across NBC, OBC, BCBC, and 13 other Canadian codes.

> Works with Claude Desktop and any MCP-compatible client (Cursor, Windsurf, etc.)

<!-- TODO: Add GIF demo here
![Demo](docs/demo.gif)
-->

---

## Why This Exists

Architects and engineers waste hours searching through thousands of pages of building codes. This MCP server lets AI do the heavy lifting:

```
You: "What are the fire separation requirements for a 3-storey
     residential building in Saskatchewan?"

Claude: [Searches NBC 2025, finds relevant sections, extracts text]

        "According to NBC 2025 Section 3.2.2.55, Group C buildings
         up to 3 storeys with sprinklers require:
         - Maximum area: 1,800 m²
         - Floor assemblies: 45-min fire-resistance rating
         - Load-bearing walls: Same rating as supported assembly"
```

---

## Features

| Feature | Description |
|---------|-------------|
| **24,000+ Sections** | NBC, OBC, BCBC, ABC, QCC + 11 more codes indexed |
| **Smart Search** | Fuzzy matching, synonyms, "Did you mean?" suggestions |
| **Token Optimized** | 81% reduction vs naive approach (v1.2.0) |
| **Copyright Safe** | BYOD model - coordinates only, you provide the PDF |
| **Jurisdiction Aware** | Knows which code applies where (ON→OBC, BC→BCBC) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│            MCP Client (Claude, Cursor, etc.)                 │
└─────────────────────────┬───────────────────────────────────┘
                          │ MCP Protocol
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Building Code MCP Server                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ search_code  │  │ get_section  │  │ get_table    │       │
│  │ (fuzzy+TF-IDF│  │ (BYOD text)  │  │ (markdown)   │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │               │
│         ▼                 ▼                 ▼               │
│  ┌─────────────────────────────────────────────────┐        │
│  │              maps/*.json (15.9 MB)              │        │
│  │         Section IDs, pages, keywords, bbox       │        │
│  └─────────────────────────────────────────────────┘        │
│                          │                                  │
│                          ▼ (BYOD mode only)                 │
│  ┌─────────────────────────────────────────────────┐        │
│  │              User's PDF (via PyMuPDF)            │        │
│  │           Text extraction at runtime             │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

**Two Modes:**
- **Map-Only** (default): Returns page numbers & coordinates. No PDF needed.
- **BYOD**: Connect your PDF via `set_pdf_path` for full text extraction.

---

## Quick Start (1 minute)

### Option 1: Smithery (Recommended)

```bash
npx -y @smithery/cli@latest install davidcho/ca-building-code-mcp --client claude
```

### Option 2: uvx

```bash
# Install uv (one-time)
pip install uv
```

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "building-code": {
      "command": "uvx",
      "args": ["building-code-mcp"]
    }
  }
}
```

### Option 3: pip

```bash
pip install building-code-mcp
```

```json
{
  "mcpServers": {
    "building-code": {
      "command": "building-code-mcp"
    }
  }
}
```

---

## Example Conversations

### Finding Requirements

```
You: "I'm designing a 6-storey office building in Vancouver.
     What are the fire separation requirements?"

Claude: Let me search the BC Building Code...

[Uses search_code("fire separation office", code="BCBC")]
[Uses get_section("3.2.2.57", code="BCBC")]

Based on BCBC 2024 Section 3.2.2.57, a 6-storey Group D
(business) building requires:
- Sprinkler system: Required
- Floor assemblies: 1-hour fire-resistance rating
- Maximum building area: 7,200 m²
```

### Checking Specific Sections

```
You: "What does OBC section 9.10.14.1 say about spatial separation?"

Claude: [Uses get_section("9.10.14.1", code="OBC_Vol1")]

OBC Section 9.10.14.1 - Spatial Separation Between Buildings:
"Buildings on the same property shall have spatial separation
between them based on the aggregate area of unprotected openings
in exposing building faces..."
```

### Jurisdiction Lookup

```
You: "Which building code applies in Calgary?"

Claude: [Uses get_applicable_code("Calgary, Alberta")]

Calgary follows the Alberta Building Code (ABC) 2023.
Primary codes: ABC, AFC (Fire), APC (Plumbing)
Also check: National codes (NBC, NFC) for reference
```

---

## Supported Codes

### National Codes (4)
NBC 2025, NFC 2025, NPC 2025, NECB 2025

### Provincial Codes (9)
- **Ontario**: OBC 2024 (Vol 1 & 2), OFC
- **British Columbia**: BCBC 2024
- **Alberta**: ABC 2023
- **Quebec**: QCC, QECB, QPC, QSC (2020)

### User's Guides (3)
IUGP9 (Part 9 Housing), UGP4 (Structural), UGNECB (Energy)

**Total: 24,000+ indexed sections**

---

## Token Efficiency (v1.2.0)

Built-in optimizations reduce token usage:

| Optimization | Reduction |
|--------------|-----------|
| `list_codes` compact mode | 81% |
| `disclaimer` as resource | 61% |
| Default `verbose=false` | ~50% |

**Best practice:** Use `limit=5-10` and only request `verbose=true` when needed.

See [Token Efficiency Guide](docs/CLAUDE_RULES.md) for details.

---

## Tools Available

| Tool | Purpose |
|------|---------|
| `list_codes` | Show available codes and connection status |
| `search_code` | Find sections by keywords |
| `get_section` | Get section details (page, citation, text) |
| `get_table` | Get table content as markdown |
| `get_hierarchy` | Navigate parent/child sections |
| `verify_section` | Check if section ID exists |
| `get_applicable_code` | Find codes for a location |
| `set_pdf_path` | Connect PDF for text extraction |

---

## API Access

REST API: https://canada-aec-code-mcp.onrender.com

```bash
curl https://canada-aec-code-mcp.onrender.com/search/fire+separation
```

> Note: Hosted API runs in Map-Only mode. Use local MCP for full text.

---

## Development

```bash
git clone https://github.com/DavidCho1999/Canada_building_code_mcp.git
cd Canada_building_code_mcp
pip install -e ".[all]"
python src/mcp_server.py
```

---

## License

MIT License - See [LICENSE](LICENSE)

---

## Links

- [PyPI](https://pypi.org/project/building-code-mcp/)
- [Smithery](https://smithery.ai/server/davidcho/ca-building-code-mcp)
- [Token Efficiency Guide](docs/CLAUDE_RULES.md)
