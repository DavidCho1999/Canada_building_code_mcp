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


# PDF Download Links (all free)
PDF_DOWNLOAD_LINKS = {
    "NBC": {
        "url": "https://nrc-publications.canada.ca/eng/view/object/?id=adf1ad94-7ea8-4b08-a19f-653ebb7f45f6",
        "source": "NRC",
        "free": True
    },
    "NFC": {
        "url": "https://nrc-publications.canada.ca/eng/view/object/?id=e8a18373-a824-42d5-8823-bfad854c2ebd",
        "source": "NRC",
        "free": True
    },
    "NPC": {
        "url": "https://nrc-publications.canada.ca/eng/view/object/?id=6e7cabf5-d83e-4efd-9a1c-6515fc7cdc71",
        "source": "NRC",
        "free": True
    },
    "NECB": {
        "url": "https://nrc-publications.canada.ca/eng/view/object/?id=0d558a8e-28fe-4b5d-bb73-35b5a3703e8b",
        "source": "NRC",
        "free": True
    },
    "OBC": {
        "url": "https://www.publications.gov.on.ca/browse-catalogues/building-code-and-guides/2024-ontarios-building-code-compendium-updated-to-january-16-2025-two-volume-pdf-set-kit",
        "source": "Publications Ontario",
        "free": True
    },
    "BCBC": {
        "url": "https://www2.gov.bc.ca/gov/content/industry/construction-industry/building-codes-standards/bc-codes/2024-bc-codes",
        "source": "BC Government",
        "free": True
    },
    "ABC": {
        "url": "https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications/national-building-code-2023-alberta-edition",
        "source": "NRC",
        "free": True
    },
    "QCC": {
        "url": "https://nrc-publications.canada.ca/eng/view/object/?id=fbb47c66-fcda-4d5b-a045-882dfa80ab0e",
        "source": "NRC",
        "free": True
    },
    "QECB": {
        "url": "https://nrc-publications.canada.ca/eng/view/object/?id=ad5eaa41-7532-4cbb-9a1e-49c54b25371e",
        "source": "NRC",
        "free": True
    },
    "QPC": {
        "url": "https://nrc-publications.canada.ca/eng/view/object/?id=4931b15f-9344-43b6-a0f3-446b7b25c410",
        "source": "NRC",
        "free": True
    },
    "QSC": {
        "url": "https://nrc-publications.canada.ca/eng/view/object/?id=6a46f33c-2fc3-4d85-8ee7-34e6780e4bf5",
        "source": "NRC",
        "free": True
    },
    "OFC": {
        "url": "https://www.ontario.ca/laws/regulation/070213",
        "source": "Ontario e-Laws",
        "free": True
    },
}

# Jurisdiction to applicable code mapping
JURISDICTION_MAP = {
    # Ontario
    "ontario": {"primary": "OBC", "also_check": ["NBC"], "notes": "OBC is mandatory, NBC for reference"},
    "toronto": {"primary": "OBC", "also_check": ["NBC"], "notes": "OBC is mandatory, NBC for reference"},
    "ottawa": {"primary": "OBC", "also_check": ["NBC"], "notes": "OBC is mandatory, NBC for reference"},
    "mississauga": {"primary": "OBC", "also_check": ["NBC"], "notes": "OBC is mandatory, NBC for reference"},
    # British Columbia
    "british columbia": {"primary": "BCBC", "also_check": ["NBC"], "notes": "BCBC is mandatory"},
    "bc": {"primary": "BCBC", "also_check": ["NBC"], "notes": "BCBC is mandatory"},
    "vancouver": {"primary": "BCBC", "also_check": ["NBC"], "notes": "BCBC is mandatory, check municipal bylaws"},
    "victoria": {"primary": "BCBC", "also_check": ["NBC"], "notes": "BCBC is mandatory"},
    # Alberta
    "alberta": {"primary": "ABC", "also_check": ["NBC"], "notes": "ABC (Alberta Edition) is mandatory"},
    "calgary": {"primary": "ABC", "also_check": ["NBC"], "notes": "ABC is mandatory"},
    "edmonton": {"primary": "ABC", "also_check": ["NBC"], "notes": "ABC is mandatory"},
    # Quebec
    "quebec": {"primary": "QCC", "also_check": ["QPC", "QECB", "QSC"], "notes": "Quebec has separate codes for construction, plumbing, energy, safety"},
    "montreal": {"primary": "QCC", "also_check": ["QPC", "QECB", "QSC"], "notes": "Quebec codes mandatory"},
    "quebec city": {"primary": "QCC", "also_check": ["QPC", "QECB", "QSC"], "notes": "Quebec codes mandatory"},
    # Other provinces (use National codes directly)
    "manitoba": {"primary": "NBC", "also_check": ["NFC", "NPC"], "notes": "Adopts National Codes with amendments"},
    "winnipeg": {"primary": "NBC", "also_check": ["NFC", "NPC"], "notes": "Adopts National Codes"},
    "saskatchewan": {"primary": "NBC", "also_check": ["NFC", "NPC"], "notes": "Adopts National Codes with amendments"},
    "regina": {"primary": "NBC", "also_check": ["NFC", "NPC"], "notes": "Adopts National Codes"},
    "saskatoon": {"primary": "NBC", "also_check": ["NFC", "NPC"], "notes": "Adopts National Codes"},
    "nova scotia": {"primary": "NBC", "also_check": ["NFC", "NPC"], "notes": "Adopts National Codes"},
    "halifax": {"primary": "NBC", "also_check": ["NFC", "NPC"], "notes": "Adopts National Codes"},
    "new brunswick": {"primary": "NBC", "also_check": ["NFC", "NPC"], "notes": "Adopts National Codes"},
    "newfoundland": {"primary": "NBC", "also_check": ["NFC", "NPC"], "notes": "Adopts National Codes"},
    "pei": {"primary": "NBC", "also_check": ["NFC", "NPC"], "notes": "Adopts National Codes"},
    "prince edward island": {"primary": "NBC", "also_check": ["NFC", "NPC"], "notes": "Adopts National Codes"},
    # Territories
    "yukon": {"primary": "NBC", "also_check": ["NFC", "NPC"], "notes": "Adopts National Codes"},
    "northwest territories": {"primary": "NBC", "also_check": ["NFC", "NPC"], "notes": "Adopts National Codes"},
    "nunavut": {"primary": "NBC", "also_check": ["NFC", "NPC"], "notes": "Adopts National Codes"},
}

