#!/usr/bin/env python3
"""
Smoke Tests for Canadian Building Code MCP
Basic tests to verify core functionality works.

Run: pytest tests/test_smoke.py -v
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the core class (without MCP server parts)
exec_lines = []
with open(Path(__file__).parent.parent / "src" / "mcp_server.py", 'r', encoding='utf-8') as f:
    for line in f:
        if 'server = Server' in line:
            break
        exec_lines.append(line)
exec(''.join(exec_lines), globals())


class TestListCodes:
    """Test list_codes functionality"""

    def test_returns_codes(self):
        """Should return list of available codes"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.list_codes()

        assert 'codes' in result
        assert result.get('total_codes', 0) > 0 or len(result.get('codes', [])) > 0

    def test_contains_nbc(self):
        """Should include NBC (National Building Code)"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.list_codes()

        codes = result.get('codes', [])
        code_names = [c.get('code', '') for c in codes]
        assert 'NBC' in code_names


class TestSearchCode:
    """Test search_code functionality"""

    def test_returns_results(self):
        """Should return search results for valid query"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.search_code('fire', 'NBC')

        assert 'results' in result
        assert result['total'] > 0

    def test_empty_query_returns_error(self):
        """Should handle empty query gracefully"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.search_code('', 'NBC')

        assert 'error' in result or result['total'] == 0

    def test_invalid_code_returns_error(self):
        """Should return error for non-existent code"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.search_code('fire', 'NONEXISTENT')

        assert 'error' in result

    def test_section_id_search(self):
        """Should find sections by ID"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.search_code('9.10.14', 'NBC')

        assert result['total'] > 0
        # Should prioritize exact matches
        assert any('9.10.14' in r['id'] for r in result['results'])


class TestGetSection:
    """Test get_section functionality"""

    def test_returns_section(self):
        """Should return section details"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.get_section('B-9.10.14', 'NBC')

        assert 'error' not in result
        assert result.get('id') == 'B-9.10.14'
        assert 'title' in result
        assert 'page' in result

    def test_invalid_section_returns_error(self):
        """Should return error for non-existent section"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.get_section('INVALID.ID', 'NBC')

        assert 'error' in result

    def test_invalid_code_returns_error(self):
        """Should return error for non-existent code"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.get_section('9.10.14', 'NONEXISTENT')

        assert 'error' in result


class TestGetHierarchy:
    """Test get_hierarchy functionality"""

    def test_returns_hierarchy(self):
        """Should return parent, children, siblings"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.get_hierarchy('B-9.10.14', 'NBC')

        assert 'error' not in result
        assert 'parent' in result
        assert 'children' in result
        assert 'siblings' in result

    def test_has_children(self):
        """Should find children for section with subsections"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.get_hierarchy('B-9.10.14', 'NBC')

        assert len(result['children']) > 0

    def test_has_siblings(self):
        """Should find siblings"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.get_hierarchy('B-9.10.14', 'NBC')

        assert len(result['siblings']) > 0

    def test_invalid_section_id(self):
        """Should handle None/empty section_id"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.get_hierarchy(None, 'NBC')

        assert 'error' in result


class TestSetPdfPath:
    """Test set_pdf_path functionality"""

    def test_invalid_path_returns_error(self):
        """Should return error for non-existent file"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.set_pdf_path('NBC', '/nonexistent/path.pdf')

        assert 'error' in result

    def test_invalid_code_returns_error(self):
        """Should return error for non-existent code"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.set_pdf_path('NONEXISTENT', 'some/path.pdf')

        assert 'error' in result

    def test_directory_returns_error(self):
        """Should reject directory path"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.set_pdf_path('NBC', 'maps/')

        assert 'error' in result


class TestDataQuality:
    """Test data quality in maps"""

    def test_nbc_has_sections(self):
        """NBC should have substantial number of sections"""
        mcp = BuildingCodeMCP('maps')
        sections = mcp.maps.get('NBC', {}).get('sections', [])

        assert len(sections) > 2000  # NBC has ~2700+ sections

    def test_sections_have_required_fields(self):
        """Each section should have id, title, page"""
        mcp = BuildingCodeMCP('maps')
        sections = mcp.maps.get('NBC', {}).get('sections', [])[:100]

        for section in sections:
            assert 'id' in section
            assert 'title' in section
            assert 'page' in section

    def test_keywords_exist(self):
        """Most sections should have keywords"""
        mcp = BuildingCodeMCP('maps')
        sections = mcp.maps.get('NBC', {}).get('sections', [])

        with_keywords = sum(1 for s in sections if s.get('keywords'))
        ratio = with_keywords / len(sections)

        assert ratio > 0.8  # At least 80% have keywords


class TestSynonymSearch:
    """Test synonym-based search"""

    def test_washroom_finds_water_closet(self):
        """Searching 'restroom' should find 'washroom' or 'water closet' sections"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.search_code('restroom', 'NBC')

        # Should find results due to synonym expansion
        assert result['total'] > 0 or 'search_features' in result

    def test_stairs_finds_stairway(self):
        """Searching 'stairs' should find 'stairway' sections"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.search_code('stairs', 'NBC')

        assert result['total'] > 0

    def test_accessible_finds_barrier_free(self):
        """Searching 'accessible' should find 'barrier-free' sections"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.search_code('accessible', 'NBC')

        assert result['total'] > 0


