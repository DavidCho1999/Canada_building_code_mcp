# Canadian Building Code MCP Server

A Model Context Protocol (MCP) server that provides search and navigation capabilities for Canadian building codes.

## Overview

This tool helps professionals navigate Canadian building codes by providing:
- **Keyword search** across code sections
- **Section lookup** by ID (e.g., "9.10.14.1")
- **Hierarchy navigation** (parent, children, siblings)
- **BYOD Mode**: Connect your own PDF for full text extraction

## Supported Codes

| Code | Version | Description |
|------|---------|-------------|
| NBC | 2025 | National Building Code |
| NPC | 2025 | National Plumbing Code |
| NFC | 2025 | National Fire Code |
| NECB | 2025 | National Energy Code for Buildings |
| OBC | 2024 | Ontario Building Code |
| BCBC | 2024 | British Columbia Building Code |
| ABC | 2023 | Alberta Building Code |

## Installation

\`\`\`bash
pip install mcp pymupdf
\`\`\`

## Usage

### As MCP Server

Add to your Claude Desktop config:

\`\`\`json
{
  "mcpServers": {
    "building-code": {
      "command": "python",
      "args": ["path/to/src/mcp_server.py"]
    }
  }
}
\`\`\`

### Available Tools

#### \`list_codes\`
List all available building codes and their status.

#### \`search_code\`
Search building code sections by keywords.
\`\`\`
search_code("fire separation garage", code="NBC")
\`\`\`

#### \`get_section\`
Get details of a specific section by ID.
\`\`\`
get_section(id="9.10.14.1", code="NBC")
\`\`\`

#### \`get_hierarchy\`
Get parent, children, and siblings of a section.
\`\`\`
get_hierarchy(id="9.10.14", code="NBC")
\`\`\`

#### \`set_pdf_path\` (BYOD Mode)
Connect your own PDF file for full text extraction.
\`\`\`
set_pdf_path(code="NBC", path="C:/codes/NBC2025.pdf")
\`\`\`

## How It Works

### Mode A: Map Only (Default)
Returns structural metadata: section ID, title, page number, and keywords.
This mode works without any PDF files.

### Mode B: BYOD (Bring Your Own Document)
When you connect your legally obtained PDF copy:
1. The server verifies the PDF version using hash comparison
2. Uses stored coordinates to extract actual text from specific sections
3. Returns both metadata and full text content

## Project Structure

\`\`\`
building_code_mcp/
├── maps/               # Structural index files (JSON)
├── src/
│   └── mcp_server.py   # MCP server implementation
├── scripts/
│   ├── convert_with_docling.py  # PDF conversion tool
│   └── generate_map.py          # Map generation tool
└── README.md
\`\`\`

## For Developers

### Creating Maps for New Codes

1. Convert PDF with Docling:
\`\`\`bash
python scripts/convert_with_docling.py path/to/code.pdf
\`\`\`

2. Generate map:
\`\`\`bash
python scripts/generate_map.py docling_output/code_name/
\`\`\`

### Map JSON Schema

\`\`\`json
{
  "code": "NBC",
  "version": "2025",
  "source_pdf": {
    "md5": "abc123...",
    "page_count": 1200
  },
  "sections": [
    {
      "id": "9.10.14.1",
      "title": "Fire Separations Required",
      "page": 892,
      "level": "article",
      "parent_id": "9.10.14",
      "keywords": ["fire", "separation", "dwelling", "garage"],
      "bbox": {"l": 72, "t": 120, "r": 540, "b": 680}
    }
  ]
}
\`\`\`

## Disclaimer

This is a structural index for Canadian Building Codes. It helps you navigate your legally obtained copy of the code. No copyrighted text is distributed with this tool. This is not an official NRC or government product.

The building codes themselves are published by the National Research Council of Canada (NRC) and provincial authorities. Please obtain official copies through proper channels.

## License

MIT License - See [LICENSE](LICENSE) file.
