"""
Injection - MD 파일에 수정된 테이블 주입
"""

import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class InjectionResult:
    """주입 결과"""
    success: bool
    table_id: str
    message: str
    lines_replaced: int = 0


def inject_table(
    md_path: str,
    table_id: str,
    new_content: str,
    start_line: int,
    end_line: int,
    backup: bool = True
) -> InjectionResult:
    """
    MD 파일의 특정 구간을 새 테이블로 교체

    Args:
        md_path: MD 파일 경로
        table_id: 테이블 ID
        new_content: 새 테이블 내용 (마크다운 또는 HTML)
        start_line: 시작 줄 번호 (0-indexed)
        end_line: 끝 줄 번호 (0-indexed, exclusive)
        backup: 백업 파일 생성 여부

    Returns:
        InjectionResult
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 범위 검증
        if start_line < 0 or end_line > len(lines) or start_line >= end_line:
            return InjectionResult(
                success=False,
                table_id=table_id,
                message=f"Invalid line range: {start_line}-{end_line}"
            )

        # 백업 생성
        if backup:
            backup_path = md_path + ".bak"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

        # 테이블 헤딩 보존 (### Table X.X.X.X ...)
        header_lines = []
        for i in range(start_line, min(start_line + 3, end_line)):
            if lines[i].strip().startswith('#'):
                header_lines.append(lines[i])
            else:
                break

        # 새 내용 구성
        new_lines = header_lines + ['\n', new_content, '\n\n']

        # 교체
        lines_replaced = end_line - start_line
        lines[start_line:end_line] = new_lines

        # 저장
        with open(md_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        return InjectionResult(
            success=True,
            table_id=table_id,
            message=f"Replaced {lines_replaced} lines",
            lines_replaced=lines_replaced
        )

    except Exception as e:
        return InjectionResult(
            success=False,
            table_id=table_id,
            message=f"Error: {str(e)}"
        )


def inject_by_table_id(
    md_path: str,
    table_id: str,
    new_content: str,
    backup: bool = True
) -> InjectionResult:
    """
    테이블 ID로 자동으로 위치를 찾아서 교체

    Args:
        md_path: MD 파일 경로
        table_id: 테이블 ID (예: "Table 9.10.14.4")
        new_content: 새 테이블 내용
        backup: 백업 파일 생성 여부
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 테이블 ID 패턴
        # 예: ### Table 9.10.14.4 또는 #### Table 9.10.14.4-A
        table_num = table_id.replace("Table ", "")
        pattern = rf'^#{2,4}\s+Table\s+{re.escape(table_num)}\b'

        start_line = None
        end_line = None

        for i, line in enumerate(lines):
            if re.match(pattern, line):
                start_line = i
                # 끝 찾기
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
                break

        if start_line is None:
            return InjectionResult(
                success=False,
                table_id=table_id,
                message=f"Table not found: {table_id}"
            )

        return inject_table(
            md_path=md_path,
            table_id=table_id,
            new_content=new_content,
            start_line=start_line,
            end_line=end_line,
            backup=backup
        )

    except Exception as e:
        return InjectionResult(
            success=False,
            table_id=table_id,
            message=f"Error: {str(e)}"
        )


def preview_injection(
    md_path: str,
    table_id: str,
    new_content: str,
    context_lines: int = 3
) -> str:
    """
    교체 전 미리보기 생성

    Returns:
        교체 전후 비교 문자열
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        table_num = table_id.replace("Table ", "")
        pattern = rf'^#{2,4}\s+Table\s+{re.escape(table_num)}\b'

        for i, line in enumerate(lines):
            if re.match(pattern, line):
                # 현재 내용
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

                old_content = ''.join(lines[i:j])

                preview = []
                preview.append("=" * 60)
                preview.append(f"Table: {table_id}")
                preview.append(f"Lines: {i}-{j}")
                preview.append("=" * 60)
                preview.append("\n--- BEFORE ---")
                preview.append(old_content[:500] + "..." if len(old_content) > 500 else old_content)
                preview.append("\n--- AFTER ---")
                preview.append(new_content[:500] + "..." if len(new_content) > 500 else new_content)
                preview.append("=" * 60)

                return '\n'.join(preview)

        return f"Table not found: {table_id}"

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: python injection.py <md_path> <table_id> <new_content_file>")
        print("       python injection.py --preview <md_path> <table_id>")
        sys.exit(1)

    if sys.argv[1] == "--preview":
        md_path = sys.argv[2]
        table_id = sys.argv[3]
        print(preview_injection(md_path, table_id, "[New content would go here]"))
    else:
        md_path = sys.argv[1]
        table_id = sys.argv[2]
        content_file = sys.argv[3]

        with open(content_file, 'r', encoding='utf-8') as f:
            new_content = f.read()

        result = inject_by_table_id(md_path, table_id, new_content)
        print(f"{result.table_id}: {'OK' if result.success else 'FAILED'} - {result.message}")
