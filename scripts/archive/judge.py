"""
Judge - 테이블 품질 판별 (6가지 기준)
"""

import re
from dataclasses import dataclass, field
from typing import List
from enum import Enum


class BrokenReason(Enum):
    NO_PIPES = "Flat text (no markdown table)"
    COL_MISMATCH = "Column count mismatch"
    EMPTY_CELLS = "Too many empty cells (>25%)"
    ROWSPAN_BROKEN = "Rowspan structure broken"
    NO_DATA = "No data rows"
    DUPLICATE_HEADER = "Multi-page split"
    TRUNCATED = "Content truncated"


@dataclass
class TableQuality:
    table_id: str
    is_broken: bool
    reasons: List[BrokenReason] = field(default_factory=list)
    details: List[str] = field(default_factory=list)
    confidence: float = 0.9

    @property
    def summary(self) -> str:
        if not self.is_broken:
            return f"✅ {self.table_id}: OK"
        reasons_str = ", ".join(r.name for r in self.reasons)
        return f"❌ {self.table_id}: {reasons_str}"


def judge_table(content: str, table_id: str = "") -> TableQuality:
    """
    마크다운 테이블 품질 판별 (6가지 기준)

    깨진 테이블 징후:
    1. 파이프(|) 없음 → Flat Text
    2. 열 개수 불일치 → 구조 깨짐
    3. 빈 셀 25%+ → 데이터 손실
    4. 첫 열 연속 빈칸 → Rowspan 깨짐
    5. 데이터 행 없음 → 헤더만 있음
    6. 중복 헤더 → Multi-page 분리
    """
    result = TableQuality(table_id=table_id, is_broken=False)

    lines = content.strip().split('\n')
    table_lines = [l for l in lines if '|' in l and not l.strip().startswith('#')]

    # 1. Flat Text 감지 (파이프 없음)
    if len(table_lines) < 2:
        result.is_broken = True
        result.reasons.append(BrokenReason.NO_PIPES)
        result.details.append(f"Only {len(table_lines)} lines with pipes")
        result.confidence = 0.95
        return result

    # 2. 열 개수 일관성
    col_counts = [l.count('|') - 1 for l in table_lines]
    if col_counts:
        variance = max(col_counts) - min(col_counts)
        if variance > 1:
            result.is_broken = True
            result.reasons.append(BrokenReason.COL_MISMATCH)
            result.details.append(f"Columns vary: {min(col_counts)}~{max(col_counts)}")

    # 3. 빈 셀 비율 (25% 이상이면 의심)
    total_pipes = content.count('|')
    empty_patterns = content.count('| |') + content.count('||') + content.count('|  |')
    if total_pipes > 10:
        empty_ratio = empty_patterns / (total_pipes / 2)
        if empty_ratio > 0.25:
            result.is_broken = True
            result.reasons.append(BrokenReason.EMPTY_CELLS)
            result.details.append(f"Empty cell ratio: {empty_ratio:.0%}")

    # 4. Rowspan 깨짐 (첫 열이 연속으로 빈 경우)
    if len(table_lines) > 3:
        first_cells = []
        for line in table_lines[2:]:  # 헤더+구분선 제외
            parts = line.split('|')
            if len(parts) > 1:
                first_cells.append(parts[1].strip())

        if first_cells:
            empty_first = sum(1 for c in first_cells if c == '')
            if empty_first / len(first_cells) > 0.4:
                result.is_broken = True
                result.reasons.append(BrokenReason.ROWSPAN_BROKEN)
                result.details.append(f"{empty_first}/{len(first_cells)} empty first cells")

    # 5. 데이터 행 부족
    data_rows = len(table_lines) - 2
    if data_rows < 1:
        result.is_broken = True
        result.reasons.append(BrokenReason.NO_DATA)
        result.details.append("Header only, no data")

    # 6. 중복 헤더 (Multi-page 분리)
    if table_lines:
        header = table_lines[0]
        header_count = sum(1 for l in table_lines if l == header)
        if header_count > 1:
            result.is_broken = True
            result.reasons.append(BrokenReason.DUPLICATE_HEADER)
            result.details.append(f"Header repeated {header_count} times")

    # 7. 내용 잘림 감지
    if '...' in content or 'truncated' in content.lower():
        result.is_broken = True
        result.reasons.append(BrokenReason.TRUNCATED)

    # Confidence 계산
    if result.is_broken:
        result.confidence = min(0.5 + len(result.reasons) * 0.12, 0.95)

    return result


if __name__ == "__main__":
    # 테스트
    test_good = """
### Table 9.10.14.4 Maximum Area

| Distance | Residential | Other |
|----------|-------------|-------|
| 1.2 m    | 0.2         | 0.1   |
| 2.0 m    | 0.5         | 0.3   |
"""

    test_broken = """
### Table 9.10.14.4 Maximum Area

| Distance | Residential | Other |
|----------|-------------|-------|
|          | 0.2         | 0.1   |
|          | 0.5         |       |
|          |             |       |
"""

    print("Good table:")
    result = judge_table(test_good, "Table 9.10.14.4")
    print(f"  {result.summary}")

    print("\nBroken table:")
    result = judge_table(test_broken, "Table 9.10.14.4")
    print(f"  {result.summary}")
    print(f"  Details: {result.details}")
