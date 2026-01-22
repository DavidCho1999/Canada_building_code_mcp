#!/usr/bin/env python3
"""
BYOD Mode Quality Tests for Canadian Building Code MCP

Tests PDF text extraction quality, table handling, and coordinate accuracy.
Requires actual PDF files in sources/ directory.

Run: pytest tests/test_byod_quality.py -v
"""

import sys
import json
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the core class
exec_lines = []
with open(Path(__file__).parent.parent / "src" / "mcp_server.py", 'r', encoding='utf-8') as f:
    for line in f:
        if 'server = Server' in line:
            break
        exec_lines.append(line)
exec(''.join(exec_lines), globals())


# ============================================
# Test Configuration
# ============================================

SOURCES_DIR = Path(__file__).parent.parent / "sources"
MAPS_DIR = Path(__file__).parent.parent / "maps"

# PDF filename mappings
PDF_FILES = {
    "NBC": "NBC2025p1.pdf",
    "OBC_Vol1": "obc volume 1.pdf",
    "OBC_Vol2": "obc volume 2.pdf",
    "BCBC": "bcbc_2024_web_version_20240409.pdf",
    "ABC": "2023NBCAE-V1_National_Building_Code2023_Alberta_Edition.pdf",
    "NFC": "NFC2025p1.pdf",
    "NECB": "NECB2025p1.pdf",
    "NPC": "NPC2025p1.pdf",
    "QCC": "QCC_2020p1.pdf",
    "IUGP9": "IUGP9_2020p1.2025-01-30.pdf",
}

# Known sections with tables for quality testing
TABLE_SECTIONS = {
    "NBC": [
        {"id": "B-3.1.17.1", "desc": "Fire-Resistance Ratings table"},
        {"id": "B-9.10.14.4", "desc": "Spatial Separation tables"},
        {"id": "B-Table 3.2.4.1.-A", "desc": "Maximum Area of Building table"},
    ],
    "OBC_Vol1": [
        {"id": "B-3.1.17.1", "desc": "Fire-Resistance Ratings table"},
    ]
}

# Known sections with specific expected content
CONTENT_VERIFICATION = {
    "NBC": {
        "B-9.10.14": {
            "expected_terms": ["fire", "separation", "garage"],
            "section_title_contains": "Separations"
        },
        "B-3.2.4.1": {
            "expected_terms": ["area", "building", "storey"],
            "section_title_contains": "Building Size"
        }
    }
}


# ============================================
# Helper Functions
# ============================================

def get_pdf_path(code: str) -> Path:
    """Get PDF path for a code."""
    filename = PDF_FILES.get(code)
    if not filename:
        return None
    return SOURCES_DIR / filename


def calculate_text_quality_score(text: str, expected_terms: list = None) -> dict:
    """
    Calculate quality score for extracted text.
    Returns dict with scores and details.
    """
    if not text:
        return {"score": 0, "issues": ["No text extracted"], "details": {}}

    score = 100
    issues = []
    details = {}

    # 1. Check for garbage characters (OCR artifacts)
    garbage_pattern = r'[^\x00-\x7F\u00C0-\u017F\u2000-\u206F\u2190-\u21FF]+'
    garbage_matches = re.findall(garbage_pattern, text)
    garbage_ratio = len(''.join(garbage_matches)) / len(text) if text else 0
    details["garbage_ratio"] = round(garbage_ratio, 4)

    if garbage_ratio > 0.1:
        score -= 20
        issues.append(f"High garbage character ratio: {garbage_ratio:.2%}")
    elif garbage_ratio > 0.05:
        score -= 10
        issues.append(f"Moderate garbage characters: {garbage_ratio:.2%}")

    # 2. Check for proper line breaks (not excessive)
    lines = text.split('\n')
    avg_line_length = sum(len(l) for l in lines) / len(lines) if lines else 0
    details["avg_line_length"] = round(avg_line_length, 1)
    details["num_lines"] = len(lines)

    if avg_line_length < 10:
        score -= 15
        issues.append(f"Lines too short (avg {avg_line_length:.1f} chars) - possible column break issues")

    # 3. Check for table-like patterns (pipes, excessive whitespace)
    table_pattern_count = len(re.findall(r'\|', text))
    excessive_whitespace = len(re.findall(r'  +', text))
    details["pipe_chars"] = table_pattern_count
    details["excessive_whitespace"] = excessive_whitespace

    # 4. Check for expected terms if provided
    if expected_terms:
        text_lower = text.lower()
        found_terms = [t for t in expected_terms if t.lower() in text_lower]
        term_ratio = len(found_terms) / len(expected_terms)
        details["expected_terms_found"] = found_terms
        details["expected_terms_missing"] = [t for t in expected_terms if t.lower() not in text_lower]
        details["term_match_ratio"] = term_ratio

        if term_ratio < 0.5:
            score -= 25
            issues.append(f"Low expected term match: {term_ratio:.0%}")
        elif term_ratio < 0.8:
            score -= 10
            issues.append(f"Some expected terms missing: {term_ratio:.0%}")

    # 5. Check text length (too short = incomplete)
    details["text_length"] = len(text)
    if len(text) < 50:
        score -= 20
        issues.append("Text too short - possibly incomplete extraction")

    # 6. Check for sentence structure (has periods, capitals)
    has_sentences = bool(re.search(r'[A-Z][^.!?]*[.!?]', text))
    details["has_sentence_structure"] = has_sentences
    if not has_sentences and len(text) > 100:
        score -= 10
        issues.append("No clear sentence structure detected")

    return {
        "score": max(0, score),
        "issues": issues,
        "details": details
    }


