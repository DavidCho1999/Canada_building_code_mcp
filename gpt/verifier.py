# verifier.py - GPT Building Code 응답 검증 도구
# extractor.py 재사용 + 검증 전용 함수

import re
import json
import difflib
from pathlib import Path

# extractor.py 함수 재사용
try:
    from extractor import search_json, extract_section, extract_sections_batch, extract_table
except ImportError:
    # 독립 실행 시 경로 추가
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from extractor import search_json, extract_section, extract_sections_batch, extract_table


# ========== 정규식 패턴 ==========

# **NBC Section 4.1.3.2** - Title (p.452)
SECTION_PATTERN = re.compile(
    r'\*\*(\w+)\s+Section\s+([\d\.]+)\*\*\s*[-–]\s*(.+?)\s*\(p\.?(\d+)\)',
    re.IGNORECASE
)

# **NBC Table 4.1.5.3** - Live Loads (p.452)
TABLE_PATTERN = re.compile(
    r'\*\*(\w+)\s+Table\s+([\d\.]+)\*\*\s*[-–]\s*(.+?)\s*\(p\.?(\d+)\)',
    re.IGNORECASE
)

# > "quoted text..." or > 'quoted text...'
QUOTE_PATTERN = re.compile(r'>\s*["\'](.+?)["\']', re.DOTALL)


# ========== 1. GPT 응답 파싱 ==========

def parse_gpt_response(text: str) -> list:
    """
    GPT 응답에서 섹션/테이블 참조를 파싱

    입력 형식 예시:
    **NBC Section 4.1.3.2** - Strength and Stability (p.452)
    > "A building and its structural components shall be designed..."

    **NBC Table 4.1.5.3** - Live Loads on Floors (p.452)

    반환:
    [
        {
            "type": "section",
            "code": "NBC",
            "id": "4.1.3.2",
            "title": "Strength and Stability",
            "page_claimed": 452,
            "quote": "A building and its structural components...",
            "raw_match": "원본 매치"
        }
    ]
    """
    results = []
    lines = text.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i]

        # Section 패턴 매칭
        section_match = SECTION_PATTERN.search(line)
        if section_match:
            ref = {
                "type": "section",
                "code": section_match.group(1).upper(),
                "id": section_match.group(2),
                "title": section_match.group(3).strip(),
                "page_claimed": int(section_match.group(4)),
                "quote": None,
                "raw_match": section_match.group(0)
            }

            # 다음 줄에서 인용문 찾기
            if i + 1 < len(lines):
                quote_match = QUOTE_PATTERN.search(lines[i + 1])
                if quote_match:
                    ref["quote"] = quote_match.group(1).strip()
                    i += 1

            results.append(ref)

        # Table 패턴 매칭
        table_match = TABLE_PATTERN.search(line)
        if table_match:
            ref = {
                "type": "table",
                "code": table_match.group(1).upper(),
                "id": f"Table-{table_match.group(2)}",
                "title": table_match.group(3).strip(),
                "page_claimed": int(table_match.group(4)),
                "quote": None,
                "raw_match": table_match.group(0)
            }
            results.append(ref)

        i += 1

    return results


# ========== 2. JSON 검증 ==========

def verify_reference_exists(json_data: dict, ref_type: str, ref_id: str) -> dict:
    """
    JSON에서 섹션 또는 테이블 존재 확인

    Args:
        json_data: 로드된 JSON 데이터
        ref_type: "section" | "table"
        ref_id: 섹션/테이블 ID (예: "4.1.3.2" 또는 "Table-4.1.5.3")

    Returns:
        {
            "exists": True/False,
            "data": {...} or None,
            "similar_ids": ["4.1.3.1", "4.1.3.3"]
        }
    """
    result = {
        "exists": False,
        "data": None,
        "similar_ids": []
    }

    if ref_type == "section":
        sections = json_data.get("sections", [])

        # 직접 매칭 시도
        for section in sections:
            if section.get("id") == ref_id:
                result["exists"] = True
                result["data"] = section
                return result

        # Division prefix 추가 시도 (B-4.1.3.2, A-4.1.3.2 등)
        for prefix in ["B-", "A-", "C-", ""]:
            prefixed_id = f"{prefix}{ref_id}"
            for section in sections:
                if section.get("id") == prefixed_id:
                    result["exists"] = True
                    result["data"] = section
                    result["matched_id"] = prefixed_id  # 실제 매칭된 ID 기록
                    return result

        # 유사한 ID 찾기
        result["similar_ids"] = find_similar_ids(
            [s.get("id", "") for s in sections],
            ref_id
        )

    elif ref_type == "table":
        tables = json_data.get("tables", [])
        # Table- 접두사 정규화
        normalized_id = ref_id if ref_id.startswith("Table-") else f"Table-{ref_id}"

        for table in tables:
            if table.get("id") == normalized_id:
                result["exists"] = True
                result["data"] = table
                return result

        # 유사한 ID 찾기
        result["similar_ids"] = find_similar_ids(
            [t.get("id", "") for t in tables],
            normalized_id
        )

    return result


