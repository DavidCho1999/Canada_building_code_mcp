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
from mcp.types import (
    Tool, TextContent, ToolAnnotations,
    Prompt, PromptArgument, PromptMessage, GetPromptResult,
    Resource
)
from mcp.server.stdio import stdio_server

# For PDF text extraction (BYOD mode)
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# For fuzzy search (typo tolerance)
try:
    from rapidfuzz import fuzz, process
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False

# Building code synonyms for better search
SYNONYMS = {
    "restroom": ["washroom", "water closet", "toilet", "lavatory", "bathroom"],
    "washroom": ["restroom", "water closet", "toilet", "lavatory", "bathroom"],
    "stairs": ["stairway", "staircase", "stair"],
    "stairway": ["stairs", "staircase", "stair"],
    "exit": ["egress", "means of egress"],
    "egress": ["exit", "means of egress"],
    "fire": ["fire resistance", "fire separation", "fire-resistance"],
    "garage": ["parking garage", "parking structure", "carport"],
    "window": ["glazing", "fenestration"],
    "door": ["doorway", "entrance"],
    "wall": ["partition", "barrier"],
    "ceiling": ["soffit"],
    "floor": ["storey", "story"],
    "storey": ["floor", "story"],
    "handicap": ["accessible", "accessibility", "barrier-free"],
    "accessible": ["handicap", "accessibility", "barrier-free"],
    "ramp": ["slope", "incline"],
    "handrail": ["guardrail", "railing", "guard"],
    "guardrail": ["handrail", "railing", "guard"],
}


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
        # Separate codes from guides based on document_type
        codes_list = []
        guides_list = []

        for code, data in self.maps.items():
            doc_type = data.get("document_type", "code")
            code_info = {
                "code": code,
                "version": data.get("version", "unknown"),
                "sections": len(data.get("sections", [])),
                "document_type": doc_type,
                "searchable": True,
                "pdf_connected": code in self.pdf_paths
            }
            # Add download link if available
            if code in PDF_DOWNLOAD_LINKS:
                link_info = PDF_DOWNLOAD_LINKS[code]
                code_info["download_url"] = link_info["url"]
                code_info["source"] = link_info["source"]
                code_info["free"] = link_info.get("free", True)

            if doc_type == "guide":
                code_info["note"] = "Interpretation guide - NOT legally binding"
                guides_list.append(code_info)
            else:
                codes_list.append(code_info)

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
            "codes": codes_list,
            "guides": guides_list,
            "web_references": web_references,
            "total_codes": len(codes_list),
            "total_guides": len(guides_list),
            "total_web": len(web_references)
        }

    def _expand_query_with_synonyms(self, query_terms: set) -> set:
        """Expand query terms with synonyms."""
        expanded = set(query_terms)
        for term in query_terms:
            if term in SYNONYMS:
                expanded.update(SYNONYMS[term])
        return expanded

    def _fuzzy_match_score(self, query_term: str, target_terms: set, threshold: int = 80) -> float:
        """Calculate fuzzy match score for a query term against target terms."""
        if not FUZZY_AVAILABLE or not target_terms:
            return 0.0

        # Find best fuzzy match
        best_score = 0
        for target in target_terms:
            ratio = fuzz.ratio(query_term, target)
            if ratio > best_score:
                best_score = ratio

        # Return normalized score if above threshold
        if best_score >= threshold:
            return best_score / 100.0
        return 0.0

    def search_code(self, query: str, code: Optional[str] = None) -> Dict:
        """Search for sections matching query with fuzzy matching and synonym support."""
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
        # Expand with synonyms
        expanded_terms = self._expand_query_with_synonyms(query_terms)

        maps_to_search = {code: self.maps[code]} if code and code in self.maps else self.maps

        for code_name, data in maps_to_search.items():
            doc_type = data.get("document_type", "code")
            for section in data.get("sections", []):
                section_id = section.get("id", "")
                title = section.get("title", "")
                keywords = set(kw.lower() for kw in section.get('keywords', []))
                title_words = set(title.lower().split())
                all_terms = keywords | title_words

                # Score calculation
                score = 0.0
                match_type = None

                # 1. Section ID exact/partial match (highest priority)
                if query_lower in section_id.lower():
                    score = 2.0 if section_id.lower().endswith(query_lower) else 1.5
                    match_type = "exact_id"

                # 2. Exact keyword/title word matches (including synonyms)
                elif expanded_terms:
                    matches = expanded_terms & all_terms
                    if matches:
                        # Boost if original terms matched (not just synonyms)
                        original_matches = query_terms & all_terms
                        if original_matches:
                            score = len(original_matches) / len(query_terms)
                            match_type = "exact"
                        else:
                            # Synonym match - slightly lower score
                            score = (len(matches) / len(expanded_terms)) * 0.9
                            match_type = "synonym"

                # 3. Fuzzy matching (typo tolerance) - only if no exact match
                if score == 0 and FUZZY_AVAILABLE:
                    fuzzy_scores = []
                    for term in query_terms:
                        fscore = self._fuzzy_match_score(term, all_terms)
                        if fscore > 0:
                            fuzzy_scores.append(fscore)

                    if fuzzy_scores:
                        score = (sum(fuzzy_scores) / len(query_terms)) * 0.8  # Fuzzy gets lower weight
                        match_type = "fuzzy"

                if score > 0:
                    # Boost tables slightly to ensure they appear in results
                    if section.get("type") == "table":
                        score += 0.01

                    result_item = {
                        "code": code_name,
                        "id": section_id,
                        "title": title,
                        "page": section.get("page"),
                        "score": round(score, 3),
                        "document_type": doc_type
                    }
                    # Include type and level for tables
                    if section.get("type"):
                        result_item["type"] = section.get("type")
                    if section.get("level"):
                        result_item["level"] = section.get("level")
                    # Include page_end for multi-page tables
                    if section.get("page_end"):
                        result_item["page_end"] = section.get("page_end")
                    if match_type:
                        result_item["match_type"] = match_type
                    # Add warning for guides
                    if doc_type == "guide":
                        result_item["note"] = "Interpretation guide - NOT legally binding"
                    results.append(result_item)

        results.sort(key=lambda x: x["score"], reverse=True)

        response = {"query": query, "results": results[:20], "total": len(results)}
        # Add search enhancement info
        if FUZZY_AVAILABLE:
            response["search_features"] = ["synonyms", "fuzzy_matching"]
        else:
            response["search_features"] = ["synonyms"]

        return response

    def get_section(self, section_id: str, code: str) -> Optional[Dict]:
        """Get a specific section by ID."""
        if code not in self.maps:
            return {"error": f"Code not found: {code}", "disclaimer": DISCLAIMER}

        data = self.maps[code]
        version = data.get("version", "unknown")
        doc_type = data.get("document_type", "code")

        # Try exact match first, then try with Division prefixes
        search_ids = [section_id]
        # If no prefix, try adding common Division prefixes
        if not section_id.startswith(('A-', 'B-', 'C-', 'Commentary-', 'Part')):
            search_ids.extend([f'A-{section_id}', f'B-{section_id}', f'C-{section_id}'])

        for section in data.get("sections", []):
            if section.get("id") in search_ids:
                result = dict(section)
                actual_id = section.get("id")
                result["code"] = code
                result["version"] = version
                result["document_type"] = doc_type

                # Note if we found it with a different prefix
                if actual_id != section_id:
                    result["note"] = f"Found as '{actual_id}' (you searched for '{section_id}')"

                # Add formal citation
                page = section.get("page")
                result["citation"] = f"{code} {version}, Section {actual_id}" + (f", Page {page}" if page else "")
                result["citation_short"] = f"{code} {version}, s. {actual_id}"

                # Add warning for guides
                if doc_type == "guide":
                    result["warning"] = "This is an interpretation guide - NOT legally binding. Always cite the actual code section."

                # BYOD: Extract text if PDF connected
                if code in self.pdf_paths and self.pdf_verified.get(code):
                    text = self._extract_text(code, section)
                    if text:
                        result["text"] = text
                        result["text_available"] = True
                    else:
                        result["text"] = None
                        result["text_available"] = False
                        result["text_error"] = "Could not extract text from PDF"
                else:
                    # PDF not connected - provide guidance
                    result["text"] = None
                    result["text_available"] = False
                    if code in self.pdf_paths and not self.pdf_verified.get(code):
                        result["text_status"] = "PDF connected but version mismatch detected"
                    else:
                        result["text_status"] = "PDF not connected"

                    # Provide download link if available
                    if code in PDF_DOWNLOAD_LINKS:
                        link = PDF_DOWNLOAD_LINKS[code]
                        result["how_to_get_text"] = (
                            f"1. Download PDF from: {link['url']}\n"
                            f"2. Use set_pdf_path('{code}', '/path/to/your.pdf') to connect"
                        )
                    else:
                        result["how_to_get_text"] = f"Use set_pdf_path('{code}', '/path/to/your.pdf') to enable text extraction"

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

        # Try exact match first, then try with Division prefixes
        search_ids = [section_id]
        if not section_id.startswith(('A-', 'B-', 'C-', 'Commentary-', 'Part')):
            search_ids.extend([f'A-{section_id}', f'B-{section_id}', f'C-{section_id}'])

        for section in data.get("sections", []):
            if section.get("id") in search_ids:
                actual_id = section.get("id")
                page = section.get("page")
                title = section.get("title", "")

                # Build formal citation
                citation = f"{code} {version}, Section {actual_id}"
                if page:
                    citation += f", Page {page}"

                result = {
                    "exists": True,
                    "section_id": actual_id,
                    "code": code,
                    "version": version,
                    "title": title,
                    "page": page,
                    "citation": citation,
                    "citation_format": f"{code} {version}, s. {actual_id}" + (f", p. {page}" if page else ""),
                    "disclaimer": DISCLAIMER
                }
                # Note if found with different prefix
                if actual_id != section_id:
                    result["note"] = f"Found as '{actual_id}' (you searched for '{section_id}')"
                return result

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

    def get_table(self, table_id: str, code: Optional[str] = None) -> Dict:
        """
        Get a specific table by ID with markdown content.

        Args:
            table_id: Table ID (e.g., "Table-4.1.5.3", "4.1.5.3")
            code: Optional code name (e.g., "NBC")

        Returns:
            Table data with markdown content
        """
        if not table_id:
            return {"error": "Table ID is required"}

        # Normalize table ID
        if not table_id.startswith("Table-"):
            table_id = f"Table-{table_id}"

        # Search in specified code or all codes
        codes_to_search = [code] if code and code in self.maps else list(self.maps.keys())

        for code_name in codes_to_search:
            data = self.maps.get(code_name, {})
            tables = data.get("tables", [])

            for table in tables:
                if table.get("id") == table_id:
                    version = data.get("version", "unknown")
                    return {
                        "id": table_id,
                        "code": code_name,
                        "version": version,
                        "title": table.get("title", ""),
                        "page": table.get("page"),
                        "table_info": table.get("table_info", {}),
                        "markdown": table.get("markdown", ""),
                        "keywords": table.get("keywords", []),
                        "citation": f"{code_name} {version}, {table.get('title', table_id)}",
                        "disclaimer": DISCLAIMER
                    }

        return {
            "error": f"Table {table_id} not found",
            "suggestion": "Use search_code to find tables, e.g., search_code('Table 4.1.5.3', 'NBC')",
            "note": "Table IDs follow pattern: Table-X.X.X.X or Table-X.X.X.X-A"
        }

    def get_page(self, code: str, page: int) -> Dict:
        """
        Get full text content of a specific page.

        Args:
            code: Code name (e.g., "NBC")
            page: Page number

        Returns:
            Page text content
        """
        if not code or code not in self.maps:
            return {"error": f"Code not found: {code}"}

        if not PYMUPDF_AVAILABLE:
            return {
                "error": "PDF text extraction not available",
                "suggestion": "Install PyMuPDF: pip install pymupdf"
            }

        pdf_path = self.pdf_paths.get(code)
        if not pdf_path:
            return {
                "error": f"PDF not connected for {code}",
                "suggestion": f"Use set_pdf_path('{code}', '/path/to/pdf') first"
            }

        try:
            doc = fitz.open(pdf_path)
            if page <= 0 or page > len(doc):
                return {
                    "error": f"Invalid page number: {page}",
                    "total_pages": len(doc)
                }

            page_obj = doc[page - 1]
            text = page_obj.get_text()
            doc.close()

            # Limit text length
            max_chars = 3000
            truncated = len(text) > max_chars

            return {
                "code": code,
                "page": page,
                "text": text[:max_chars],
                "truncated": truncated,
                "char_count": len(text),
                "disclaimer": DISCLAIMER
            }
        except Exception as e:
            return {"error": f"Failed to read page: {str(e)}"}

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
            description="List all available Canadian building codes and user guides with section counts, versions, and download links. Returns codes (legally binding) and guides (interpretation only) separately.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            },
            annotations=ToolAnnotations(
                title="List Building Codes",
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False
            )
        ),
        Tool(
            name="search_code",
            description="Search building code sections by keywords across all codes or a specific code. Returns matching sections with page numbers, section IDs, and relevance scores.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keywords to search for (e.g., 'fire separation', 'stair width', 'egress requirements')"
                    },
                    "code": {
                        "type": "string",
                        "description": "Optional: Specific code to search (e.g., 'NBC', 'OBC', 'BCBC'). If omitted, searches all codes."
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            },
            annotations=ToolAnnotations(
                title="Search Building Code",
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False
            )
        ),
        Tool(
            name="get_section",
            description="Get detailed information about a specific section by its ID. Returns page number, coordinates, keywords, and hierarchy info. Auto-detects Division prefix (A/B/C) if not provided.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Section ID to retrieve (e.g., '9.10.14.1', '3.2.4.1', 'B-9.10.14.1'). Division prefix is auto-detected if omitted."
                    },
                    "code": {
                        "type": "string",
                        "description": "Code name (e.g., 'NBC', 'OBC', 'BCBC', 'ABC', 'QCC')"
                    }
                },
                "required": ["id", "code"],
                "additionalProperties": False
            },
            annotations=ToolAnnotations(
                title="Get Section Details",
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False
            )
        ),
        Tool(
            name="get_hierarchy",
            description="Navigate the code structure by getting parent, children, and sibling sections. Useful for understanding context and finding related requirements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Section ID to get hierarchy for (e.g., '9.9' to see all stair subsections)"
                    },
                    "code": {
                        "type": "string",
                        "description": "Code name (e.g., 'NBC', 'OBC')"
                    }
                },
                "required": ["id", "code"],
                "additionalProperties": False
            },
            annotations=ToolAnnotations(
                title="Get Section Hierarchy",
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False
            )
        ),
        Tool(
            name="set_pdf_path",
            description="Connect your legally obtained PDF file for full text extraction (BYOD mode). Once connected, get_section will return actual code text, not just coordinates.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code name to connect PDF for (e.g., 'NBC', 'OBC')"
                    },
                    "path": {
                        "type": "string",
                        "description": "Absolute path to your PDF file (e.g., 'C:/codes/NBC2025.pdf' or '/home/user/codes/NBC2025.pdf')"
                    }
                },
                "required": ["code", "path"],
                "additionalProperties": False
            },
            annotations=ToolAnnotations(
                title="Connect PDF File",
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False
            )
        ),
        Tool(
            name="verify_section",
            description="Verify that a section ID exists and get a formal citation. Use this to prevent hallucination by confirming section references are valid before citing them.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Section ID to verify (e.g., '9.10.14.1'). Division prefix is auto-detected if omitted."
                    },
                    "code": {
                        "type": "string",
                        "description": "Code name to verify against (e.g., 'NBC', 'OBC')"
                    }
                },
                "required": ["id", "code"],
                "additionalProperties": False
            },
            annotations=ToolAnnotations(
                title="Verify Section Exists",
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False
            )
        ),
        Tool(
            name="get_applicable_code",
            description="Determine which building codes apply to a specific location in Canada. Returns applicable provincial and national codes with notes about jurisdiction.",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Canadian location (city, province, or territory). Examples: 'Toronto', 'Vancouver', 'Montreal', 'British Columbia', 'Alberta'"
                    }
                },
                "required": ["location"],
                "additionalProperties": False
            },
            annotations=ToolAnnotations(
                title="Get Applicable Code by Location",
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False
            )
        ),
        Tool(
            name="get_table",
            description="Get a specific table from the building code with full markdown content. Use this for tables like 'Table 4.1.5.3' (live loads), 'Table 9.10.14.4' (spatial separation), etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "Table ID (e.g., '4.1.5.3', 'Table-4.1.5.3', '9.10.14.4-A')"
                    },
                    "code": {
                        "type": "string",
                        "description": "Optional: Code name (e.g., 'NBC', 'OBC'). If omitted, searches all codes."
                    }
                },
                "required": ["table_id"],
                "additionalProperties": False
            },
            annotations=ToolAnnotations(
                title="Get Table Content",
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False
            )
        ),
        Tool(
            name="get_page",
            description="Get full text content of a specific page. Requires PDF to be connected via set_pdf_path. Use this when you need to see all content on a page, not just a specific section.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code name (e.g., 'NBC', 'OBC')"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number to retrieve"
                    }
                },
                "required": ["code", "page"],
                "additionalProperties": False
            },
            annotations=ToolAnnotations(
                title="Get Page Content",
                readOnlyHint=True,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False
            )
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
    elif name == "get_table":
        result = mcp.get_table(arguments.get("table_id", ""), arguments.get("code"))
    elif name == "get_page":
        result = mcp.get_page(arguments.get("code", ""), arguments.get("page", 0))
    else:
        result = {"error": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


# ============================================
# PROMPTS - Reusable templates for LLM interactions
# ============================================

@server.list_prompts()
async def list_prompts() -> List[Prompt]:
    """List available prompts for building code interactions."""
    return [
        Prompt(
            name="search_building_code",
            description="Search Canadian building codes for specific requirements or regulations",
            arguments=[
                PromptArgument(
                    name="query",
                    description="What to search for (e.g., 'fire separation requirements', 'stair dimensions')",
                    required=True
                ),
                PromptArgument(
                    name="code",
                    description="Specific code to search (NBC, OBC, BCBC, etc.) or leave empty for all",
                    required=False
                )
            ]
        ),
        Prompt(
            name="verify_code_reference",
            description="Verify a building code section exists before citing it (prevents hallucination)",
            arguments=[
                PromptArgument(
                    name="section_id",
                    description="Section ID to verify (e.g., '9.10.14.1', '3.2.4.1')",
                    required=True
                ),
                PromptArgument(
                    name="code",
                    description="Code name (NBC, OBC, BCBC, etc.)",
                    required=True
                )
            ]
        ),
        Prompt(
            name="find_applicable_code",
            description="Determine which building codes apply to a specific Canadian location",
            arguments=[
                PromptArgument(
                    name="location",
                    description="City, province, or territory (e.g., 'Toronto', 'Vancouver', 'Alberta')",
                    required=True
                )
            ]
        ),
        Prompt(
            name="explore_code_structure",
            description="Navigate and explore the hierarchy of a building code section",
            arguments=[
                PromptArgument(
                    name="section_id",
                    description="Section ID to explore (e.g., '9.9' for stairs)",
                    required=True
                ),
                PromptArgument(
                    name="code",
                    description="Code name (NBC, OBC, BCBC, etc.)",
                    required=True
                )
            ]
        )
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: Optional[Dict[str, str]] = None) -> GetPromptResult:
    """Get a specific prompt with arguments filled in."""
    args = arguments or {}

    if name == "search_building_code":
        query = args.get("query", "building requirements")
        code = args.get("code", "")
        code_text = f" in {code}" if code else " across all Canadian building codes"
        return GetPromptResult(
            description=f"Search for '{query}'{code_text}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Please search for '{query}'{code_text}. Use the search_code tool to find relevant sections, then use get_section to get details on the most relevant results."
                    )
                )
            ]
        )

    elif name == "verify_code_reference":
        section_id = args.get("section_id", "")
        code = args.get("code", "")
        return GetPromptResult(
            description=f"Verify section {section_id} in {code}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Before citing section {section_id} from {code}, please verify it exists using the verify_section tool. If it exists, provide the formal citation. If not, suggest similar sections that do exist."
                    )
                )
            ]
        )

    elif name == "find_applicable_code":
        location = args.get("location", "")
        return GetPromptResult(
            description=f"Find applicable codes for {location}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"What building codes apply to construction projects in {location}, Canada? Use the get_applicable_code tool to determine the primary and secondary codes that apply to this jurisdiction."
                    )
                )
            ]
        )

    elif name == "explore_code_structure":
        section_id = args.get("section_id", "")
        code = args.get("code", "")
        return GetPromptResult(
            description=f"Explore structure of {section_id} in {code}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Please explore the structure of section {section_id} in {code}. Use get_hierarchy to show the parent section, all child subsections, and sibling sections. This helps understand the context and related requirements."
                    )
                )
            ]
        )

    else:
        raise ValueError(f"Unknown prompt: {name}")


