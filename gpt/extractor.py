# extractor.py - Canadian Building Code GPT Helper
# Upload this file to GPT Knowledge for faster PDF extraction

import re

def extract_section(pdf_path, page_num, section_id):
    """
    Extract section text from PDF by Section ID.

    Args:
        pdf_path: Path to uploaded PDF file
        page_num: Page number (1-indexed)
        section_id: Section ID like "9.8.8.2", "3.2.2.55"

    Returns:
        Extracted text or error message
    """

    # Get page text
    text = None

    try:
        import fitz
        doc = fitz.open(pdf_path)
        page = doc[page_num - 1]
        text = page.get_text("text")
        doc.close()
    except:
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[page_num - 1]
                text = page.extract_text() or ""
        except Exception as e:
            return f"Error reading PDF: {e}"

    if not text:
        return f"Could not extract text from page {page_num}"

    # Find section ID in text
    if section_id not in text:
        # Try without leading zeros or with variations
        variations = [
            section_id,
            section_id.replace(".", ". "),
            section_id + ".",
            section_id + " "
        ]

        found = False
        for var in variations:
            if var in text:
                section_id = var
                found = True
                break

        if not found:
            return f"Section {section_id} not found on page {page_num}.\n\nPage preview:\n{text[:1000]}"

    # Extract from section ID to next section
    start_idx = text.find(section_id)
    remaining = text[start_idx:]

    # Find next section (pattern: newline + number.number.number)
    next_match = re.search(r'\n\d+\.\d+\.\d+\.?\d*[\s\.]', remaining[len(section_id):])

    if next_match:
        end_idx = len(section_id) + next_match.start()
        result = remaining[:end_idx].strip()
    else:
        # No next section, take up to 2500 chars
        result = remaining[:2500].strip()

    return result


def search_json(json_data, query, code_filter=None):
    """
    Search JSON for sections matching query.

    Args:
        json_data: Loaded JSON data (dict)
        query: Search keywords
        code_filter: Optional code name filter (e.g., "OBC", "NBC")

    Returns:
        List of matching sections
    """

    results = []
    query_lower = query.lower()
    query_words = query_lower.split()

    # Get codes to search
    if "codes" in json_data:
        codes = json_data["codes"]
    else:
        codes = {json_data.get("code", "unknown"): json_data}

    for code_name, code_data in codes.items():
        # Apply code filter
        if code_filter and code_filter.upper() not in code_name.upper():
            continue

        sections = code_data.get("sections", [])

        for section in sections:
            score = 0

            # Check title
            title = section.get("title", "").lower()
            for word in query_words:
                if word in title:
                    score += 10

            # Check keywords
            keywords = section.get("keywords", [])
            for word in query_words:
                if word in keywords:
                    score += 5
                for kw in keywords:
                    if word in kw:
                        score += 2

            if score > 0:
                results.append({
                    "id": section.get("id"),
                    "title": section.get("title"),
                    "page": section.get("page"),
                    "code": code_name,
                    "score": score
                })

    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:10]  # Top 10


def extract_sections_batch(pdf_path, sections):
    """
    Extract multiple sections in ONE PDF open (faster!).

    Args:
        pdf_path: Path to uploaded PDF file
        sections: List of {"page": int, "id": str}
                  e.g., [{"page": 452, "id": "4.1.3.2"}, ...]

    Returns:
        Dict of {section_id: extracted_text}
    """

    results = {}

    # Try PyMuPDF first
    try:
        import fitz
        doc = fitz.open(pdf_path)

        for s in sections:
            page_num = s["page"]
            section_id = s["id"]

            try:
                page = doc[page_num - 1]
                text = page.get_text("text")

                if section_id in text:
                    start_idx = text.find(section_id)
                    remaining = text[start_idx:]

                    # Find next section
                    next_match = re.search(
                        r'\n\d+\.\d+\.\d+\.?\d*[\s\.]',
                        remaining[len(section_id):]
                    )

                    if next_match:
                        end_idx = len(section_id) + next_match.start()
                        results[section_id] = remaining[:end_idx].strip()
                    else:
                        results[section_id] = remaining[:2000].strip()
                else:
                    results[section_id] = f"[Section {section_id} not found on page {page_num}]"

            except Exception as e:
                results[section_id] = f"[Error extracting {section_id}: {e}]"

        doc.close()
        return results

    except ImportError:
        pass

    # Fallback: pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for s in sections:
                page_num = s["page"]
                section_id = s["id"]

                try:
                    page = pdf.pages[page_num - 1]
                    text = page.extract_text() or ""

                    if section_id in text:
                        start_idx = text.find(section_id)
                        remaining = text[start_idx:]

                        next_match = re.search(
                            r'\n\d+\.\d+\\.d+\.?\d*[\s\.]',
                            remaining[len(section_id):]
                        )

                        if next_match:
                            end_idx = len(section_id) + next_match.start()
                            results[section_id] = remaining[:end_idx].strip()
                        else:
                            results[section_id] = remaining[:2000].strip()
                    else:
                        results[section_id] = f"[Section {section_id} not found on page {page_num}]"

                except Exception as e:
                    results[section_id] = f"[Error: {e}]"

        return results

    except Exception as e:
        return {"error": f"Could not open PDF: {e}"}