def verify_page_match(json_data: dict, ref_type: str, ref_id: str, claimed_page: int) -> dict:
    """
    페이지 번호 일치 확인

    Returns:
        {
            "match": True/False,
            "json_page": 450,
            "claimed_page": 452,
            "difference": 2
        }
    """
    result = {
        "match": False,
        "json_page": None,
        "claimed_page": claimed_page,
        "difference": None
    }

    # 먼저 존재 확인
    ref_result = verify_reference_exists(json_data, ref_type, ref_id)
    if not ref_result["exists"]:
        return result

    json_page = ref_result["data"].get("page")
    result["json_page"] = json_page
    result["match"] = (json_page == claimed_page)
    result["difference"] = abs(json_page - claimed_page) if json_page else None

    return result


def find_similar_ids(all_ids: list, target_id: str, limit: int = 5) -> list:
    """유사한 ID 찾기 (difflib 사용)"""
    matches = difflib.get_close_matches(target_id, all_ids, n=limit, cutoff=0.6)
    return matches


# ========== 3. PDF 텍스트 검증 ==========

def verify_quote(pdf_path: str, page: int, section_id: str, claimed_quote: str) -> dict:
    """
    PDF에서 실제 텍스트 추출 후 인용문 비교

    Returns:
        {
            "match": True/False,
            "match_ratio": 0.85,
            "actual_text": "실제 추출된 텍스트",
            "claimed_quote": "GPT가 인용한 텍스트",
            "extraction_success": True/False
        }
    """
    result = {
        "match": False,
        "match_ratio": 0.0,
        "actual_text": None,
        "claimed_quote": claimed_quote,
        "extraction_success": False
    }

    if not claimed_quote:
        result["match"] = True  # 인용문 없으면 스킵
        return result

    try:
        actual_text = extract_section(pdf_path, page, section_id)
        result["actual_text"] = actual_text[:500] if actual_text else None  # 500자 제한
        result["extraction_success"] = bool(actual_text and "Error" not in actual_text)

        if result["extraction_success"]:
            result["match_ratio"] = calculate_similarity(claimed_quote, actual_text)
            result["match"] = result["match_ratio"] >= 0.7  # 70% 이상이면 일치
    except Exception as e:
        result["actual_text"] = f"Error: {e}"

    return result


def calculate_similarity(text1: str, text2: str) -> float:
    """두 텍스트의 유사도 계산 (0-1)"""
    if not text1 or not text2:
        return 0.0

    # 정규화: 소문자, 공백 정리
    t1 = ' '.join(text1.lower().split())
    t2 = ' '.join(text2.lower().split())

    # SequenceMatcher로 유사도 계산
    return difflib.SequenceMatcher(None, t1, t2).ratio()


# ========== 4. 종합 검증 ==========

