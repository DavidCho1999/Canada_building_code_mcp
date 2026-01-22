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

        assert 'codes' in result or 'indexed_codes' in result
        assert result.get('total', 0) > 0 or len(result.get('indexed_codes', [])) > 0

    def test_contains_nbc(self):
        """Should include NBC (National Building Code)"""
        mcp = BuildingCodeMCP('maps')
        result = mcp.list_codes()

        codes = result.get('codes', result.get('indexed_codes', []))
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


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