def calculate_bbox_accuracy(section: dict, text: str) -> dict:
    """
    Evaluate bounding box accuracy based on extracted text.
    """
    bbox = section.get("bbox")
    if not bbox:
        return {"score": 50, "issues": ["No bbox available"], "details": {}}

    score = 100
    issues = []
    details = {
        "bbox": bbox,
        "page": section.get("page")
    }

    # Check bbox dimensions
    width = bbox.get("r", 0) - bbox.get("l", 0)
    height = bbox.get("t", 0) - bbox.get("b", 0)
    details["bbox_width"] = round(width, 1)
    details["bbox_height"] = round(height, 1)

    # Very small bbox might indicate header-only extraction
    if height < 20:
        score -= 10
        issues.append("Very small bbox height - might be header only")

    # Check if section title appears in text (good bbox alignment)
    title = section.get("title", "")
    if title and text:
        # Check first few words of title
        title_words = title.split()[:3]
        text_start = text[:200].lower()
        found_title_words = sum(1 for w in title_words if w.lower() in text_start)
        title_match_ratio = found_title_words / len(title_words) if title_words else 0
        details["title_match_ratio"] = title_match_ratio

        if title_match_ratio < 0.3:
            score -= 15
            issues.append("Section title not found at start of text")

    return {
        "score": max(0, score),
        "issues": issues,
        "details": details
    }


# ============================================
# Test Classes
# ============================================

class TestBYODConnection:
    """Test PDF connection functionality"""

    def test_connect_nbc_pdf(self):
        """Should successfully connect NBC PDF"""
        pdf_path = get_pdf_path("NBC")
        if not pdf_path or not pdf_path.exists():
            import pytest
            pytest.skip("NBC PDF not available")

        mcp = BuildingCodeMCP(str(MAPS_DIR))
        result = mcp.set_pdf_path("NBC", str(pdf_path))

        assert result.get("success") is True
        assert "NBC" in mcp.pdf_paths

    def test_version_verification(self):
        """Should verify PDF version matches map"""
        pdf_path = get_pdf_path("NBC")
        if not pdf_path or not pdf_path.exists():
            import pytest
            pytest.skip("NBC PDF not available")

        mcp = BuildingCodeMCP(str(MAPS_DIR))
        result = mcp.set_pdf_path("NBC", str(pdf_path))

        # Should be verified or have warning
        assert "verified" in result or "warning" in result