def verify_gpt_response(gpt_text: str, maps_dir: str, sources_dir: str = None) -> dict:
    """
    GPT 응답 종합 검증 (메인 함수)

    Args:
        gpt_text: GPT 응답 텍스트
        maps_dir: maps/ 폴더 경로
        sources_dir: sources/ 폴더 경로 (PDF, None이면 텍스트 비교 스킵)

    Returns:
        {
            "summary": {
                "total_references": 5,
                "passed": 3,
                "issues": 2,
                "pass_rate": 0.6
            },
            "details": [...],
            "recommendations": [...]
        }
    """
    result = {
        "summary": {
            "total_references": 0,
            "passed": 0,
            "issues": 0,
            "pass_rate": 0.0
        },
        "details": [],
        "recommendations": []
    }

    # 1. GPT 응답 파싱
    references = parse_gpt_response(gpt_text)
    result["summary"]["total_references"] = len(references)

    if not references:
        result["recommendations"].append("No section/table references found in GPT response")
        return result

    # 2. 각 참조 검증
    for ref in references:
        detail = {
            "type": ref["type"],
            "code": ref["code"],
            "id": ref["id"],
            "title": ref["title"],
            "checks": {},
            "status": "PASS"
        }

        # JSON 로드
        json_path = get_code_json_path(ref["code"], maps_dir)
        if not json_path:
            detail["checks"]["json_load"] = {"pass": False, "error": f"JSON not found for {ref['code']}"}
            detail["status"] = "FAIL"
            result["details"].append(detail)
            result["summary"]["issues"] += 1
            result["recommendations"].append(f"JSON file not found for code: {ref['code']}")
            continue

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except Exception as e:
            detail["checks"]["json_load"] = {"pass": False, "error": str(e)}
            detail["status"] = "FAIL"
            result["details"].append(detail)
            result["summary"]["issues"] += 1
            continue

        has_issue = False

        # 2a. 존재 확인
        exists_result = verify_reference_exists(json_data, ref["type"], ref["id"])
        detail["checks"]["exists"] = {
            "pass": exists_result["exists"],
            "similar_ids": exists_result["similar_ids"]
        }
        if not exists_result["exists"]:
            has_issue = True
            if exists_result["similar_ids"]:
                result["recommendations"].append(
                    f"{ref['type'].title()} {ref['id']} not found. Did you mean: {', '.join(exists_result['similar_ids'][:3])}?"
                )
            else:
                result["recommendations"].append(f"{ref['type'].title()} {ref['id']} not found in {ref['code']}")

        # 2b. 페이지 확인
        page_result = verify_page_match(json_data, ref["type"], ref["id"], ref["page_claimed"])
        detail["checks"]["page"] = {
            "pass": page_result["match"],
            "json_page": page_result["json_page"],
            "claimed_page": page_result["claimed_page"]
        }
        if not page_result["match"] and page_result["json_page"]:
            has_issue = True
            result["recommendations"].append(
                f"{ref['type'].title()} {ref['id']}: Page should be {page_result['json_page']}, not {page_result['claimed_page']}"
            )

        # 2c. 텍스트 비교 (섹션만, PDF 있을 때)
        if ref["type"] == "section" and sources_dir and ref.get("quote"):
            pdf_path = get_pdf_path(ref["code"], json_data, sources_dir)
            if pdf_path:
                quote_result = verify_quote(
                    pdf_path,
                    page_result["json_page"] or ref["page_claimed"],
                    ref["id"],
                    ref["quote"]
                )
                detail["checks"]["quote"] = {
                    "pass": quote_result["match"],
                    "similarity": round(quote_result["match_ratio"], 2),
                    "extraction_success": quote_result["extraction_success"]
                }
                if not quote_result["match"] and quote_result["extraction_success"]:
                    has_issue = True
                    result["recommendations"].append(
                        f"Quote mismatch for {ref['id']} (similarity: {quote_result['match_ratio']:.0%})"
                    )

        # 상태 결정
        if has_issue:
            # 모든 체크 실패하면 FAIL, 일부만 실패하면 PARTIAL
            all_failed = all(not c.get("pass", True) for c in detail["checks"].values())
            detail["status"] = "FAIL" if all_failed else "PARTIAL"
            result["summary"]["issues"] += 1
        else:
            result["summary"]["passed"] += 1

        result["details"].append(detail)

    # 통과율 계산
    total = result["summary"]["total_references"]
    if total > 0:
        result["summary"]["pass_rate"] = result["summary"]["passed"] / total

    return result


# ========== 5. JSON 무결성 검증 ==========

def validate_json_structure(json_path: str) -> dict:
    """
    JSON 파일 구조 검증

    Returns:
        {
            "valid": True/False,
            "checks": {
                "required_keys": {"pass": True, "missing": []},
                "sections_structure": {"pass": True, "errors": []},
                "tables_structure": {"pass": True, "errors": []}
            },
            "stats": {"sections": 3000, "tables": 230}
        }
    """
    result = {
        "valid": True,
        "checks": {},
        "stats": {}
    }

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        result["valid"] = False
        result["checks"]["load"] = {"pass": False, "error": str(e)}
        return result

    # 필수 키 확인
    required_keys = ["code", "version", "sections"]
    missing = [k for k in required_keys if k not in data]
    result["checks"]["required_keys"] = {
        "pass": len(missing) == 0,
        "missing": missing
    }
    if missing:
        result["valid"] = False

    # sections 구조 확인
    sections = data.get("sections", [])
    section_errors = []
    for i, s in enumerate(sections[:100]):  # 처음 100개만 샘플 검사
        if not s.get("id"):
            section_errors.append(f"Section {i}: missing 'id'")
        if not s.get("page"):
            section_errors.append(f"Section {i} ({s.get('id', '?')}): missing 'page'")

    result["checks"]["sections_structure"] = {
        "pass": len(section_errors) == 0,
        "errors": section_errors[:10]  # 최대 10개만
    }
    result["stats"]["sections"] = len(sections)

    # tables 구조 확인
    tables = data.get("tables", [])
    table_errors = []
    for i, t in enumerate(tables[:50]):  # 처음 50개만 샘플 검사
        if not t.get("id"):
            table_errors.append(f"Table {i}: missing 'id'")
        if not t.get("markdown"):
            table_errors.append(f"Table {i} ({t.get('id', '?')}): missing 'markdown'")

    result["checks"]["tables_structure"] = {
        "pass": len(table_errors) == 0,
        "errors": table_errors[:10]
    }
    result["stats"]["tables"] = len(tables)

    if section_errors or table_errors:
        result["valid"] = False

    return result


