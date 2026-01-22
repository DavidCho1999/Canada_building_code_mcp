# Canadian Building Code MCP Server

[![PyPI version](https://badge.fury.io/py/building-code-mcp.svg)](https://pypi.org/project/building-code-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that enables Claude to search and navigate Canadian building codes.

## How It Works

This MCP server operates in **two modes**:

| Mode | Use Case | PDF Required | Text Extraction |
|------|----------|--------------|-----------------|
| **Map-Only** | Hosted API, Quick lookup | No | Page numbers & coordinates only |
| **BYOD** | Local MCP with full text | Yes (your own) | Full section text |

### Map-Only Mode (Default)
- Returns page numbers, section IDs, and coordinates
- Works everywhere (local, Vercel, Render, etc.)
- **No PDF needed** - just the indexed maps

### BYOD Mode (Bring Your Own Document)
- Connect YOUR legally obtained PDF using `set_pdf_path`
- Get full text extraction from sections
- **Local MCP only** - not available in hosted API

> **Note**: The hosted API at `canada-aec-code-mcp.onrender.com` runs in Map-Only mode. For full text extraction, run the MCP server locally and connect your own PDFs.

---

## Quick Setup

### Option A: Smithery (One-click install)

```bash
npx -y @smithery/cli@latest install davidcho/ca-building-code-mcp --client claude
```

### Option B: uvx (No install needed)

Add to Claude Desktop config (`%APPDATA%\Claude\claude_desktop_config.json` on Windows, `~/Library/Application Support/Claude/claude_desktop_config.json` on Mac):

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

### Option C: pip install

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

## What It Does

Ask Claude questions like:
- "Find fire separation requirements for garages in NBC"
- "What are the stair width requirements in OBC?"
- "Show me section 9.10.14 of the Building Code"

Claude will search **22,500+ indexed sections** across 16 Canadian building codes and guides.

## Supported Codes

### Building Codes (13)

| Code | Version | Sections | Description |
|------|---------|----------|-------------|
| NBC | 2025 | 2,700+ | National Building Code |
| NFC | 2025 | 1,000+ | National Fire Code |
| NPC | 2025 | 400+ | National Plumbing Code |
| NECB | 2025 | 450+ | National Energy Code for Buildings |
| OBC | 2024 | 4,100+ | Ontario Building Code (Vol 1 & 2) |
| OFC | O. Reg. 213/07 | 1,900+ | Ontario Fire Code |
| BCBC | 2024 | 2,500+ | British Columbia Building Code |
| ABC | 2023 | 2,800+ | Alberta Building Code |
| QCC | 2020 | 2,700+ | Quebec Construction Code |
| QECB | 2020 | 380+ | Quebec Energy Code |
| QPC | 2020 | 420+ | Quebec Plumbing Code |
| QSC | 2020 | 1,000+ | Quebec Safety Code |

### User's Guides (3)

| Guide | Version | Sections | Description |
|-------|---------|----------|-------------|
| IUGP9 | 2020 | 1,000+ | Illustrated Guide - Part 9 Housing |
| UGP4 | 2020 | 490+ | User's Guide - NBC Structural Commentaries |
| UGNECB | 2020 | 160+ | User's Guide - NECB |

## Usage Examples

Once installed, just ask Claude naturally:

```
"Search for egress requirements in NBC"
"What does section 3.2.4.1 say in OBC?"
"Find fire resistance ratings for walls"
"Which building code applies in Toronto?"
"List all available building codes"
```

## API Access

REST API available at: https://canada-aec-code-mcp.onrender.com

```
GET /codes              - List all codes
GET /search/{query}     - Search sections
GET /section/{id}       - Get section details
```

> **Hosted API Limitation**: The hosted API runs in Map-Only mode. `set_pdf_path` is not available - use local MCP for full text extraction.

## License

MIT License - See [LICENSE](LICENSE) file.