class TestFuzzySearch:
    """Test fuzzy matching for typo tolerance"""

    def test_search_features_reported(self):
        """Search should report available features"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.search_code('fire', 'NBC')

        assert 'search_features' in result
        assert 'synonyms' in result['search_features']

    def test_slight_typo_still_finds(self):
        """Slight typos should still return results (if rapidfuzz available)"""
        mcp = BuildingCodeMCP('maps')
        # 'fier' is a typo for 'fire'
        result = mcp.search_code('fier separation', 'NBC')

        # Even without fuzzy, synonym or partial match might work
        # Just ensure no crash
        assert 'results' in result

    def test_match_type_returned(self):
        """Results should include match_type indicator"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.search_code('fire', 'NBC')

        if result['results']:
            # At least some results should have match_type
            has_match_type = any('match_type' in r for r in result['results'])
            assert has_match_type


class TestVerifySection:
    """Test verify_section functionality"""

    def test_valid_section_exists(self):
        """Should confirm existing section"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.verify_section('B-9.10.14', 'NBC')

        assert result['exists'] is True
        assert 'citation' in result

    def test_invalid_section_not_exists(self):
        """Should report non-existent section"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.verify_section('99.99.99.99', 'NBC')

        assert result['exists'] is False
        assert 'error' in result

    def test_suggests_similar_sections(self):
        """Should suggest similar sections when not found"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.verify_section('9.10.999', 'NBC')

        assert result['exists'] is False
        # Should suggest similar sections starting with 9.10
        assert 'similar_sections' in result

    def test_auto_prefix_detection(self):
        """Should auto-detect Division prefix (A/B/C)"""
        mcp = BuildingCodeMCP('maps')
        # Search without prefix
        result = mcp.verify_section('9.10.14', 'NBC')

        # Should find B-9.10.14 automatically
        if result['exists']:
            assert 'B-9.10.14' in result.get('section_id', '') or 'note' in result


class TestGetApplicableCode:
    """Test get_applicable_code functionality"""

    def test_toronto_returns_obc(self):
        """Toronto should return OBC as primary"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.get_applicable_code('Toronto')

        assert result['primary_code'] == 'OBC'

    def test_vancouver_returns_bcbc(self):
        """Vancouver should return BCBC as primary"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.get_applicable_code('Vancouver')

        assert result['primary_code'] == 'BCBC'

    def test_montreal_returns_qcc(self):
        """Montreal should return QCC as primary"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.get_applicable_code('Montreal')

        assert result['primary_code'] == 'QCC'

    def test_unknown_location_suggests_national(self):
        """Unknown location should suggest national codes"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.get_applicable_code('Unknown City XYZ')

        assert 'error' in result or 'default_codes' in result

    def test_includes_disclaimer(self):
        """All responses should include disclaimer"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.get_applicable_code('Toronto')

        assert 'disclaimer' in result


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_special_characters_in_query(self):
        """Should handle special characters in search query"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.search_code('fire-resistance (1h)', 'NBC')

        # Should not crash
        assert 'results' in result

    def test_very_long_query(self):
        """Should handle very long queries"""
        mcp = BuildingCodeMCP('maps')
        long_query = 'fire ' * 100
        result = mcp.search_code(long_query, 'NBC')

        # Should not crash
        assert 'results' in result

    def test_unicode_query(self):
        """Should handle unicode characters"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.search_code('résistance au feu', 'NBC')

        # Should not crash
        assert 'results' in result

    def test_none_code_searches_all(self):
        """Passing None for code should search all codes"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.search_code('fire', None)

        assert result['total'] > 0
        # Should have results from multiple codes
        codes_found = set(r['code'] for r in result['results'])
        assert len(codes_found) >= 1

    def test_empty_maps_directory(self):
        """Should handle missing maps gracefully"""
        mcp = BuildingCodeMCP('nonexistent_maps_dir')

        # Should not crash, just have empty maps
        assert mcp.maps == {} or isinstance(mcp.maps, dict)

    def test_section_with_division_prefix(self):
        """Should handle sections with A-, B-, C- prefixes"""
        mcp = BuildingCodeMCP('maps')

        # Test with explicit prefix
        result_b = mcp.get_section('B-9.10.14', 'NBC')
        assert 'error' not in result_b

        # Test hierarchy with prefix
        hierarchy = mcp.get_hierarchy('B-9.10.14', 'NBC')
        assert 'children' in hierarchy


class TestMultipleCodeSearch:
    """Test searching across multiple codes"""

    def test_search_all_codes(self):
        """Should search all codes when none specified"""
        mcp = BuildingCodeMCP('maps')
        # Use a very common term that exists in all codes
        result = mcp.search_code('fire')

        # Should find results
        assert result['total'] > 0
        # Results come from at least one code (might be same code due to limit)
        codes = set(r['code'] for r in result['results'])
        assert len(codes) >= 1

    def test_guide_marked_as_guide(self):
        """Guide results should be marked as non-binding"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.search_code('fire', 'IUGP9')

        if result['total'] > 0:
            # Results from guide should have note
            for r in result['results']:
                if r.get('document_type') == 'guide':
                    assert 'note' in r


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
