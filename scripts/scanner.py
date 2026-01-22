"""
Scanner - MD 파일에서 테이블 구간 탐지
"""

import re
from pathlib import Path
from dataclasses import dataclass
from typing import List


@dataclass
class TableLocation:
    """테이블 위치 정보"""
    table_id: str
    start_line: int
    end_line: int
    content: str
    page_num: int = 0  # Index에서 나중에 채움


def scan_tables(md_path: str) -> List[TableLocation]:
    """
    MD 파일에서 모든 테이블 구간을 찾습니다.

    패턴:
    - ### Table X.X.X.X 또는 #### Table X.X.X.X
    - |로 시작하는 마크다운 테이블
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    tables = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # 테이블 헤딩 찾기
        table_match = re.match(r'^#{2,4}\s+(Table\s+\d+\.\d+\.\d+\.\d+[A-Z]?(?:-[A-Z])?)', line)

        if table_match:
            table_id = table_match.group(1)
            start_line = i

            # 테이블 끝 찾기 (다음 헤딩 또는 빈 줄 2개)
            j = i + 1
            empty_count = 0

            while j < len(lines):
                if lines[j].startswith('#'):
                    break
                if lines[j].strip() == '':
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0
                j += 1

            end_line = j
            content = ''.join(lines[start_line:end_line])

            tables.append(TableLocation(
                table_id=table_id,
                start_line=start_line,
                end_line=end_line,
                content=content
            ))

            i = j
        else:
            i += 1

    return tables


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scanner.py <md_path>")
        sys.exit(1)

    md_path = sys.argv[1]
    tables = scan_tables(md_path)

    print(f"Found {len(tables)} tables:\n")
    for t in tables:
        print(f"  {t.table_id}")
        print(f"    Lines: {t.start_line}-{t.end_line}")
        print(f"    Content length: {len(t.content)} chars")
        print()