# Standard disclaimer for all responses
DISCLAIMER = "This tool provides references only. Verify with official documents before use. Not legal or professional advice."

# Web-only references (no searchable index, AI reads directly)
# OFC is now indexed in maps/OFC.json - searchable!
WEB_REFERENCE_CODES = {}


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
        """List all available codes with download links."""
        # Searchable codes (have map index)
        indexed_codes = []
        for code, data in self.maps.items():
            code_info = {
                "code": code,
                "version": data.get("version", "unknown"),
                "sections": len(data.get("sections", [])),
                "searchable": True,
                "pdf_connected": code in self.pdf_paths
            }
            # Add download link if available
            if code in PDF_DOWNLOAD_LINKS:
                link_info = PDF_DOWNLOAD_LINKS[code]
                code_info["download_url"] = link_info["url"]
                code_info["source"] = link_info["source"]
                code_info["free"] = link_info.get("free", True)
            indexed_codes.append(code_info)

        # Web reference codes (no map, AI reads directly)
        web_references = []
        for code, info in WEB_REFERENCE_CODES.items():
            web_references.append({
                "code": code,
                "name": info["name"],
                "version": info["version"],
                "url": info["url"],
                "source": info["source"],
                "searchable": False,
                "note": info["note"]
            })

        return {
            "indexed_codes": indexed_codes,
            "web_references": web_references,
            "total_indexed": len(indexed_codes),
            "total_web": len(web_references)
        }

    def search_code(self, query: str, code: Optional[str] = None) -> Dict:
        """Search for sections matching query."""
        # Input validation
        if not query or not isinstance(query, str):
            return {"error": "Query is required", "query": "", "results": [], "total": 0}

        # Check if code is web-reference only (like OFC)
        if code and code in WEB_REFERENCE_CODES:
            web_info = WEB_REFERENCE_CODES[code]
            return {
                "error": f"{code} is a web reference only (not searchable)",
                "suggestion": f"Read directly from: {web_info['url']}",
                "query": query,
                "results": [],
                "total": 0
            }

        # Return error if specified code doesn't exist
        if code and code not in self.maps:
            return {"error": f"Code not found: {code}", "query": query, "results": [], "total": 0}

        results = []
        query_lower = query.lower().strip()
        if not query_lower:
            return {"error": "Query cannot be empty", "query": query, "results": [], "total": 0}

        query_terms = set(query_lower.split())

        maps_to_search = {code: self.maps[code]} if code and code in self.maps else self.maps

        for code_name, data in maps_to_search.items():
            for section in data.get("sections", []):
                section_id = section.get("id", "")
                title = section.get("title", "")
                keywords = set(kw.lower() for kw in section.get('keywords', []))
                title_words = set(title.lower().split())
                all_terms = keywords | title_words

                # Score calculation
                score = 0.0

                # 1. Section ID exact/partial match (highest priority)
                if query_lower in section_id.lower():
                    score = 2.0 if section_id.lower().endswith(query_lower) else 1.5

                # 2. Keyword/title word matches
                elif query_terms:
                    matches = query_terms & all_terms
                    if matches:
                        score = len(matches) / len(query_terms)

                if score > 0:
                    results.append({
                        "code": code_name,
                        "id": section_id,
                        "title": title,
                        "page": section.get("page"),
                        "score": score
                    })

        results.sort(key=lambda x: x["score"], reverse=True)
        return {"query": query, "results": results[:20], "total": len(results)}

    def get_section(self, section_id: str, code: str) -> Optional[Dict]:
        """Get a specific section by ID."""
        if code not in self.maps:
            return {"error": f"Code not found: {code}", "disclaimer": DISCLAIMER}

        data = self.maps[code]
        version = data.get("version", "unknown")

        for section in data.get("sections", []):
            if section.get("id") == section_id:
                result = dict(section)
                result["code"] = code
                result["version"] = version

                # Add formal citation
                page = section.get("page")
                result["citation"] = f"{code} {version}, Section {section_id}" + (f", Page {page}" if page else "")
                result["citation_short"] = f"{code} {version}, s. {section_id}"

                # BYOD: Extract text if PDF connected
                if code in self.pdf_paths and self.pdf_verified.get(code):
                    text = self._extract_text(code, section)
                    if text:
                        result["text"] = text

                result["disclaimer"] = DISCLAIMER
                return result

        return {"error": f"Section not found: {section_id}", "disclaimer": DISCLAIMER}

    def get_hierarchy(self, section_id: str, code: str) -> Dict:
        """Get parent, children, siblings of a section."""
        # Input validation
        if not section_id or not isinstance(section_id, str):
            return {"error": "Section ID is required"}
        if not code or code not in self.maps:
            return {"error": f"Code not found: {code}"}

        sections = self.maps[code].get("sections", [])

        # Find current section first (to get parent_id field)
        current = None
        for s in sections:
            if s.get("id") == section_id:
                current = s
                break

        # Bug fix: Use parent_id field from section data, not string parsing
        parent = None
        parent_id = current.get("parent_id") if current else None

        # Fallback to string parsing if parent_id field not available
        if not parent_id:
            parts = section_id.split(".")
            parent_id = ".".join(parts[:-1]) if len(parts) > 1 else None

        # Find parent section
        if parent_id:
            for s in sections:
                if s.get("id") == parent_id:
                    parent = {"id": s["id"], "title": s.get("title")}
                    break
            # If parent not in sections, return parent_id info anyway
            if not parent:
                parent = {"id": parent_id, "title": "(not in map)", "note": "Parent section not indexed"}

        # Find children
        children = []
        for s in sections:
            sid = s.get("id", "")
            # Check if this section's parent_id matches current section
            if s.get("parent_id") == section_id:
                children.append({"id": sid, "title": s.get("title")})
            # Fallback: string matching for older maps
            elif sid.startswith(section_id + ".") and sid.count(".") == section_id.count(".") + 1:
                if not any(c["id"] == sid for c in children):
                    children.append({"id": sid, "title": s.get("title")})

        # Find siblings (same parent)
        siblings = []
        if parent_id:
            for s in sections:
                sid = s.get("id", "")
                s_parent = s.get("parent_id")
                # Check by parent_id field
                if s_parent == parent_id and sid != section_id:
                    siblings.append({"id": sid, "title": s.get("title")})
                # Fallback: string matching
                elif not s_parent and sid.startswith(parent_id + ".") and sid.count(".") == section_id.count(".") and sid != section_id:
                    if not any(sib["id"] == sid for sib in siblings):
                        siblings.append({"id": sid, "title": s.get("title")})

        return {"section_id": section_id, "parent": parent, "children": children, "siblings": siblings}

    def set_pdf_path(self, code: str, path: str) -> Dict:
        """Connect user's PDF for text extraction."""
        if not code or code not in self.maps:
            return {"error": f"Code not found: {code}"}

        if not path:
            return {"error": "Path is required"}

        path = Path(path)
        if not path.exists():
            return {"error": f"PDF not found: {path}"}

        # Validate it's a file, not a directory
        if not path.is_file():
            return {"error": f"Path is not a file: {path}"}

        # Validate it's a PDF
        if path.suffix.lower() != '.pdf':
            return {"error": f"File is not a PDF: {path}"}

        # Version verification: check page count
        warning = None
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(str(path))
                pdf_pages = len(doc)
                doc.close()

                # Get max page from map
                sections = self.maps[code].get("sections", [])
                max_map_page = max((s.get("page", 0) for s in sections), default=0)

                if pdf_pages < max_map_page:
                    warning = (
                        f"PDF version mismatch detected! "
                        f"PDF has {pdf_pages} pages, but map references page {max_map_page}. "
                        f"Text extraction may return incorrect content. "
                        f"Please ensure you have the correct PDF version for {code}."
                    )
            except Exception:
                pass  # If check fails, continue anyway

        self.pdf_paths[code] = str(path.absolute())
        self.pdf_verified[code] = warning is None

        result = {"success": True, "code": code, "path": str(path)}
        if warning:
            result["warning"] = warning
            result["verified"] = False
        else:
            result["verified"] = True

        return result

    def verify_section(self, section_id: str, code: str) -> Dict:
        """Verify if a section exists and return its citation."""
        if not section_id or not isinstance(section_id, str):
            return {
                "exists": False,
                "error": "Section ID is required",
                "disclaimer": DISCLAIMER
            }

        if not code or code not in self.maps:
            return {
                "exists": False,
                "error": f"Code not found: {code}",
                "available_codes": list(self.maps.keys()),
                "disclaimer": DISCLAIMER
            }

        data = self.maps[code]
        version = data.get("version", "unknown")

        for section in data.get("sections", []):
            if section.get("id") == section_id:
                page = section.get("page")
                title = section.get("title", "")

                # Build formal citation
                citation = f"{code} {version}, Section {section_id}"
                if page:
                    citation += f", Page {page}"

                return {
                    "exists": True,
                    "section_id": section_id,
                    "code": code,
                    "version": version,
                    "title": title,
                    "page": page,
                    "citation": citation,
                    "citation_format": f"{code} {version}, s. {section_id}" + (f", p. {page}" if page else ""),
                    "disclaimer": DISCLAIMER
                }

        # Section not found - suggest similar sections
        similar = []
        section_prefix = section_id.rsplit(".", 1)[0] if "." in section_id else section_id
        for section in data.get("sections", []):
            sid = section.get("id", "")
            if sid.startswith(section_prefix):
                similar.append(sid)
                if len(similar) >= 5:
                    break

        return {
            "exists": False,
            "section_id": section_id,
            "code": code,
            "version": version,
            "error": f"Section {section_id} not found in {code}",
            "similar_sections": similar,
            "suggestion": "Check the section number or use search_code to find the correct section",
            "disclaimer": DISCLAIMER
        }

    def get_applicable_code(self, location: str) -> Dict:
        """Get applicable building codes for a location."""
        if not location or not isinstance(location, str):
            return {
                "error": "Location is required",
                "example": "get_applicable_code('Toronto')",
                "disclaimer": DISCLAIMER
            }

        location_lower = location.lower().strip()

        # Direct match
        if location_lower in JURISDICTION_MAP:
            info = JURISDICTION_MAP[location_lower]
            primary_code = info["primary"]

            # Get version info if we have the map
            primary_version = "unknown"
            if primary_code in self.maps:
                primary_version = self.maps[primary_code].get("version", "unknown")

            also_check_info = []
            for code in info["also_check"]:
                version = self.maps[code].get("version", "unknown") if code in self.maps else "unknown"
                also_check_info.append({"code": code, "version": version})

            return {
                "location": location,
                "primary_code": primary_code,
                "primary_version": primary_version,
                "also_check": also_check_info,
                "notes": info["notes"],
                "warning": "Always verify with local Authority Having Jurisdiction (AHJ)",
                "disclaimer": DISCLAIMER
            }

        # Fuzzy match - check if location contains a known jurisdiction
        for jurisdiction, info in JURISDICTION_MAP.items():
            if jurisdiction in location_lower or location_lower in jurisdiction:
                return {
                    "location": location,
                    "matched_jurisdiction": jurisdiction,
                    "primary_code": info["primary"],
                    "also_check": info["also_check"],
                    "notes": info["notes"],
                    "warning": "Partial match - verify with local Authority Having Jurisdiction (AHJ)",
                    "disclaimer": DISCLAIMER
                }

        # Unknown location - default to National codes
        return {
            "location": location,
            "error": "Location not in database",
            "suggestion": "For unknown Canadian locations, start with National Codes",
            "default_codes": ["NBC", "NFC", "NPC", "NECB"],
            "warning": "Contact local Authority Having Jurisdiction (AHJ) to confirm applicable codes",
            "available_jurisdictions": list(set(JURISDICTION_MAP.keys())),
            "disclaimer": DISCLAIMER
        }

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
        Tool(
            name="verify_section",
            description="Verify if a section exists and get its formal citation (use this to prevent hallucination)",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Section ID to verify (e.g., 9.10.14.1)"},
                    "code": {"type": "string", "description": "Code name (e.g., NBC, OBC)"}
                },
                "required": ["id", "code"]
            }
        ),
        Tool(
            name="get_applicable_code",
            description="Get which building codes apply to a Canadian location (city, province, or territory)",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "Location name (e.g., Toronto, British Columbia, Calgary)"}
                },
                "required": ["location"]
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
    elif name == "verify_section":
        result = mcp.verify_section(arguments.get("id", ""), arguments.get("code", ""))
    elif name == "get_applicable_code":
        result = mcp.get_applicable_code(arguments.get("location", ""))
    else:
        result = {"error": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