def test_extractor_functions(json_path: str, pdf_path: str = None) -> dict:
    """
    extractor.py 함수 테스트

    Returns:
        {
            "all_pass": True/False,
            "tests": {
                "search_json": {"pass": True, "result": "5 results"},
                "extract_section": {"pass": True, "result": "extracted 500 chars"},
                "extract_table": {"pass": True, "result": "markdown found"}
            }
        }
    """
    result = {
        "all_pass": True,
        "tests": {}
    }

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        result["all_pass"] = False
        result["tests"]["load"] = {"pass": False, "error": str(e)}
        return result

    # search_json 테스트
    try:
        results = search_json(data, "guard height")
        result["tests"]["search_json"] = {
            "pass": len(results) > 0,
            "result": f"{len(results)} results found"
        }
    except Exception as e:
        result["tests"]["search_json"] = {"pass": False, "error": str(e)}
        result["all_pass"] = False

    # extract_table 테스트
    tables = data.get("tables", [])
    if tables:
        try:
            table = extract_table(data, tables[0].get("id", ""))
            has_markdown = bool(table.get("markdown"))
            result["tests"]["extract_table"] = {
                "pass": has_markdown,
                "result": f"markdown {'found' if has_markdown else 'missing'}"
            }
        except Exception as e:
            result["tests"]["extract_table"] = {"pass": False, "error": str(e)}
            result["all_pass"] = False

    # extract_section 테스트 (PDF 있을 때만)
    if pdf_path and Path(pdf_path).exists():
        sections = data.get("sections", [])
        if sections:
            test_section = sections[0]
            try:
                text = extract_section(pdf_path, test_section.get("page", 1), test_section.get("id", ""))
                has_text = bool(text and "Error" not in text)
                result["tests"]["extract_section"] = {
                    "pass": has_text,
                    "result": f"extracted {len(text) if text else 0} chars"
                }
            except Exception as e:
                result["tests"]["extract_section"] = {"pass": False, "error": str(e)}
                result["all_pass"] = False

    return result


# ========== 6. 리포트 생성 ==========