# ============================================
# RESOURCES - Data entities exposed by the server
# ============================================

@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources."""
    mcp = get_mcp()
    resources = [
        Resource(
            uri="buildingcode://welcome",
            name="Getting Started",
            description="Introduction, legal info, and setup guide for Canada Building Code MCP",
            mimeType="application/json"
        ),
        Resource(
            uri="buildingcode://codes",
            name="Available Building Codes",
            description="List of all available Canadian building codes with section counts and download links",
            mimeType="application/json"
        ),
        Resource(
            uri="buildingcode://stats",
            name="Server Statistics",
            description="Statistics about indexed building codes and sections",
            mimeType="application/json"
        )
    ]

    # Add each code as a resource
    for code in mcp.maps.keys():
        data = mcp.maps[code]
        doc_type = data.get("document_type", "code")
        version = data.get("version", "unknown")
        sections = len(data.get("sections", []))
        resources.append(Resource(
            uri=f"buildingcode://code/{code}",
            name=f"{code} {version}",
            description=f"{'Guide' if doc_type == 'guide' else 'Building Code'} with {sections} indexed sections",
            mimeType="application/json"
        ))

    return resources


@server.read_resource()
async def read_resource(uri) -> str:
    """Read a specific resource."""
    mcp = get_mcp()

    # Convert AnyUrl to string
    uri_str = str(uri)

    if uri_str == "buildingcode://welcome":
        welcome = {
            "title": "Canada Building Code MCP - Getting Started",
            "legal_notice": {
                "status": "100% Copyright Safe",
                "explanation": "This MCP only provides coordinates (page numbers, bounding boxes, section IDs). No copyrighted text is distributed. You must obtain the PDF yourself from official sources."
            },
            "how_it_works": {
                "mode_a_map_only": {
                    "description": "Default mode - returns page numbers and coordinates only",
                    "use_case": "When you have the PDF open separately"
                },
                "mode_b_byod": {
                    "description": "Bring Your Own Document - connect YOUR legally obtained PDF",
                    "use_case": "For full text extraction within the MCP",
                    "setup": "Use set_pdf_path tool with your PDF location"
                }
            },
            "recommendation": "For the best experience, download the official PDF (FREE from government sources) and connect it using the set_pdf_path tool.",
            "free_pdf_sources": {
                "National_Codes": "https://nrc-publications.canada.ca (NBC, NFC, NPC, NECB)",
                "Ontario": "https://publications.gov.on.ca (OBC, OFC)",
                "BC": "https://free.bcpublications.ca (BCBC)",
                "Alberta": "https://open.alberta.ca (ABC)",
                "Quebec": "https://www.rbq.gouv.qc.ca (QCC, QECB, QPC, QSC)"
            },
            "quick_start": [
                "1. list_codes - See all available codes (13 codes + 3 guides)",
                "2. search_code - Find sections by keywords",
                "3. get_section - Get page number and coordinates",
                "4. verify_section - Confirm a section exists before citing",
                "5. get_applicable_code - Find which codes apply to a location",
                "6. (Optional) set_pdf_path - Connect your PDF for full text"
            ],
            "total_coverage": "25,000+ sections across 16 documents"
        }
        return json.dumps(welcome, indent=2, ensure_ascii=False)

    elif uri_str == "buildingcode://codes":
        return json.dumps(mcp.list_codes(), indent=2, ensure_ascii=False)

    elif uri_str == "buildingcode://stats":
        total_sections = sum(len(d.get("sections", [])) for d in mcp.maps.values())
        stats = {
            "total_codes": len([c for c, d in mcp.maps.items() if d.get("document_type") != "guide"]),
            "total_guides": len([c for c, d in mcp.maps.items() if d.get("document_type") == "guide"]),
            "total_sections": total_sections,
            "codes": {code: len(data.get("sections", [])) for code, data in mcp.maps.items()}
        }
        return json.dumps(stats, indent=2, ensure_ascii=False)

    elif uri_str.startswith("buildingcode://code/"):
        code = uri_str.replace("buildingcode://code/", "")
        if code in mcp.maps:
            data = mcp.maps[code]
            summary = {
                "code": code,
                "version": data.get("version"),
                "document_type": data.get("document_type", "code"),
                "total_sections": len(data.get("sections", [])),
                "sample_sections": [
                    {"id": s.get("id"), "title": s.get("title"), "page": s.get("page")}
                    for s in data.get("sections", [])[:10]
                ]
            }
            return json.dumps(summary, indent=2, ensure_ascii=False)
        else:
            return json.dumps({"error": f"Code not found: {code}"})

    else:
        return json.dumps({"error": f"Unknown resource: {uri_str}"})


async def _async_main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    """Entry point for the MCP server."""
    import asyncio
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