class TestTextExtraction:
    """Test text extraction quality"""

    def test_extract_simple_section(self):
        """Should extract text from simple section"""
        pdf_path = get_pdf_path("NBC")
        if not pdf_path or not pdf_path.exists():
            import pytest
            pytest.skip("NBC PDF not available")

        mcp = BuildingCodeMCP(str(MAPS_DIR))
        mcp.set_pdf_path("NBC", str(pdf_path))

        # Get a section known to have text
        result = mcp.get_section("B-9.10.14", "NBC")

        if result.get("text_available"):
            text = result.get("text", "")
            quality = calculate_text_quality_score(
                text,
                ["fire", "separation", "garage"]
            )

            print(f"\n=== Text Extraction Quality ===")
            print(f"Score: {quality['score']}/100")
            print(f"Text length: {len(text)} chars")
            print(f"Issues: {quality['issues']}")

            assert quality["score"] >= 50, f"Text quality too low: {quality}"

    def test_extract_multiple_sections(self):
        """Should extract text from multiple sections consistently"""
        pdf_path = get_pdf_path("NBC")
        if not pdf_path or not pdf_path.exists():
            import pytest
            pytest.skip("NBC PDF not available")

        mcp = BuildingCodeMCP(str(MAPS_DIR))
        mcp.set_pdf_path("NBC", str(pdf_path))

        test_sections = ["B-9.9", "B-9.10", "B-3.2.4", "B-9.10.14"]
        results = []

        for section_id in test_sections:
            result = mcp.get_section(section_id, "NBC")
            if result.get("text_available"):
                text = result.get("text", "")
                quality = calculate_text_quality_score(text)
                results.append({
                    "section": section_id,
                    "score": quality["score"],
                    "length": len(text)
                })

        if results:
            avg_score = sum(r["score"] for r in results) / len(results)
            print(f"\n=== Multi-Section Extraction ===")
            for r in results:
                print(f"  {r['section']}: {r['score']}/100 ({r['length']} chars)")
            print(f"Average score: {avg_score:.1f}/100")

            assert avg_score >= 50


class TestTableExtraction:
    """Test table extraction quality"""

    def test_table_section_extraction(self):
        """Should handle sections with tables"""
        pdf_path = get_pdf_path("NBC")
        if not pdf_path or not pdf_path.exists():
            import pytest
            pytest.skip("NBC PDF not available")

        mcp = BuildingCodeMCP(str(MAPS_DIR))
        mcp.set_pdf_path("NBC", str(pdf_path))

        # Test known table sections
        table_sections = TABLE_SECTIONS.get("NBC", [])
        results = []

        for ts in table_sections:
            result = mcp.get_section(ts["id"], "NBC")
            if result.get("text_available"):
                text = result.get("text", "")
                quality = calculate_text_quality_score(text)

                # Check for table-specific patterns
                has_numbers = bool(re.search(r'\d+', text))
                has_structure = bool(re.search(r'(\d+\s+){2,}', text))

                results.append({
                    "section": ts["id"],
                    "desc": ts["desc"],
                    "score": quality["score"],
                    "has_numbers": has_numbers,
                    "has_structure": has_structure,
                    "details": quality["details"]
                })

        if results:
            print(f"\n=== Table Extraction Quality ===")
            for r in results:
                print(f"  {r['section']} ({r['desc']})")
                print(f"    Score: {r['score']}/100")
                print(f"    Has numbers: {r['has_numbers']}")
                print(f"    Has structure: {r['has_structure']}")


class TestBboxAccuracy:
    """Test bounding box coordinate accuracy"""

    def test_bbox_text_alignment(self):
        """Bbox should align with extracted text"""
        pdf_path = get_pdf_path("NBC")
        if not pdf_path or not pdf_path.exists():
            import pytest
            pytest.skip("NBC PDF not available")

        mcp = BuildingCodeMCP(str(MAPS_DIR))
        mcp.set_pdf_path("NBC", str(pdf_path))

        # Get sections with bbox
        sections_data = mcp.maps.get("NBC", {}).get("sections", [])[:20]
        results = []

        for section in sections_data:
            if section.get("bbox"):
                result = mcp.get_section(section["id"], "NBC")
                if result.get("text_available"):
                    text = result.get("text", "")
                    accuracy = calculate_bbox_accuracy(section, text)
                    results.append({
                        "section": section["id"],
                        "score": accuracy["score"],
                        "details": accuracy["details"]
                    })

        if results:
            avg_score = sum(r["score"] for r in results) / len(results)
            print(f"\n=== Bbox Accuracy ===")
            print(f"Tested {len(results)} sections")
            print(f"Average accuracy score: {avg_score:.1f}/100")

            assert avg_score >= 60