def generate_report(verification_result: dict, format: str = "markdown") -> str:
    """
    검증 결과를 Markdown 리포트로 변환
    """
    if format == "json":
        return json.dumps(verification_result, indent=2, ensure_ascii=False)

    summary = verification_result.get("summary", {})
    details = verification_result.get("details", [])
    recommendations = verification_result.get("recommendations", [])

    lines = [
        "# GPT 응답 검증 리포트\n",
        "## 요약\n",
        "| 항목 | 결과 |",
        "|------|------|",
        f"| 총 참조 수 | {summary.get('total_references', 0)} |",
        f"| 검증 통과 | {summary.get('passed', 0)} |",
        f"| 문제 발견 | {summary.get('issues', 0)} |",
        f"| 통과율 | {summary.get('pass_rate', 0):.0%} |",
        "\n---\n",
        "## 상세 결과\n"
    ]

    for i, detail in enumerate(details, 1):
        status_emoji = {"PASS": "\u2705", "PARTIAL": "\u26a0\ufe0f", "FAIL": "\u274c"}.get(detail.get("status"), "\u2753")

        lines.append(f"### {i}. {detail.get('code', '')} {detail.get('type', '').title()} {detail.get('id', '')}")
        lines.append(f"**{detail.get('title', '')}**\n")
        lines.append("| 검증 항목 | 결과 | 상세 |")
        lines.append("|----------|------|------|")

        checks = detail.get("checks", {})

        # 존재 확인
        if "exists" in checks:
            c = checks["exists"]
            emoji = "\u2705" if c.get("pass") else "\u274c"
            extra = ""
            if not c.get("pass") and c.get("similar_ids"):
                extra = f" (유사: {', '.join(c['similar_ids'][:2])})"
            lines.append(f"| 존재 확인 | {emoji} | {'JSON 확인' if c.get('pass') else '찾을 수 없음'}{extra} |")

        # 페이지 확인
        if "page" in checks:
            c = checks["page"]
            emoji = "\u2705" if c.get("pass") else "\u26a0\ufe0f"
            if c.get("pass"):
                lines.append(f"| 페이지 | {emoji} | {c.get('json_page', '?')} |")
            else:
                lines.append(f"| 페이지 | {emoji} | JSON: {c.get('json_page', '?')}, GPT: {c.get('claimed_page', '?')} |")

        # 텍스트 비교
        if "quote" in checks:
            c = checks["quote"]
            emoji = "\u2705" if c.get("pass") else "\u26a0\ufe0f"
            sim = c.get("similarity", 0)
            lines.append(f"| 텍스트 비교 | {emoji} | 유사도: {sim:.0%} |")

        lines.append(f"\n**상태:** {status_emoji} {detail.get('status', 'UNKNOWN')}\n")

    # 권장 조치
    if recommendations:
        lines.append("---\n")
        lines.append("## 권장 조치\n")
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")

    lines.append("\n---\n")
    lines.append("*Generated by gpt-verify skill*")

    return '\n'.join(lines)


# ========== 7. 유틸리티 ==========

# Code → JSON 파일 매핑
CODE_JSON_MAP = {
    "NBC": "NBC2025.json",
    "NFC": "NFC2025.json",
    "NPC": "NPC2025.json",
    "NECB": "NECB2025.json",
    "OBC": "OBC_Vol1.json",  # 기본값 Vol1
    "OFC": "OFC.json",
    "BCBC": "BCBC2024.json",
    "ABC": "ABC2023.json",
    "QCC": "QCC2020.json",
    "QECB": "QECB2020.json",
    "QPC": "QPC2020.json",
    "QSC": "QSC2020.json",
}

# Code → PDF 파일 매핑
CODE_PDF_MAP = {
    "NBC": "NBC2025p1.pdf",
    "NFC": "NFC2025p1.pdf",
    "NPC": "NPC2025p1.pdf",
    "NECB": "NECB2025p1.pdf",
    "OBC": "obc volume 1.pdf",
    "OFC": "OFC_2024.pdf",
    "BCBC": "bcbc_2024_web_version_20240409.pdf",
    "ABC": "2023NBCAE-V1_National_Building_Code2023_Alberta_Edition.pdf",
}


def get_code_json_path(code_name: str, maps_dir: str) -> str:
    """코드명에서 JSON 파일 경로 반환"""
    code_upper = code_name.upper()
    json_file = CODE_JSON_MAP.get(code_upper)

    if not json_file:
        return None

    path = Path(maps_dir) / json_file
    return str(path) if path.exists() else None


def get_pdf_path(code_name: str, json_data: dict, sources_dir: str) -> str:
    """코드명에서 PDF 파일 경로 반환"""
    code_upper = code_name.upper()

    # JSON에서 source_pdf 확인
    source_pdf = json_data.get("source_pdf", {}).get("filename")
    if source_pdf:
        path = Path(sources_dir) / source_pdf
        if path.exists():
            return str(path)

    # 매핑 테이블에서 찾기
    pdf_file = CODE_PDF_MAP.get(code_upper)
    if pdf_file:
        path = Path(sources_dir) / pdf_file
        if path.exists():
            return str(path)

    return None


# ========== CLI 실행 ==========

if __name__ == "__main__":
    # 간단한 테스트
    test_text = """
**NBC Section 4.1.3.2** - Strength and Stability (p.452)
> "A building and its structural components shall be designed to have sufficient structural capacity."

**NBC Table 4.1.5.3** - Live Loads on Floors (p.460)
"""

    print("=== Parse Test ===")
    refs = parse_gpt_response(test_text)
    for r in refs:
        print(f"  {r['type']}: {r['code']} {r['id']} (p.{r['page_claimed']})")

    print("\n=== JSON Validation Test ===")
    import sys
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
        result = validate_json_structure(json_path)
        print(f"  Valid: {result['valid']}")
        print(f"  Sections: {result['stats'].get('sections', 0)}")
        print(f"  Tables: {result['stats'].get('tables', 0)}")
