#!/usr/bin/env python3
"""
Canadian Building Code MCP Server
"""

import json
import hashlib
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# For PDF text extraction (BYOD mode)
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class BuildingCodeMCP:
    """Canadian Building Code MCP Server"""

    def __init__(self, maps_dir: str = "maps"):
        self.maps_dir = Path(maps_dir)
        self.maps: Dict[str, Dict] = {}
        self.pdf_paths: Dict[str, str] = {}
        self.pdf_verified: Dict[str, bool] = {}
        self._load_maps()

    def _load_maps(self):
        """Load all map JSON files."""
        if not self.maps_dir.exists():
            return
        for json_file in self.maps_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    code = data.get('code', json_file.stem)
                    self.maps[code] = data
            except Exception:
                pass

    def list_codes(self) -> Dict:
        """List all available codes."""
        codes = []
        for code, data in self.maps.items():
            codes.append({
                "code": code,
                "version": data.get("version", "unknown"),
                "sections": len(data.get("sections", [])),
                "pdf_connected": code in self.pdf_paths
            })
        return {"codes": codes, "total": len(codes)}

    def search_code(self, query: str, code: Optional[str] = None) -> Dict:
        """Search for sections matching query."""
        results = []
        query_terms = set(query.lower().split())

        maps_to_search = {code: self.maps[code]} if code and code in self.maps else self.maps

        for code_name, data in maps_to_search.items():
            for section in data.get("sections", []):
                keywords = set(kw.lower() for kw in section.get('keywords', []))
                title_words = set(section.get('title', '').lower().split())
                all_terms = keywords | title_words
                matches = query_terms & all_terms

                if matches:
                    results.append({
                        "code": code_name,
                        "id": section.get("id"),
                        "title": section.get("title"),
                        "page": section.get("page"),
                        "score": len(matches) / len(query_terms)
                    })

        results.sort(key=lambda x: x["score"], reverse=True)
        return {"query": query, "results": results[:20], "total": len(results)}

    def get_section(self, section_id: str, code: str) -> Optional[Dict]:
        """Get a specific section by ID."""
        if code not in self.maps:
            return {"error": f"Code not found: {code}"}

        for section in self.maps[code].get("sections", []):
            if section.get("id") == section_id:
                result = dict(section)
                result["code"] = code

                # BYOD: Extract text if PDF connected
                if code in self.pdf_paths and self.pdf_verified.get(code):
                    text = self._extract_text(code, section)
                    if text:
                        result["text"] = text

                return result

        return {"error": f"Section not found: {section_id}"}

    def get_hierarchy(self, section_id: str, code: str) -> Dict:
        """Get parent, children, siblings of a section."""
        if code not in self.maps:
            return {"error": f"Code not found: {code}"}

        sections = self.maps[code].get("sections", [])

        # Find parent
        parts = section_id.split(".")
        parent_id = ".".join(parts[:-1]) if len(parts) > 1 else None
        parent = None
        if parent_id:
            for s in sections:
                if s.get("id") == parent_id:
                    parent = {"id": s["id"], "title": s.get("title")}
                    break

        # Find children
        children = []
        for s in sections:
            sid = s.get("id", "")
            if sid.startswith(section_id + ".") and sid.count(".") == section_id.count(".") + 1:
                children.append({"id": sid, "title": s.get("title")})

        # Find siblings
        siblings = []
        if parent_id:
            for s in sections:
                sid = s.get("id", "")
                if sid.startswith(parent_id + ".") and sid.count(".") == section_id.count(".") and sid != section_id:
                    siblings.append({"id": sid, "title": s.get("title")})

        return {"parent": parent, "children": children, "siblings": siblings}

    def set_pdf_path(self, code: str, path: str) -> Dict:
        """Connect user's PDF for text extraction."""
        if code not in self.maps:
            return {"error": f"Code not found: {code}"}

        path = Path(path)
        if not path.exists():
            return {"error": f"PDF not found: {path}"}

        self.pdf_paths[code] = str(path.absolute())
        self.pdf_verified[code] = True  # Skip hash verification for now

        return {"success": True, "code": code, "path": str(path)}

    def _extract_text(self, code: str, section: Dict) -> Optional[str]:
        """Extract text from PDF."""
        if not PYMUPDF_AVAILABLE:
            return None

        pdf_path = self.pdf_paths.get(code)
        if not pdf_path:
            return None

        try:
            doc = fitz.open(pdf_path)
            page_num = section.get("page", 0)
            if page_num <= 0 or page_num > len(doc):
                return None

            page = doc[page_num - 1]
            bbox = section.get("bbox")

            if bbox:
                page_height = page.rect.height
                # "Read to End of Page" - 헤더 바닥부터 페이지 끝까지
                rect = fitz.Rect(
                    bbox["l"],
                    page_height - bbox["b"],  # 헤더 바닥부터
                    page.rect.width - 50,     # 오른쪽 여백
                    page_height               # 페이지 끝까지
                )
                text = page.get_text(clip=rect)[:800]  # 미리보기 제한
            else:
                text = page.get_text()[:500]

            doc.close()
            return text.strip() if text else None
        except Exception:
            return None


# Create server and instance
server = Server("building-code")
mcp_instance: Optional[BuildingCodeMCP] = None


def get_mcp() -> BuildingCodeMCP:
    global mcp_instance
    if mcp_instance is None:
        maps_dir = Path(__file__).parent.parent / "maps"
        if not maps_dir.exists():
            maps_dir = Path("maps")
        mcp_instance = BuildingCodeMCP(str(maps_dir))
    return mcp_instance


@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="list_codes",
            description="List all available Canadian building codes",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="search_code",
            description="Search building code sections by keywords",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search terms"},
                    "code": {"type": "string", "description": "Code name (optional)"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_section",
            description="Get details of a specific section",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Section ID (e.g., 9.10.14)"},
                    "code": {"type": "string", "description": "Code name (e.g., NBC)"}
                },
                "required": ["id", "code"]
            }
        ),
        Tool(
            name="get_hierarchy",
            description="Get parent, children, siblings of a section",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Section ID"},
                    "code": {"type": "string", "description": "Code name"}
                },
                "required": ["id", "code"]
            }
        ),
        Tool(
            name="set_pdf_path",
            description="Connect your PDF for text extraction (BYOD)",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Code name"},
                    "path": {"type": "string", "description": "PDF file path"}
                },
                "required": ["code", "path"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    mcp = get_mcp()

    if name == "list_codes":
        result = mcp.list_codes()
    elif name == "search_code":
        result = mcp.search_code(arguments.get("query", ""), arguments.get("code"))
    elif name == "get_section":
        result = mcp.get_section(arguments.get("id", ""), arguments.get("code", ""))
    elif name == "get_hierarchy":
        result = mcp.get_hierarchy(arguments.get("id", ""), arguments.get("code", ""))
    elif name == "set_pdf_path":
        result = mcp.set_pdf_path(arguments.get("code", ""), arguments.get("path", ""))
    else:
        result = {"error": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