def extract_table(json_data, table_id):
    """
    Extract table markdown from JSON maps (fast, primary method).

    Args:
        json_data: Loaded JSON map data (single code or multi-code dict)
        table_id: Table ID (e.g., "4.1.5.3" or "Table-4.1.5.3")

    Returns:
        Dict with table info or error message
        {
            "id": "Table-4.1.5.3",
            "title": "Live Loads on Floors...",
            "page": 452,
            "markdown": "| Col1 | Col2 |\n|---|---|\n...",
            "table_info": {"rows": 15, "cols": 4},
            "source": "JSON"
        }
    """
    # Normalize ID - add "Table-" prefix if missing
    if not table_id.startswith("Table-"):
        table_id = f"Table-{table_id}"

    # Handle both single-code and multi-code JSON structures
    codes = json_data if isinstance(json_data, dict) and "tables" not in json_data else {"default": json_data}

    # Search in tables array
    for code_name, code_data in codes.items():
        tables = code_data.get("tables", [])
        for table in tables:
            if table.get("id") == table_id:
                return {
                    "id": table["id"],
                    "title": table.get("title", ""),
                    "page": table.get("page", 0),
                    "markdown": table.get("markdown", ""),
                    "table_info": table.get("table_info", {}),
                    "source": "JSON"
                }

    return {"error": f"Table {table_id} not found in JSON"}


def extract_table_from_pdf(pdf_path, page, table_id):
    """
    Attempt to extract table from PDF by searching for table ID.
    Note: No bbox available, uses text search + heuristics.
    This is a FALLBACK method - JSON markdown is preferred.

    Args:
        pdf_path: Path to PDF file
        page: Page number
        table_id: Table ID to search for (e.g., "Table-4.1.5.3")

    Returns:
        Dict with extracted text or error
    """
    # Normalize table ID
    if not table_id.startswith("Table-"):
        table_id = f"Table-{table_id}"

    # Try PyMuPDF first
    try:
        import fitz
        doc = fitz.open(pdf_path)
        page_obj = doc[page - 1]
        text = page_obj.get_text("text")
        doc.close()

        # Search for table ID (with or without "Table " prefix)
        search_patterns = [
            table_id,
            table_id.replace("Table-", "Table "),
            table_id.replace("Table-", "")
        ]

        start_idx = -1
        for pattern in search_patterns:
            if pattern in text:
                start_idx = text.find(pattern)
                break

        if start_idx >= 0:
            # Extract ~2000 chars after table ID
            excerpt = text[start_idx:start_idx + 2000]

            return {
                "id": table_id,
                "page": page,
                "text": excerpt,
                "source": "PDF (heuristic)",
                "note": "⚠️ Table extracted from PDF text. Format may not match original."
            }
        else:
            return {"error": f"Table {table_id} not found on page {page}"}

    except ImportError:
        pass

    # Fallback: pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            page_obj = pdf.pages[page - 1]
            text = page_obj.extract_text() or ""

            search_patterns = [
                table_id,
                table_id.replace("Table-", "Table "),
                table_id.replace("Table-", "")
            ]

            start_idx = -1
            for pattern in search_patterns:
                if pattern in text:
                    start_idx = text.find(pattern)
                    break

            if start_idx >= 0:
                excerpt = text[start_idx:start_idx + 2000]
                return {
                    "id": table_id,
                    "page": page,
                    "text": excerpt,
                    "source": "PDF (heuristic)",
                    "note": "⚠️ Table extracted from PDF text. Format may not match original."
                }
            else:
                return {"error": f"Table {table_id} not found on page {page}"}

    except Exception as e:
        return {"error": f"PDF extraction failed: {e}"}


def extract_tables_batch(json_data, table_ids):
    """
    Extract multiple tables from JSON in one call (fast).

    Args:
        json_data: Loaded JSON map
        table_ids: List of table IDs
                   e.g., ["4.1.5.3", "9.10.14.4"] or ["Table-4.1.5.3", ...]

    Returns:
        Dict of {table_id: table_data}
        e.g., {
            "Table-4.1.5.3": {"id": "...", "markdown": "...", ...},
            "Table-9.10.14.4": {"id": "...", "markdown": "...", ...}
        }
    """
    results = {}

    for tid in table_ids:
        # Normalize ID
        normalized_id = tid if tid.startswith("Table-") else f"Table-{tid}"

        # Extract table
        result = extract_table(json_data, tid)
        results[normalized_id] = result

    return results


# Quick usage examples:
#
# 1. Extract single section from PDF:
#    text = extract_section("/path/to/obc.pdf", 127, "9.8.8.2")
#
# 2. Extract multiple sections (FASTER!):
#    texts = extract_sections_batch("/path/to/nbc.pdf", [
#        {"page": 452, "id": "4.1.3.2"},
#        {"page": 538, "id": "4.3.3.1"},
#        {"page": 537, "id": "4.2.7.2"}
#    ])
#
# 3. Search JSON:
#    import json
#    with open("OBC_Vol1.json") as f:
#        data = json.load(f)
#    results = search_json(data, "guard height stairs")
#
# 4. Extract table from JSON (NEW!):
#    table = extract_table(data, "4.1.5.3")
#    print(table["markdown"])  # Display formatted table
#
# 5. Extract multiple tables (BATCH!):
#    tables = extract_tables_batch(data, ["4.1.5.3", "9.10.14.4"])
#    for tid, table in tables.items():
#        print(f"## {table['title']}")
#        print(table['markdown'])
#
# 6. Extract table from PDF (FALLBACK!):
#    table = extract_table_from_pdf("/path/to/nbc.pdf", 452, "Table-4.1.5.3")
#    print(table["text"])
