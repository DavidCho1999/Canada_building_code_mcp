"""
Smart Hybrid Pipeline - Marker + pdfplumber 통합 파이프라인
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from index_builder import build_table_index, load_index
from scanner import scan_tables, TableLocation
from judge import judge_table, TableQuality, BrokenReason
from surgery import extract_table_from_pdf, extract_multipage_table, table_to_markdown, table_to_html
from injection import inject_by_table_id, InjectionResult


@dataclass
class PipelineResult:
    """파이프라인 실행 결과"""
    total_tables: int = 0
    ok_tables: int = 0
    fixed_tables: int = 0
    failed_tables: int = 0
    details: List[str] = field(default_factory=list)


@dataclass
class PipelineConfig:
    """파이프라인 설정"""
    pdf_path: str
    md_path: str
    meta_json_path: Optional[str] = None
    index_path: Optional[str] = None
    output_format: str = "markdown"  # "markdown" or "html"
    dry_run: bool = False
    verbose: bool = True


def run_pipeline(config: PipelineConfig) -> PipelineResult:
    """
    Smart Hybrid Pipeline 실행

    단계:
    1. INDEX: meta.json에서 Table→Page 인덱스 빌드
    2. SCAN: MD에서 테이블 구간 탐지
    3. JUDGE: 6가지 기준으로 품질 검사
    4. SURGERY: 깨진 테이블만 pdfplumber로 재추출
    5. INJECT: 수정된 테이블 주입
    """
    result = PipelineResult()

    # Step 1: INDEX
    if config.verbose:
        print("\n[1/5] Building table index...")

    if config.index_path and Path(config.index_path).exists():
        table_index = load_index(config.index_path)
    elif config.meta_json_path and Path(config.meta_json_path).exists():
        table_index = build_table_index(config.meta_json_path)
    else:
        print("Warning: No index available. Page lookup will fail.")
        table_index = {}

    if config.verbose:
        print(f"   Index: {len(table_index)} tables mapped")

    # Step 2: SCAN
    if config.verbose:
        print("\n[2/5] Scanning MD for tables...")

    tables = scan_tables(config.md_path)
    result.total_tables = len(tables)

    if config.verbose:
        print(f"   Found: {len(tables)} tables")

    # Step 3: JUDGE
    if config.verbose:
        print("\n[3/5] Judging table quality...")

    broken_tables = []
    ok_tables = []

    for table in tables:
        quality = judge_table(table.content, table.table_id)

        # 인덱스에서 페이지 번호 채우기
        if table.table_id in table_index:
            table.page_num = table_index[table.table_id]

        if quality.is_broken:
            broken_tables.append((table, quality))
            if config.verbose:
                reasons = ", ".join(r.name for r in quality.reasons)
                print(f"   ❌ {table.table_id}: {reasons}")
        else:
            ok_tables.append(table)
            result.ok_tables += 1

    if config.verbose:
        print(f"\n   OK: {len(ok_tables)}, Broken: {len(broken_tables)}")

    # Step 4 & 5: SURGERY + INJECT
    if config.verbose:
        print("\n[4/5] Fixing broken tables with pdfplumber...")
        print("[5/5] Injecting fixed tables...")

    for table, quality in broken_tables:
        if table.page_num == 0:
            result.failed_tables += 1
            result.details.append(f"❌ {table.table_id}: No page number")
            if config.verbose:
                print(f"   ⚠️  {table.table_id}: No page number, skipping")
            continue

        # Multi-page 테이블 처리
        if BrokenReason.DUPLICATE_HEADER in quality.reasons:
            # 여러 페이지 추출 시도 (최대 5페이지)
            extracted = extract_multipage_table(
                config.pdf_path,
                table.page_num,
                table.page_num + 4,
                table.table_id
            )
        else:
            extracted = extract_table_from_pdf(
                config.pdf_path,
                table.page_num,
                table.table_id
            )

        if extracted is None:
            result.failed_tables += 1
            result.details.append(f"❌ {table.table_id}: Extraction failed")
            if config.verbose:
                print(f"   ❌ {table.table_id}: pdfplumber extraction failed")
            continue

        # 포맷 변환
        if config.output_format == "html":
            new_content = table_to_html(extracted)
        else:
            new_content = table_to_markdown(extracted)

        # 주입
        if config.dry_run:
            result.fixed_tables += 1
            result.details.append(f"✅ {table.table_id}: Would fix (dry-run)")
            if config.verbose:
                print(f"   🔧 {table.table_id}: Would fix (dry-run)")
        else:
            inject_result = inject_by_table_id(
                config.md_path,
                table.table_id,
                new_content,
                backup=True
            )

            if inject_result.success:
                result.fixed_tables += 1
                result.details.append(f"✅ {table.table_id}: Fixed")
                if config.verbose:
                    print(f"   ✅ {table.table_id}: Fixed ({inject_result.lines_replaced} lines)")
            else:
                result.failed_tables += 1
                result.details.append(f"❌ {table.table_id}: {inject_result.message}")
                if config.verbose:
                    print(f"   ❌ {table.table_id}: {inject_result.message}")

    return result


def print_summary(result: PipelineResult):
    """결과 요약 출력"""
    print("\n" + "=" * 50)
    print("PIPELINE SUMMARY")
    print("=" * 50)
    print(f"Total tables:  {result.total_tables}")
    print(f"OK (no fix):   {result.ok_tables}")
    print(f"Fixed:         {result.fixed_tables}")
    print(f"Failed:        {result.failed_tables}")
    print("=" * 50)

    if result.failed_tables > 0:
        print("\nFailed tables:")
        for detail in result.details:
            if detail.startswith("❌"):
                print(f"  {detail}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Smart Hybrid Pipeline")
    parser.add_argument("pdf_path", help="PDF file path")
    parser.add_argument("md_path", help="Marker output MD file path")
    parser.add_argument("--meta", help="Marker meta.json path")
    parser.add_argument("--index", help="Pre-built index JSON path")
    parser.add_argument("--format", choices=["markdown", "html"], default="markdown",
                        help="Output format (default: markdown)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't actually modify files")
    parser.add_argument("--quiet", action="store_true",
                        help="Minimal output")

    args = parser.parse_args()

    config = PipelineConfig(
        pdf_path=args.pdf_path,
        md_path=args.md_path,
        meta_json_path=args.meta,
        index_path=args.index,
        output_format=args.format,
        dry_run=args.dry_run,
        verbose=not args.quiet
    )

    result = run_pipeline(config)
    print_summary(result)
