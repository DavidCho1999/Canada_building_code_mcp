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


# ============================================
# LOGGING - stderr output for MCP Inspector
# ============================================
def _log(message: str):
    """Log to stderr (visible in MCP Inspector, doesn't interfere with protocol)."""
    print(f"[building-code-mcp] {message}", file=sys.stderr)


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

# Version markers for PDF verification
# Check first page for these text patterns to verify correct version
VERSION_MARKERS = {
    "NBC": {
        "page": 0,  # 0-indexed
        "markers": ["National Building", "Code of Canada", "2025"],
        "expected_pages": 1693
    },
    "NFC": {
        "page": 0,
        "markers": ["National Fire", "Code of Canada", "2025"],
        "expected_pages": 352
    },
    "NPC": {
        "page": 0,
        "markers": ["National Plumbing", "Code of Canada", "2025"],
        "expected_pages": 246
    },
    "NECB": {
        "page": 0,
        "markers": ["National Energy", "Code of Canada", "2025"],
        "expected_pages": 350
    },
    "OBC_Vol1": {
        "page": 1,  # Page 0 is blank cover
        "markers": ["Ministry", "Municipal Affairs", "2024"],
        "expected_pages": None  # Variable
    },
    "OBC_Vol2": {
        "page": 1,  # Page 0 is blank cover
        "markers": ["Ministry", "Municipal Affairs", "2024"],
        "expected_pages": None
    },
    "BCBC": {
        "page": 0,
        "markers": ["British Columbia", "BUILDING CODE", "2024"],
        "expected_pages": 1932
    },
    "ABC": {
        "page": 0,
        "markers": ["National Building Code", "2023 Alberta Edition"],
        "expected_pages": 1570
    },
    "QCC": {
        "page": 0,
        "markers": ["BUILDING", "Quebec", "Chapter I"],  # More specific
        "expected_pages": None
    },
    "QECB": {
        "page": 0,
        "markers": ["ENERGY", "Quebec", "Chapter I.1"],  # Chapter I.1 is unique to QECB
        "expected_pages": None
    },
    "QPC": {
        "page": 0,
        "markers": ["PLUMBING", "Quebec", "Chapter III"],  # Chapter III is unique to QPC
        "expected_pages": None
    },
    "QSC": {
        "page": 0,
        "markers": ["FIRE", "Quebec", "Safety Code"],  # FIRE + Safety Code
        "expected_pages": None
    },
    "OFC": {
        "page": 0,
        "markers": ["Ontario", "Fire Code"],
        "expected_pages": None
    },
    "IUGP9": {
        "page": 0,
        "markers": ["Housing and", "Small Buildings", "National Building Code of Canada 2020"],
        "expected_pages": 650
    },
    "UGP4": {
        "page": 0,
        "markers": ["Structural", "Commentaries", "Part 4"],
        "expected_pages": None
    },
    "UGNECB": {
        "page": 0,
        "markers": ["User's Guide", "National Energy Code", "2020"],  # Add year for specificity
        "expected_pages": None
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

    def _add_mode_info(self, result: Dict, code: str) -> Dict:
        """Add mode status information to response."""
        pdf_connected = code in self.pdf_paths
        can_extract = pdf_connected and PYMUPDF_AVAILABLE

        result["mode_info"] = {
            "code": code,
            "mode": "BYOD Active" if pdf_connected else "Map Only",
            "status_icon": "✓" if pdf_connected else "○",
            "showing": "Full text extraction" if can_extract else "Coordinates only"
        }

        # Add suggestion if not connected
        if not pdf_connected:
            tip_parts = ["💡 Want to see actual text?"]

            # Add download link if available
            if code in PDF_DOWNLOAD_LINKS:
                tip_parts.append(f"Download PDF: {PDF_DOWNLOAD_LINKS[code]['url']}")

            # Add usage instruction
            tip_parts.append(f"Then use: set_pdf_path('{code}', 'path/to/pdf')")

            result["mode_info"]["tip"] = " ".join(tip_parts)

        return result

    def list_codes(self, verbose: bool = False) -> Dict:
        """List all available codes with download links.

        Args:
            verbose: If True, include full details. Default False for token efficiency.
        """
        # Separate codes from guides based on document_type
        codes_list = []
        guides_list = []
        codes_compact = []
        guides_compact = []

        for code, data in self.maps.items():
            doc_type = data.get("document_type", "code")
            pdf_connected = code in self.pdf_paths
            can_extract = pdf_connected and PYMUPDF_AVAILABLE

            # Compact info (always needed)
            compact_info = {
                "code": code,
                "sections": len(data.get("sections", [])),
                "status": "BYOD" if pdf_connected else "Map"
            }

            if doc_type == "guide":
                guides_compact.append(compact_info)
            else:
                codes_compact.append(compact_info)

            # Full info (only for verbose mode)
            if verbose:
                code_info = {
                    "code": code,
                    "version": data.get("version", "unknown"),
                    "sections": len(data.get("sections", [])),
                    "document_type": doc_type,
                    "searchable": True,
                    "status": f"{'✓' if pdf_connected else '○'} {'BYOD Active' if pdf_connected else 'Map Only'}",
                    "pdf_connected": pdf_connected,
                    "can_extract_text": can_extract
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

        # Compact response (default) - token efficient
        if not verbose:
            return {
                "codes": codes_compact,
                "guides": guides_compact,
                "total": len(codes_compact) + len(guides_compact),
                "hint": "Use verbose=true for full details including download links"
            }

        # Verbose response - full details
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

        # Calculate summary statistics
        all_items = codes_list + guides_list
        byod_count = sum(1 for item in all_items if item.get("pdf_connected", False))
        map_only_count = len(all_items) - byod_count

        return {
            "codes": codes_list,
            "guides": guides_list,
            "web_references": web_references,
            "total_codes": len(codes_list),
            "total_guides": len(guides_list),
            "total_web": len(web_references),
            "summary": {
                "total": len(all_items),
                "byod_active": byod_count,
                "map_only": map_only_count,
                "pymupdf_installed": PYMUPDF_AVAILABLE
            },
            "modes_explained": {
                "map_only": "○ Provides page numbers and coordinates (legally safe, no text extraction)",
                "byod": "✓ Extract actual text from your own PDFs (requires set_pdf_path)"
            },
            "quick_start": "Use set_pdf_path to connect your PDFs for text extraction"
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

    def _suggest_similar_keywords(self, query: str, code: Optional[str] = None, limit: int = 3) -> List[str]:
        """Find similar keywords when search returns no results (for 'Did you mean?' suggestions)."""
        if not FUZZY_AVAILABLE:
            return []

        # Collect all keywords from relevant codes
        all_keywords = set()
        maps_to_search = {code: self.maps[code]} if code and code in self.maps else self.maps

        for code_name, data in maps_to_search.items():
            for section in data.get("sections", []):
                all_keywords.update(kw.lower() for kw in section.get('keywords', []))

        if not all_keywords:
            return []

        # Find best matches using rapidfuzz
        matches = process.extract(query.lower(), list(all_keywords), limit=limit, score_cutoff=60)
        return [match[0] for match in matches]

    def search_code(self, query: str, code: Optional[str] = None,
                    limit: int = 10, verbose: bool = False) -> Dict:
        """Search for sections matching query with fuzzy matching and synonym support.

        Args:
            query: Search keywords
            code: Optional specific code to search
            limit: Max results to return (default 10, max 50)
            verbose: If True, include keywords, match_type, etc. (default False for token efficiency)
        """
        # Clamp limit
        limit = max(1, min(limit, 50))

        # Log search request
        _log(f"search: query='{query}' code={code} limit={limit}")

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

                    # Compact result (default) - minimal tokens
                    result_item = {
                        "id": section_id,
                        "title": title,
                        "page": section.get("page"),
                        "score": round(score, 3)
                    }

                    # Add code only if searching multiple codes
                    if not code:
                        result_item["code"] = code_name

                    # Verbose mode - include extra metadata
                    if verbose:
                        result_item["document_type"] = doc_type
                        if section.get("type"):
                            result_item["type"] = section.get("type")
                        if section.get("level"):
                            result_item["level"] = section.get("level")
                        if section.get("page_end"):
                            result_item["page_end"] = section.get("page_end")
                        if match_type:
                            result_item["match_type"] = match_type
                        if doc_type == "guide":
                            result_item["note"] = "Guide - NOT legally binding"

                    results.append(result_item)

        results.sort(key=lambda x: x["score"], reverse=True)

        # Apply limit
        limited_results = results[:limit]

        # Compact response (default)
        response = {
            "results": limited_results,
            "total": len(results)
        }

        # Add "Did you mean?" suggestion when no results
        if len(results) == 0:
            similar = self._suggest_similar_keywords(query, code)
            if similar:
                response["suggestion"] = f"No results for '{query}'. Did you mean: {', '.join(similar)}?"
            else:
                response["suggestion"] = f"No results for '{query}'. Try different keywords or check spelling."

        # Add more info only in verbose mode
        if verbose:
            response["query"] = query
            response["search_features"] = ["synonyms", "fuzzy"] if FUZZY_AVAILABLE else ["synonyms"]
            if code:
                response = self._add_mode_info(response, code)
        elif len(results) > limit:
            response["hint"] = f"Showing {limit}/{len(results)}. Use limit param for more."

        # Log search results
        _log(f"search: found {len(results)} results, returning {len(limited_results)}")

        return response

    def get_section(self, section_id: str, code: str, verbose: bool = False) -> Optional[Dict]:
        """Get a specific section by ID.

        Args:
            section_id: Section ID to retrieve
            code: Code name
            verbose: If True, include all metadata. Default False for token efficiency.
        """
        _log(f"get_section: id='{section_id}' code={code}")

        if code not in self.maps:
            return {"error": f"Code not found: {code}"}

        data = self.maps[code]
        version = data.get("version", "unknown")
        doc_type = data.get("document_type", "code")

        # Try exact match first, then try with Division prefixes
        search_ids = [section_id]
        if not section_id.startswith(('A-', 'B-', 'C-', 'Commentary-', 'Part')):
            search_ids.extend([f'A-{section_id}', f'B-{section_id}', f'C-{section_id}'])

        for section in data.get("sections", []):
            if section.get("id") in search_ids:
                actual_id = section.get("id")
                page = section.get("page")

                # Compact result (default) - essential fields only
                result = {
                    "id": actual_id,
                    "title": section.get("title", ""),
                    "page": page,
                    "citation": f"{code} {version}, s. {actual_id}"
                }

                # Add text if PDF connected (always include - it's the main value)
                if code in self.pdf_paths and self.pdf_verified.get(code):
                    text = self._extract_text(code, section)
                    if text:
                        result["text"] = text

                # Verbose mode - include all metadata
                if verbose:
                    result["code"] = code
                    result["version"] = version
                    result["document_type"] = doc_type
                    result["citation_full"] = f"{code} {version}, Section {actual_id}" + (f", Page {page}" if page else "")

                    if actual_id != section_id:
                        result["note"] = f"Found as '{actual_id}'"

                    if section.get("keywords"):
                        result["keywords"] = section.get("keywords")
                    if section.get("bbox"):
                        result["bbox"] = section.get("bbox")

                    if doc_type == "guide":
                        result["warning"] = "Interpretation guide - NOT legally binding"

                    # PDF status info
                    if code not in self.pdf_paths:
                        result["text_status"] = "PDF not connected"
                    elif not self.pdf_verified.get(code):
                        result["text_status"] = "PDF version mismatch"

                    result = self._add_mode_info(result, code)
                    result["disclaimer_ref"] = "buildingcode://disclaimer"

                return result

        return {"error": f"Section not found: {section_id}"}

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

        result = {"section_id": section_id, "parent": parent, "children": children, "siblings": siblings}
        # Add mode info
        result = self._add_mode_info(result, code)
        return result

    def set_pdf_path(self, code: str, path: str) -> Dict:
        """Connect user's PDF for text extraction. If path is a folder, auto-scan for PDFs."""
        _log(f"set_pdf_path: code={code} path='{path}'")

        if not path:
            return {"error": "Path is required"}

        path = Path(path)
        if not path.exists():
            return {"error": f"Path not found: {path}"}

        # If it's a directory, scan for PDFs and auto-match
        if path.is_dir():
            return self._scan_pdf_folder(path, code if code else None)

        # Single file mode - code is required
        if not code or code not in self.maps:
            return {"error": f"Code not found: {code}. Available: {list(self.maps.keys())}"}

        # Validate it's a PDF
        if path.suffix.lower() != '.pdf':
            return {"error": f"File is not a PDF: {path}"}

        # Version verification: check text markers and page count
        warning = None
        version_issues = []

        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(str(path))
                pdf_pages = len(doc)

                # Check 1: Text markers (preferred method)
                if code in VERSION_MARKERS:
                    marker_info = VERSION_MARKERS[code]
                    marker_page = marker_info["page"]
                    expected_markers = marker_info["markers"]

                    # Extract text from the specified page (usually first page)
                    if marker_page < len(doc):
                        page_text = doc[marker_page].get_text()

                        # Check if all markers are present
                        missing_markers = []
                        for marker in expected_markers:
                            if marker not in page_text:
                                missing_markers.append(marker)

                        if missing_markers:
                            version_issues.append(
                                f"Version markers not found: {missing_markers[:2]}. "
                                f"This may not be the correct version of {code}."
                            )

                    # Check 2: Expected page count (if specified)
                    expected_pages = marker_info.get("expected_pages")
                    if expected_pages:
                        page_diff = abs(pdf_pages - expected_pages)
                        if page_diff > 50:  # Allow 50 page tolerance
                            version_issues.append(
                                f"Page count mismatch: PDF has {pdf_pages} pages, "
                                f"expected ~{expected_pages} pages."
                            )

                # Check 3: Fallback - compare with map's max page
                sections = self.maps[code].get("sections", [])
                max_map_page = max((s.get("page", 0) for s in sections), default=0)

                if pdf_pages < max_map_page:
                    version_issues.append(
                        f"PDF has {pdf_pages} pages, but map references page {max_map_page}."
                    )

                doc.close()

                # Combine all issues into warning
                if version_issues:
                    warning = (
                        f"PDF version mismatch detected for {code}:\n" +
                        "\n".join(f"  • {issue}" for issue in version_issues) +
                        f"\n\nText extraction may return incorrect content. "
                        f"Please ensure you have the correct PDF version."
                    )

            except Exception as e:
                # If check fails, continue anyway but note the failure
                warning = f"Could not verify PDF version: {str(e)}"

        self.pdf_paths[code] = str(path.absolute())
        self.pdf_verified[code] = warning is None

        result = {"success": True, "code": code, "path": str(path)}
        if warning:
            result["warning"] = warning
            result["verified"] = False
        else:
            result["verified"] = True

        return result

    def _scan_pdf_folder(self, folder: Path, specific_code: Optional[str] = None) -> Dict:
        """Scan a folder for PDFs and auto-match to codes."""
        # Code name patterns to match in filenames (order matters - more specific first)
        code_patterns = {
            "OBC_Vol2": ["obc_vol2", "obc volume 2", "volume 2", "vol2", "vol 2"],
            "OBC_Vol1": ["obc_vol1", "obc volume 1", "volume 1", "vol1", "vol 1", "obc", "ontario building"],
            "ABC": ["abc", "alberta", "2023nbcae", "nbcae"],
            "NBC": ["nbc", "national building", "nbc2025", "nbc_2025"],
            "NFC": ["nfc", "national fire", "nfc2025"],
            "NPC": ["npc", "national plumbing", "npc2025"],
            "UGNECB": ["ugnecb", "ugnecb_", "energy guide"],
            "NECB": ["necb", "energy code", "necb2025"],
            "OFC": ["ofc", "ontario fire", "o.reg"],
            "BCBC": ["bcbc", "bc building", "british columbia"],
            "QCC": ["qcc", "quebec construction"],
            "QECB": ["qecb", "quebec energy"],
            "QPC": ["qpc", "quebec plumbing"],
            "QSC": ["qsc", "quebec safety"],
            "IUGP9": ["iugp9", "iugp9_", "illustrated guide", "part 9 guide"],
            "UGP4": ["ugp4", "structural comment", "part 4"],
        }

        pdf_files = list(folder.glob("*.pdf"))
        if not pdf_files:
            return {"error": f"No PDF files found in: {folder}"}

        connected = []
        not_matched = []
        errors = []

        for pdf_path in pdf_files:
            filename_lower = pdf_path.stem.lower()
            matched_code = None

            # Try to match filename to a code
            for code, patterns in code_patterns.items():
                if code not in self.maps:
                    continue
                if specific_code and code != specific_code:
                    continue
                for pattern in patterns:
                    if pattern in filename_lower:
                        matched_code = code
                        break
                if matched_code:
                    break

            if matched_code:
                # Connect this PDF
                result = self.set_pdf_path(matched_code, str(pdf_path))
                if result.get("success"):
                    connected.append({
                        "code": matched_code,
                        "file": pdf_path.name,
                        "verified": result.get("verified", False)
                    })
                else:
                    errors.append({"file": pdf_path.name, "error": result.get("error")})
            else:
                not_matched.append(pdf_path.name)

        return {
            "success": len(connected) > 0,
            "folder": str(folder),
            "connected": connected,
            "not_matched": not_matched,
            "errors": errors if errors else None,
            "summary": f"Connected {len(connected)} PDFs, {len(not_matched)} not matched"
        }

    def verify_section(self, section_id: str, code: str) -> Dict:
        """Verify if a section exists and return its citation."""
        if not section_id or not isinstance(section_id, str):
            return {
                "exists": False,
                "error": "Section ID is required",
                "disclaimer_ref": "buildingcode://disclaimer"
            }

        if not code or code not in self.maps:
            return {
                "exists": False,
                "error": f"Code not found: {code}",
                "available_codes": list(self.maps.keys()),
                "disclaimer_ref": "buildingcode://disclaimer"
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
                    "disclaimer_ref": "buildingcode://disclaimer"
                }
                # Note if found with different prefix
                if actual_id != section_id:
                    result["note"] = f"Found as '{actual_id}' (you searched for '{section_id}')"

                # Add mode info
                result = self._add_mode_info(result, code)
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
            "disclaimer_ref": "buildingcode://disclaimer"
        }

    def get_applicable_code(self, location: str) -> Dict:
        """Get applicable building codes for a location."""
        if not location or not isinstance(location, str):
            return {
                "error": "Location is required",
                "example": "get_applicable_code('Toronto')",
                "disclaimer_ref": "buildingcode://disclaimer"
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
                "disclaimer_ref": "buildingcode://disclaimer"
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
                    "disclaimer_ref": "buildingcode://disclaimer"
                }

        # Unknown location - default to National codes
        return {
            "location": location,
            "error": "Location not in database",
            "suggestion": "For unknown Canadian locations, start with National Codes",
            "default_codes": ["NBC", "NFC", "NPC", "NECB"],
            "warning": "Contact local Authority Having Jurisdiction (AHJ) to confirm applicable codes",
            "available_jurisdictions": list(set(JURISDICTION_MAP.keys())),
            "disclaimer_ref": "buildingcode://disclaimer"
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
                        "disclaimer_ref": "buildingcode://disclaimer"
                    }

        return {
            "error": f"Table {table_id} not found",
            "suggestion": "Use search_code to find tables, e.g., search_code('Table 4.1.5.3', 'NBC')",
            "note": "Table IDs follow pattern: Table-X.X.X.X or Table-X.X.X.X-A"
        }

    def get_page(self, code: str, page: int) -> Dict:
        """
        Get full text content of a specific page from the Building Code PDF.

        Use this when you need to:
        - Read continuous text or tables that span multiple sections
        - See context around a specific section
        - Read tables that may be cut off in get_section

        Args:
            code: Building code name (e.g., 'NBC', 'OBC')
            page: Page number to read (1-indexed)
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
            total_pages = len(doc)

            if page < 1 or page > total_pages:
                doc.close()
                return {"error": f"Page {page} out of range (1-{total_pages})"}

            page_obj = doc[page - 1]
            text = page_obj.get_text("text")
            doc.close()

            return {
                "code": code,
                "page": page,
                "total_pages": total_pages,
                "text": text,
                "disclaimer_ref": "buildingcode://disclaimer"
            }
        except Exception as e:
            return {"error": f"Failed to read page: {str(e)}"}

    def _extract_text(self, code: str, section: Dict, max_chars: int = 8000) -> Optional[str]:
        """Extract text from PDF for a section.

        Supports multi-page sections using page_end field.
        Uses markdown format for better table rendering.
        """
        if not PYMUPDF_AVAILABLE:
            return None

        pdf_path = self.pdf_paths.get(code)
        if not pdf_path:
            return None

        try:
            doc = fitz.open(pdf_path)
            page_start = section.get("page", 0)
            page_end = section.get("page_end", page_start)  # Multi-page support

            if page_start <= 0 or page_start > len(doc):
                return None

            all_text = []

            for page_num in range(page_start, min(page_end + 1, len(doc) + 1)):
                page = doc[page_num - 1]

                # First page: use bbox if available
                if page_num == page_start and section.get("bbox"):
                    bbox = section["bbox"]
                    page_height = page.rect.height
                    rect = fitz.Rect(
                        bbox["l"],
                        page_height - bbox["b"],
                        page.rect.width - 50,
                        page_height
                    )
                    text = page.get_text("text", clip=rect)
                else:
                    # Full page with markdown for better tables
                    text = page.get_text("text")

                if text:
                    all_text.append(text.strip())

            doc.close()

            combined = "\n\n".join(all_text)
            # Limit total chars but don't cut mid-sentence
            if len(combined) > max_chars:
                combined = combined[:max_chars].rsplit('.', 1)[0] + '...'

            return combined if combined else None
        except Exception as e:
            return None

    def get_pages(self, code: str, start_page: int, end_page: int) -> Dict:
        """Read text from a range of pages.

        Use this for multi-page tables or sections that span several pages.
        Maximum 5 pages per request to avoid context overflow.

        Args:
            code: Building code name
            start_page: First page number (1-indexed)
            end_page: Last page number (inclusive)
        """
        if not PYMUPDF_AVAILABLE:
            return {"error": "PyMuPDF not installed. Run: pip install pymupdf"}

        if code not in self.pdf_paths:
            return {"error": f"No PDF loaded for code '{code}'. Use set_pdf_path first."}

        # Limit to 5 pages max
        if end_page - start_page > 4:
            return {"error": f"Maximum 5 pages per request. Requested {end_page - start_page + 1} pages."}

        pdf_path = self.pdf_paths[code]

        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)

            if start_page < 1 or end_page > total_pages or start_page > end_page:
                doc.close()
                return {"error": f"Invalid page range. Valid: 1-{total_pages}"}

            pages_text = []
            for page_num in range(start_page, end_page + 1):
                page = doc[page_num - 1]
                text = page.get_text("text")
                pages_text.append({
                    "page": page_num,
                    "text": text
                })

            doc.close()

            return {
                "code": code,
                "page_range": f"{start_page}-{end_page}",
                "total_pages": total_pages,
                "pages": pages_text,
                "disclaimer_ref": "buildingcode://disclaimer"
            }
        except Exception as e:
            return {"error": f"Failed to read pages: {str(e)}"}


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
            description="List all available building codes. Use this FIRST to see what codes exist and check if PDFs are connected.",
            inputSchema={
                "type": "object",
                "properties": {
                    "verbose": {
                        "type": "boolean",
                        "description": "If true, include full details (versions, download links, modes). Default false for token efficiency.",
                        "default": False
                    }
                },
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
            description="Search building code sections by keywords. Use this to find relevant sections by topic (e.g., 'fire separation', 'stair width'). Returns compact results by default.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keywords to search for (e.g., 'fire separation', 'stair width')"
                    },
                    "code": {
                        "type": "string",
                        "description": "Specific code to search (e.g., 'NBC', 'OBC'). Omit to search all."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 10, max 50). Use smaller values for token efficiency.",
                        "default": 10
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Include extra metadata (match_type, document_type, etc). Default false.",
                        "default": False
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
            description="Get section details by ID. Use this after search_code to get page number, citation, and text (if PDF connected).",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Section ID (e.g., '9.10.14.1'). Division prefix auto-detected."
                    },
                    "code": {
                        "type": "string",
                        "description": "Code name (e.g., 'NBC2025', 'OBC_Vol1')"
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Include keywords, bbox, mode_info, etc. Default false.",
                        "default": False
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
            description="Connect your PDF file for text extraction. Use this to enable full text in get_section results. Can also auto-scan a folder.",
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
            description="Get full text content of a specific page. Requires PDF to be connected via set_pdf_path. Use this when you need to see all content on a page, including tables and context around sections.",
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
        Tool(
            name="get_pages",
            description="Get text from a range of pages (max 5). Use this for multi-page tables or sections that span several pages. Requires PDF connected via set_pdf_path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code name (e.g., 'NBC', 'OBC')"
                    },
                    "start_page": {
                        "type": "integer",
                        "description": "First page number (1-indexed)"
                    },
                    "end_page": {
                        "type": "integer",
                        "description": "Last page number (inclusive)"
                    }
                },
                "required": ["code", "start_page", "end_page"],
                "additionalProperties": False
            },
            annotations=ToolAnnotations(
                title="Get Multiple Pages",
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
        result = mcp.list_codes(arguments.get("verbose", False))
    elif name == "search_code":
        result = mcp.search_code(
            arguments.get("query", ""),
            arguments.get("code"),
            arguments.get("limit", 10),
            arguments.get("verbose", False)
        )
    elif name == "get_section":
        result = mcp.get_section(
            arguments.get("id", ""),
            arguments.get("code", ""),
            arguments.get("verbose", False)
        )
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
    elif name == "get_pages":
        result = mcp.get_pages(
            arguments.get("code", ""),
            arguments.get("start_page", 0),
            arguments.get("end_page", 0)
        )
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
        ),
        Resource(
            uri="buildingcode://disclaimer",
            name="Legal Disclaimer",
            description="Important disclaimer about using this tool - reference only, not legal advice",
            mimeType="text/plain"
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

    elif uri_str == "buildingcode://disclaimer":
        return DISCLAIMER

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
    mcp = get_mcp()
    total_sections = sum(len(d.get("sections", [])) for d in mcp.maps.values())
    _log(f"Starting server: {len(mcp.maps)} codes, {total_sections} sections indexed")
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