class TestEdgeCases:
    """Test edge cases in BYOD mode"""

    def test_first_page_section(self):
        """Should handle sections on first pages"""
        pdf_path = get_pdf_path("NBC")
        if not pdf_path or not pdf_path.exists():
            import pytest
            pytest.skip("NBC PDF not available")

        mcp = BuildingCodeMCP(str(MAPS_DIR))
        mcp.set_pdf_path("NBC", str(pdf_path))

        # Get Division A (usually early in document)
        result = mcp.get_section("A", "NBC")

        # Should not crash
        assert "error" not in result or result.get("text_available") is False

    def test_last_page_section(self):
        """Should handle sections near end of document"""
        pdf_path = get_pdf_path("NBC")
        if not pdf_path or not pdf_path.exists():
            import pytest
            pytest.skip("NBC PDF not available")

        mcp = BuildingCodeMCP(str(MAPS_DIR))
        mcp.set_pdf_path("NBC", str(pdf_path))

        # Get a late Division C section
        result = mcp.get_section("C-1.1.1.1", "NBC")

        # Should not crash
        assert "results" not in result or "error" in result or result.get("text_available") is not None

    def test_section_without_bbox(self):
        """Should handle sections without bbox gracefully"""
        pdf_path = get_pdf_path("NBC")
        if not pdf_path or not pdf_path.exists():
            import pytest
            pytest.skip("NBC PDF not available")

        mcp = BuildingCodeMCP(str(MAPS_DIR))
        mcp.set_pdf_path("NBC", str(pdf_path))

        # Find a section without bbox
        sections = mcp.maps.get("NBC", {}).get("sections", [])
        no_bbox_sections = [s for s in sections if not s.get("bbox")]

        if no_bbox_sections:
            result = mcp.get_section(no_bbox_sections[0]["id"], "NBC")
            # Should not crash, might extract full page text
            assert "error" not in result


class TestComprehensiveQuality:
    """Comprehensive quality assessment"""

    def test_overall_extraction_quality(self):
        """
        Comprehensive test scoring overall BYOD extraction quality.
        This is the main quality assessment test.
        """
        pdf_path = get_pdf_path("NBC")
        if not pdf_path or not pdf_path.exists():
            import pytest
            pytest.skip("NBC PDF not available")

        mcp = BuildingCodeMCP(str(MAPS_DIR))
        mcp.set_pdf_path("NBC", str(pdf_path))

        # Sample diverse sections
        test_sections = [
            {"id": "B-9.10.14", "type": "regulation", "expected": ["fire", "separation"]},
            {"id": "B-9.9", "type": "regulation", "expected": ["stairs", "stairways"]},
            {"id": "B-3.2.4.1", "type": "regulation", "expected": ["area", "building"]},
            {"id": "A-1.1.1.1", "type": "compliance", "expected": ["code", "compliance"]},
        ]

        scores = {
            "text_quality": [],
            "bbox_accuracy": [],
            "content_relevance": []
        }

        print("\n" + "="*60)
        print("COMPREHENSIVE BYOD QUALITY ASSESSMENT")
        print("="*60)

        for ts in test_sections:
            result = mcp.get_section(ts["id"], "NBC")

            if result.get("text_available"):
                text = result.get("text", "")

                # Text quality
                tq = calculate_text_quality_score(text, ts.get("expected", []))
                scores["text_quality"].append(tq["score"])

                # Bbox accuracy
                section_data = None
                for s in mcp.maps.get("NBC", {}).get("sections", []):
                    if s.get("id") == ts["id"] or s.get("id") == f"B-{ts['id']}" or s.get("id") == f"A-{ts['id']}":
                        section_data = s
                        break

                if section_data:
                    ba = calculate_bbox_accuracy(section_data, text)
                    scores["bbox_accuracy"].append(ba["score"])

                # Content relevance (based on expected terms)
                if ts.get("expected"):
                    found = sum(1 for t in ts["expected"] if t.lower() in text.lower())
                    relevance = (found / len(ts["expected"])) * 100
                    scores["content_relevance"].append(relevance)

                print(f"\n--- {ts['id']} ({ts['type']}) ---")
                print(f"  Text quality: {tq['score']}/100")
                print(f"  Text length: {len(text)} chars")
                if tq["issues"]:
                    print(f"  Issues: {', '.join(tq['issues'])}")

        # Calculate final scores
        final_scores = {}
        for category, values in scores.items():
            if values:
                final_scores[category] = sum(values) / len(values)

        overall = sum(final_scores.values()) / len(final_scores) if final_scores else 0

        print("\n" + "="*60)
        print("FINAL SCORES")
        print("="*60)
        for category, score in final_scores.items():
            grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"
            print(f"  {category}: {score:.1f}/100 ({grade})")

        print(f"\n  OVERALL: {overall:.1f}/100")
        print("="*60)

        # Store results for reporting
        return {
            "overall": overall,
            "categories": final_scores,
            "grade": "A" if overall >= 90 else "B" if overall >= 80 else "C" if overall >= 70 else "D" if overall >= 60 else "F"
        }


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v', '-s'])
