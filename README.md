# Canadian Building Code MCP Server

[![PyPI version](https://badge.fury.io/py/building-code-mcp.svg)](https://pypi.org/project/building-code-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that enables Claude to search and navigate Canadian building codes.

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

## Installation

### Option A: pip install (Recommended)

```bash
pip install building-code-mcp

# With PDF text extraction support
pip install building-code-mcp[pdf]
```

### Option B: From GitHub

```bash
pip install git+https://github.com/DavidCho1999/Canada-AEC-Code-MCP.git
```

### Option C: Clone and install

```bash
git clone https://github.com/DavidCho1999/Canada-AEC-Code-MCP.git
cd Canada-AEC-Code-MCP
pip install -e ".[pdf]"
```

### Configure Claude Desktop

Find your Claude Desktop config file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this to the config file:

```json
{
  "mcpServers": {
    "building-code": {
      "command": "building-code-mcp"
    }
  }
}
```

Restart Claude Desktop. You should see "building-code" in the MCP tools.

## Usage Examples

Once installed, just ask Claude naturally:

```
"Search for egress requirements in NBC"
"What does section 3.2.4.1 say in OBC?"
"Find fire resistance ratings for walls"
"Which building code applies in Toronto?"
"List all available building codes"
```

## Available Tools

| Tool | Description |
|------|-------------|
| `list_codes` | List all available codes and section counts |
| `search_code` | Search by keywords (e.g., "fire separation") |
| `get_section` | Get specific section by ID (e.g., "9.10.14.1") |
| `get_hierarchy` | Get parent, children, siblings of a section |
| `set_pdf_path` | Connect your PDF for full text extraction (BYOD) |
| `verify_section` | Verify section exists and get formal citation |
| `get_applicable_code` | Get which codes apply to a Canadian location |

## How It Works

### Mode A: Map Only (Default)
Returns section metadata: ID, title, page number, keywords.
Works without any PDF files.

### Mode B: BYOD (Bring Your Own Document)
Connect your legally obtained PDF to get full text:
```
"Connect my NBC PDF at C:/codes/NBC2025.pdf"
```
The server extracts text from the exact page and coordinates.

## Running Tests

```bash
pip install pytest
pytest tests/test_smoke.py -v
```

## Troubleshooting

### "MCP server not showing in Claude Desktop"
1. Make sure Python is in your PATH
2. Restart Claude Desktop completely
3. Check logs: `%APPDATA%\Claude\logs\` (Windows)

### "No results found"
- Try simpler search terms (e.g., "fire" instead of "fire separation requirements")
- Check if the code exists: ask Claude "list available codes"

### "PDF text extraction not working"
- Ensure the PDF path is correct and file exists
- The PDF version must match the map version (e.g., NBC 2025 map needs NBC 2025 PDF)
- Install with PDF support: `pip install building-code-mcp[pdf]`

## For Developers

### Adding New Codes

1. Convert PDF with Docling:
```bash
pip install docling
python scripts/convert_with_docling.py path/to/code.pdf
```

2. Generate map:
```bash
python scripts/generate_map_v2.py docling_output/code_name/
```

### Project Structure

```
Canada-AEC-Code-MCP/
├── maps/               # 16 code index files (JSON)
├── src/
│   └── mcp_server.py   # MCP server
├── scripts/            # Pipeline scripts
├── tests/              # Smoke tests
└── README.md
```

## Disclaimer

This is a structural index for Canadian Building Codes. **No copyrighted text is distributed.** This is not an official NRC or government product.

Building codes are published by the National Research Council of Canada (NRC) and provincial authorities. Please obtain official copies through proper channels.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Run tests: `pytest tests/test_smoke.py -v`
4. Submit a pull request

## Changelog

### v1.0.1 (2026-01-22)
- PyPI package release (`pip install building-code-mcp`)
- GitHub Actions auto-publish on tag
- Added User's Guides (IUGP9, UGP4, UGNECB)
- Bug fixes and improvements
- Added smoke tests

### v1.0.0 (2026-01-21)
- Initial release with 13 Canadian building codes
- 20,000+ indexed sections
- BYOD mode for full text extraction

## License

MIT License - See [LICENSE](LICENSE) file.
