# 05. User Guide

## Overview

Canadian Building Code MCP is a tool that enables Claude to directly search and reference Canadian building codes.

**Features:**
- Runs locally (no data sent externally)
- Extracts directly from user's legally obtained PDF
- Fast search (< 1 second)
- Hallucination prevention (verify_section tool)
- Jurisdiction guidance (get_applicable_code tool)

## Available Tools (7)

| Tool | Description |
|------|-------------|
| `list_codes` | List all available codes with download links |
| `search_code` | Search sections by keywords |
| `get_section` | Get details of a specific section |
| `get_hierarchy` | Get parent/children/siblings of a section |
| `set_pdf_path` | Connect your PDF for text extraction (BYOD) |
| `verify_section` | Verify section exists + get formal citation |
| `get_applicable_code` | Get which codes apply to a location |

---

## Installation Requirements

### System Requirements

```
- Python 3.10 or higher
- Storage: 500MB (PDF + DB)
- OS: Windows, macOS, Linux
```

### Required Software

```bash
# Python packages
pip install mcp pymupdf

# Optional: for development/testing
pip install pytest
```

---

## Quick Start

### Step 1: Download MCP

```bash
# Clone from GitHub
git clone https://github.com/username/canadian-building-code-mcp.git
cd canadian-building-code-mcp
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Prepare PDF

**Ontario Building Code:**
1. Visit https://www.ontario.ca/form/get-2024-building-code-compendium-non-commercial-use
2. Fill out form and receive download link
3. Save PDF to `pdfs/` folder

**National Building Code:**
1. Visit https://nrc-publications.canada.ca
2. Search for "National Building Code of Canada"
3. Download free electronic version
4. Save PDF to `pdfs/` folder

### Step 4: Initial Setup

```bash
# Run initial setup (extract text from PDF and create DB)
python setup.py

# Expected output:
# ✓ PDF hash verification complete (OBC 2024)
# ✓ Fast Mode available
# ✓ Extracting text... (about 30 seconds)
# ✓ Database created
# ✓ Search index created
#
# Setup complete! Ready to connect to Claude Desktop.
```

### Step 5: Connect to Claude Desktop

Edit `~/.config/claude/claude_desktop_config.json` (Mac/Linux) or
`%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "building-code": {
      "command": "python",
      "args": ["/path/to/canadian-building-code-mcp/src/server.py"],
      "env": {
        "PDF_PATH": "/path/to/pdfs"
      }
    }
  }
}
```

### Step 6: Test

Restart Claude Desktop and ask:

```
"Tell me the stair width requirements in OBC 9.8.2.1"
```

---

## Usage Examples

### 1. List Available Codes

```
User: "What building codes are available?"
Claude: [calls list_codes tool]

Response:
Indexed codes: 15
- NBC (National Building Code 2025) - 4,213 sections
- OBC (Ontario Building Code 2024) - 3,925 sections
- BCBC (BC Building Code 2024) - 2,645 sections
...

Download links provided for each code.
```

### 2. Search by Keywords

```
User: "Find fire separation requirements"
Claude: [calls search_code tool with query="fire separation"]

Response:
Search results (15 items):
1. B-9.10.9.6 - Fire Separations in Houses (score: 1.0)
2. B-9.10.9.7 - Required Fire Separations (score: 0.9)
3. B-9.10.9.8 - Fire Separation of Service Rooms (score: 0.85)
...
```

### 3. Get Section Details

```
User: "Show me section 9.8.2.1 in OBC"
Claude: [calls get_section tool]

Response:
{
  "id": "B-9.8.2.1",
  "title": "Width",
  "code": "OBC",
  "version": "2024",
  "page": 245,
  "citation": "OBC 2024, Section B-9.8.2.1, Page 245",
  "citation_short": "OBC 2024, s. B-9.8.2.1",
  "disclaimer": "This tool provides references only..."
}
```

### 4. Navigate Hierarchy

```
User: "What are the subsections of 9.8.2?"
Claude: [calls get_hierarchy tool]

Response:
Parent: B-9.8 (Stairs, Ramps, Handrails and Guards)
Children:
- B-9.8.2.1 (Width)
- B-9.8.2.2 (Rise and Run)
- B-9.8.2.3 (Flight Length)
Siblings: B-9.8.1, B-9.8.3, B-9.8.4
```

### 5. Connect PDF for Text Extraction (BYOD)

```
User: "Connect my OBC PDF"
Claude: [calls set_pdf_path tool]

Response:
{
  "success": true,
  "code": "OBC",
  "path": "C:/Users/user/Documents/OBC2024.pdf",
  "verified": true
}

Now get_section will also return actual text content!
```

### 6. Verify Section (Prevent Hallucination)

```
User: "Is section 9.99.99 real in NBC?"
Claude: [calls verify_section tool]

Response:
{
  "exists": false,
  "error": "Section 9.99.99 not found in NBC",
  "similar_sections": ["B-9.9.9.1", "B-9.9.9.2", ...],
  "suggestion": "Check the section number or use search_code"
}
```

### 7. Get Applicable Code for Location

```
User: "What building code applies in Vancouver?"
Claude: [calls get_applicable_code tool]

