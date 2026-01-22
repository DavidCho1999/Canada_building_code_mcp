# Canadian Building Code MCP Server

A Model Context Protocol (MCP) server that enables Claude to search and navigate Canadian building codes.

## What It Does

Ask Claude questions like:
- "Find fire separation requirements for garages in NBC"
- "What are the stair width requirements in OBC?"
- "Show me section 9.10.14 of the Building Code"

Claude will search 18,000+ indexed sections across 12 Canadian building codes and return relevant sections with page numbers.

## Supported Codes

| Code | Version | Sections | Description |
|------|---------|----------|-------------|
| NBC | 2025 | 2,783 | National Building Code |
| NFC | 2025 | 1,044 | National Fire Code |
| NPC | 2025 | 413 | National Plumbing Code |
| NECB | 2025 | 475 | National Energy Code for Buildings |
| OBC | 2024 | 4,108 | Ontario Building Code (Vol 1 & 2) |
| BCBC | 2024 | 2,584 | British Columbia Building Code |
| ABC | 2023 | 2,832 | Alberta Building Code |
| QCC | 2020 | 2,726 | Quebec Construction Code |
| QECB | 2020 | 384 | Quebec Energy Code |
| QPC | 2020 | 428 | Quebec Plumbing Code |
| QSC | 2020 | 1,063 | Quebec Safety Code (Fire) |

### Web References (Read-Only)

These codes don't have searchable indexes but Claude can read them directly:

| Code | Description | Source |
|------|-------------|--------|
| OFC | Ontario Fire Code | [Ontario e-Laws](https://www.ontario.ca/laws/regulation/070213) |

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/DavidCho1999/Canada-AEC-Code-MCP.git
cd Canada-AEC-Code-MCP
```

### 2. Install dependencies

```bash
pip install mcp pymupdf
```

### 3. Configure Claude Desktop

Find your Claude Desktop config file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this to the config file:

```json
{
  "mcpServers": {
    "building-code": {
      "command": "python",
      "args": ["C:/full/path/to/Canada-AEC-Code-MCP/src/mcp_server.py"]
    }
  }
}
```

**Important**: Use the full absolute path to `mcp_server.py`

### 4. Restart Claude Desktop

Close and reopen Claude Desktop. You should see "building-code" in the MCP tools.

## Usage Examples

Once installed, just ask Claude naturally:

```
"Search for egress requirements in NBC"
"What does section 3.2.4.1 say in OBC?"
"Find fire resistance ratings for walls"
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

## Project Structure

```
Canada-AEC-Code-MCP/
├── maps/               # 12 code index files (JSON)
├── src/
│   └── mcp_server.py   # MCP server
├── scripts/
│   └── generate_map_v2.py  # Map generation tool
└── README.md
```

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

## Disclaimer

This is a structural index for Canadian Building Codes. No copyrighted text is distributed. This is not an official NRC or government product.

Building codes are published by the National Research Council of Canada (NRC) and provincial authorities. Please obtain official copies through proper channels.

## License

MIT License - See [LICENSE](LICENSE) file.
