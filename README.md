# Canadian Building Code MCP Server

[![PyPI version](https://badge.fury.io/py/building-code-mcp.svg)](https://pypi.org/project/building-code-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that enables Claude to search and navigate Canadian building codes.

## Quick Setup (3 Steps)

**1. Install the package**
```bash
pip install building-code-mcp
```

**2. Add to Claude Desktop config**

Config file location:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

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

**3. Restart Claude Desktop and start asking!**

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
| NBC | 2025 | 2,783 | National Building Code |
| NFC | 2025 | 1,044 | National Fire Code |
| NPC | 2025 | 413 | National Plumbing Code |
| NECB | 2025 | 475 | National Energy Code for Buildings |
| OBC | 2024 | 4,108 | Ontario Building Code (Vol 1 & 2) |
| OFC | O. Reg. 213/07 | 1,906 | Ontario Fire Code |
| BCBC | 2024 | 2,584 | British Columbia Building Code |
| ABC | 2023 | 2,832 | Alberta Building Code |
| QCC | 2020 | 2,726 | Quebec Construction Code |
| QECB | 2020 | 384 | Quebec Energy Code |
| QPC | 2020 | 428 | Quebec Plumbing Code |
| QSC | 2020 | 1,063 | Quebec Safety Code |

### User's Guides (3)

| Guide | Version | Sections | Description |
|-------|---------|----------|-------------|
| IUGP9 | 2020 | 1,096 | Illustrated Guide - Part 9 Housing |
| UGP4 | 2020 | 495 | User's Guide - NBC Structural Commentaries |
| UGNECB | 2020 | 165 | User's Guide - NECB |

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

## License

MIT License - See [LICENSE](LICENSE) file.