Response:
{
  "location": "Vancouver",
  "primary_code": "BCBC",
  "primary_version": "2024",
  "also_check": [{"code": "NBC", "version": "2025"}],
  "notes": "BCBC is mandatory, check municipal bylaws",
  "warning": "Always verify with local Authority Having Jurisdiction (AHJ)"
}
```

---

## Troubleshooting

### PDF Hash Mismatch

```
⚠️ PDF hash mismatch
Expected: a1b2c3d4...
Actual: f6e5d4c3...

Switching to Slow Mode. (Takes longer)
```

**Cause:** Using a different version of the PDF

**Solution:**
1. Download latest PDF from official source
2. Or use Slow Mode (95% accuracy)

### Section Not Found

```
❌ Section '9.99.99.99' not found
```

**Cause:** Non-existent section ID

**Solution:**
1. Verify section ID format (e.g., 9.8.2.1)
2. Use search feature to find related sections

### MCP Server Connection Failed

```
❌ Cannot connect to MCP server
```

**Cause:** Config file error or Python path issue

**Solution:**
1. Verify `claude_desktop_config.json` path
2. Use absolute Python path
3. Restart Claude Desktop

---

## Advanced Configuration

### Using Multiple Codes Simultaneously

```json
{
  "mcpServers": {
    "building-code": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "CODES": "OBC,NBC,BCBC",
        "PDF_PATH": "/path/to/pdfs"
      }
    }
  }
}
```

### Cache Settings

```python
# config.py
CACHE_SIZE = 1000      # Number of sections to cache
CACHE_TTL = 3600       # Cache validity time (seconds)
```

### Logging Settings

```python
# config.py
LOG_LEVEL = "INFO"     # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "mcp.log"   # Log file path
```

---

## CLI Commands

### Status Check

```bash
python cli.py status

# Output:
# Building Code MCP Status
# ========================
# OBC 2024: ✓ Configured (Fast Mode)
# NBC 2020: ✓ Configured (Fast Mode)
# BCBC 2024: ✗ PDF not found
#
# Database: 15,234 sections
# Last updated: 2026-01-21
```

### Rebuild Database

```bash
python cli.py rebuild --code OBC

# Use when PDF is updated
```

### Search Test

```bash
python cli.py search "fire separation"

# Test search directly without MCP server
```

---

## For AEC Professionals

### Hallucination Prevention

AI can sometimes generate fake section numbers. Use `verify_section` before citing:

```
BEFORE citing "OBC 9.10.14.5":
1. Call verify_section(id="9.10.14.5", code="OBC")
2. If exists=true → safe to cite
3. If exists=false → check similar_sections or search again
```

### Formal Citations

Every `get_section` response includes:
- `citation`: "OBC 2024, Section B-9.8.2.1, Page 245"
- `citation_short`: "OBC 2024, s. B-9.8.2.1"

Use these in reports, drawings, and permit applications.

### Multi-Province Projects

For projects spanning multiple jurisdictions:
1. Call `get_applicable_code("Toronto")` → OBC
2. Call `get_applicable_code("Vancouver")` → BCBC
3. Compare requirements using `search_code` in both codes

### Disclaimer

All responses include a standard disclaimer:
> "This tool provides references only. Verify with official documents before use. Not legal or professional advice."

Always verify with official PDF and consult with Authority Having Jurisdiction (AHJ).

---

## FAQ

### Q: Do I need an internet connection?

**A:** No. After initial installation, all data is stored locally.
Communication with Claude Desktop is also local.

### Q: Can I distribute the PDF?

**A:** No. Users must download PDFs from official sources themselves.
This MCP only distributes coordinate information; actual text is extracted from user's PDF.

### Q: Does it support other countries' Building Codes?

**A:** Currently only Canadian codes are supported.
The same architecture can be extended to add other codes.

### Q: How do I update?

**A:**
```bash
git pull origin main
pip install -r requirements.txt --upgrade
python setup.py --update
```

### Q: How do I prevent AI from making up section numbers?

**A:** Use the `verify_section` tool before citing any section:
```
verify_section(id="9.10.14.1", code="OBC")
```
This returns `exists: true/false` and provides similar sections if not found.

### Q: Which code applies to my project?

**A:** Use the `get_applicable_code` tool:
```
get_applicable_code("Toronto")  → OBC
get_applicable_code("Vancouver") → BCBC
get_applicable_code("Calgary")   → ABC
```

### Q: Does it work offline?

**A:** Yes, it works completely offline.
Claude Desktop communicates with the local MCP server.

---

## Support & Contributing

### Bug Reports

Report bugs on GitHub Issues:
https://github.com/username/canadian-building-code-mcp/issues

### Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

### License

MIT License - Free to use, modify, and distribute

---

## Legal Notice

```
This tool should only be used for educational and professional reference purposes.

For actual construction projects, always refer to official Building Code documents
and obtain review from the relevant authority.

All copyrights belong to their respective owners:
- Ontario Building Code: © King's Printer for Ontario
- National Building Code: © National Research Council of Canada

This tool only distributes coordinate information;
actual content is extracted from user's legally obtained PDF.
```

---

## Next Steps

1. **Provide Feedback**: Share your usage experience
2. **Contribute**: Add support for new codes
3. **Community**: Join discussions on Discord/Forum
