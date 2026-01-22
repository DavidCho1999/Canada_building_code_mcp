# Feature: Building Code MCP Server v1.0

## Feature Summary

MCP server implementation enabling search and reference of Canadian Building Codes in Claude Desktop.

## Problem Being Solved

Solving the inefficiency of construction professionals having to manually navigate 1,000+ page Building Code PDFs.

## Proposed Solution

### Core MCP Tools

1. **list_codes**: List supported codes
2. **search_code**: Keyword search
3. **get_section**: Detailed lookup by section ID
4. **get_hierarchy**: Navigate parent/child articles
5. **set_pdf_path**: Connect user's PDF

### Operation Modes

| Mode | Condition | Functionality |
|------|-----------|---------------|
| Map Only | No PDF | Metadata only (ID, page, keywords) |
| BYOD Fast | PDF hash matches | Coordinate-based full text extraction |
| BYOD Slow | PDF hash mismatch | Pattern matching text extraction |

## User Stories

1. As an architect, I want to search codes in natural language so that I can quickly find relevant articles.
2. As an engineer, I want to lookup by section ID so that I can verify exact article content.
3. As an inspector, I want to compare multiple codes so that I can review compliance.

## Success Criteria

- Search accuracy > 90%
- Section coverage > 95%
- Setup time < 5 min
- Search response time < 1 sec
