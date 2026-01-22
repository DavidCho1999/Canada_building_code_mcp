"""
Surgery - pdfplumber로 깨진 테이블 재추출
"""

import pdfplumber
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class ExtractedTable:
    """추출된 테이블 데이터"""
    table_id: str
    page_num: int
    headers: List[str]
    rows: List[List[str]]
    raw_data: List[List[str]]  # 원본 데이터


def extract_table_from_pdf(
    pdf_path: str,
    page_num: int,
    table_id: str = ""
) -> Optional[ExtractedTable]:
    """
    특정 페이지에서 테이블 추출

    Args:
        pdf_path: PDF 파일 경로
        page_num: 페이지 번호 (1-indexed)
        table_id: 테이블 ID (로깅용)

    Returns:
        ExtractedTable 또는 None
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_num < 1 or page_num > len(pdf.pages):
                print(f"Invalid page number: {page_num}")
                return None

            page = pdf.pages[page_num - 1]  # 0-indexed
            tables = page.extract_tables()

            if not tables:
                print(f"No tables found on page {page_num}")
                return None

            # 첫 번째 테이블 사용 (대부분 한 페이지에 테이블 하나)
            raw_data = tables[0]

            if not raw_data or len(raw_data) < 2:
                print(f"Table too small on page {page_num}")
                return None

            # 헤더와 데이터 분리
            headers = [cell or "" for cell in raw_data[0]]
            rows = [[cell or "" for cell in row] for row in raw_data[1:]]

            return ExtractedTable(
                table_id=table_id,
                page_num=page_num,
                headers=headers,
                rows=rows,
                raw_data=raw_data
            )

    except Exception as e:
        print(f"Error extracting table from page {page_num}: {e}")
        return None


def extract_multipage_table(
    pdf_path: str,
    start_page: int,
    end_page: int,
    table_id: str = ""
) -> Optional[ExtractedTable]:
    """
    여러 페이지에 걸친 테이블 추출 및 병합

    Multi-page 테이블 처리:
    - 첫 페이지: 헤더 + 데이터
    - 나머지 페이지: 데이터만 (헤더 반복 제거)
    """
    all_rows = []
    headers = None

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num in range(start_page, end_page + 1):
                if page_num < 1 or page_num > len(pdf.pages):
                    continue

                page = pdf.pages[page_num - 1]
                tables = page.extract_tables()

                if not tables:
                    continue

                raw_data = tables[0]

                if headers is None:
                    # 첫 페이지: 헤더 저장
                    headers = [cell or "" for cell in raw_data[0]]
                    rows = [[cell or "" for cell in row] for row in raw_data[1:]]
                else:
                    # 이후 페이지: 헤더가 반복되면 스킵
                    first_row = [cell or "" for cell in raw_data[0]]
                    if first_row == headers:
                        rows = [[cell or "" for cell in row] for row in raw_data[1:]]
                    else:
                        rows = [[cell or "" for cell in row] for row in raw_data]

                all_rows.extend(rows)

        if headers is None:
            return None

        return ExtractedTable(
            table_id=table_id,
            page_num=start_page,
            headers=headers,
            rows=all_rows,
            raw_data=[headers] + all_rows
        )

    except Exception as e:
        print(f"Error extracting multipage table: {e}")
        return None


def table_to_markdown(table: ExtractedTable) -> str:
    """
    ExtractedTable을 마크다운 테이블 문자열로 변환
    """
    lines = []

    # 헤더
    header_line = "| " + " | ".join(table.headers) + " |"
    lines.append(header_line)

    # 구분선
    separator = "|" + "|".join(["---"] * len(table.headers)) + "|"
    lines.append(separator)

    # 데이터 행
    for row in table.rows:
        # 열 개수 맞추기
        padded_row = row + [""] * (len(table.headers) - len(row))
        row_line = "| " + " | ".join(padded_row[:len(table.headers)]) + " |"
        lines.append(row_line)

    return "\n".join(lines)


def table_to_html(table: ExtractedTable) -> str:
    """
    ExtractedTable을 HTML 테이블로 변환
    """
    lines = ['<table class="obc-table">']

    # 헤더
    lines.append('  <thead>')
    lines.append('    <tr>')
    for header in table.headers:
        lines.append(f'      <th>{header}</th>')
    lines.append('    </tr>')
    lines.append('  </thead>')

    # 바디
    lines.append('  <tbody>')
    for row in table.rows:
        lines.append('    <tr>')
        for i, cell in enumerate(row):
            if i < len(table.headers):
                lines.append(f'      <td>{cell}</td>')
        lines.append('    </tr>')
    lines.append('  </tbody>')

    lines.append('</table>')

    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python surgery.py <pdf_path> <page_num> [table_id]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    page_num = int(sys.argv[2])
    table_id = sys.argv[3] if len(sys.argv) > 3 else ""

    table = extract_table_from_pdf(pdf_path, page_num, table_id)

    if table:
        print(f"Extracted table from page {page_num}:")
        print(f"  Headers: {table.headers}")
        print(f"  Rows: {len(table.rows)}")
        print()
        print("Markdown output:")
        print(table_to_markdown(table))
    else:
        print("Failed to extract table")
