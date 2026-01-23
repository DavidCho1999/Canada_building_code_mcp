"""
Batch Process - 여러 PDF를 일괄 처리
"""

import subprocess
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
import time


@dataclass
class BatchConfig:
    """배치 처리 설정"""
    sources_dir: str = "sources"
    marker_dir: str = "marker"
    output_dir: str = "output"
    run_marker: bool = True
    run_pipeline: bool = True
    dry_run: bool = False


@dataclass
class BatchResult:
    """배치 처리 결과"""
    pdf_name: str
    marker_success: bool = False
    pipeline_success: bool = False
    tables_total: int = 0
    tables_fixed: int = 0
    error_message: str = ""
    skipped: bool = False


def normalize_folder_name(name: str) -> str:
    """폴더명 정규화: 공백→언더스코어, 소문자"""
    return name.lower().replace(" ", "_")


def is_already_processed(marker_dir: str, pdf_name: str) -> bool:
    """marker/ 폴더에 이미 출력물 있으면 True"""
    pdf_stem = normalize_folder_name(Path(pdf_name).stem)
    marker_path = Path(marker_dir) / pdf_stem
    if marker_path.exists():
        md_files = list(marker_path.glob("*.md"))
        meta_files = list(marker_path.glob("*_meta.json"))
        return bool(md_files and meta_files)
    return False


def get_processing_order(pdf_files: List[Path]) -> List[Path]:
    """
    처리 순서 지정:
    1. National (NBC, NFC, NPC, NECB)
    2. BC (BCBC)
    3. Alberta (ABC/NBCAE)
    4. 나머지 Provincial (OBC, QCC, QECB, QPC, QSC)
    5. User Guides (UGP4, UGNECB, IUGP9)
    """
    # (패턴, 우선순위) - 순서대로 매칭, 먼저 매칭되면 사용
    order_rules = [
        # National (1-4) - 정확한 패턴
        ('nbc2025', 1),
        ('nfc2025', 2),
        ('npc2025', 3),
        ('necb2025', 4),
        # BC (5)
        ('bcbc', 5),
        # Alberta (6)
        ('nbcae', 6),
        # Provincial (7-11)
        ('obc', 7),
        ('qcc', 8),
        ('qecb', 9),
        ('qpc', 10),
        ('qsc', 11),
        # User Guides (12-14)
        ('ugp4', 12),
        ('ugnecb', 13),
        ('iugp9', 14),
        ('ugp9', 14),
    ]

    def get_priority(pdf_path: Path) -> int:
        name_lower = pdf_path.stem.lower()
        for pattern, priority in order_rules:
            if pattern in name_lower:
                return priority
        return 99  # 알 수 없는 파일은 마지막

    return sorted(pdf_files, key=get_priority)


def run_marker(pdf_path: str, output_dir: str) -> bool:
    """
    Marker PDF 파서 실행

    Returns:
        성공 여부
    """
    try:
        # marker_single 경로 (Windows Python Scripts)
        marker_exe = r"C:\Users\A\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\marker_single.exe"

        cmd = [
            marker_exe,
            pdf_path,
            "--output_dir", output_dir,
            "--output_format", "markdown"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10800  # 3시간 타임아웃
        )

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"Marker timeout for {pdf_path}")
        return False
    except FileNotFoundError:
        print("Marker not installed. Run: pip install marker-pdf")
        return False
    except Exception as e:
        print(f"Marker error: {e}")
        return False


def find_marker_outputs(marker_dir: str, pdf_name: str) -> Dict[str, str]:
    """
    Marker 출력 파일 찾기

    Returns:
        {"md": "path/to/file.md", "meta": "path/to/meta.json"}
    """
    marker_path = Path(marker_dir)
    pdf_stem = normalize_folder_name(Path(pdf_name).stem)

    # Marker는 보통 pdf_name/ 하위에 출력
    possible_dirs = [
        marker_path / pdf_stem,
        marker_path,
    ]

    result = {"md": None, "meta": None}

    for dir_path in possible_dirs:
        if not dir_path.exists():
            continue

        # MD 파일 찾기
        md_files = list(dir_path.glob("*.md"))
        if md_files:
            result["md"] = str(md_files[0])

        # meta.json 찾기
        meta_files = list(dir_path.glob("*_meta.json")) + list(dir_path.glob("meta.json"))
        if meta_files:
            result["meta"] = str(meta_files[0])

        if result["md"] and result["meta"]:
            break

    return result


def process_single_pdf(
    pdf_path: str,
    config: BatchConfig
) -> BatchResult:
    """단일 PDF 처리"""
    pdf_name = Path(pdf_path).name
    result = BatchResult(pdf_name=pdf_name)

    print(f"\n{'='*60}")
    print(f"Processing: {pdf_name}")
    print(f"{'='*60}")

    # Step 1: Marker 실행
    if config.run_marker:
        print("\n[Marker] Converting PDF to Markdown...")
        marker_output = Path(config.marker_dir) / normalize_folder_name(Path(pdf_path).stem)

        if config.dry_run:
            print("  (dry-run) Would run marker")
            result.marker_success = True
        else:
            result.marker_success = run_marker(pdf_path, str(marker_output))

        if not result.marker_success:
            result.error_message = "Marker failed"
            return result
    else:
        result.marker_success = True

    # Step 2: Marker 출력 찾기
    outputs = find_marker_outputs(config.marker_dir, pdf_name)

    if not outputs["md"]:
        result.error_message = "MD file not found"
        return result

    # Step 3: Hybrid Pipeline 실행
    if config.run_pipeline:
        print("\n[Pipeline] Running hybrid pipeline...")

        from smart_hybrid_pipeline import run_pipeline, PipelineConfig, print_summary

        pipeline_config = PipelineConfig(
            pdf_path=pdf_path,
            md_path=outputs["md"],
            meta_json_path=outputs["meta"],
            output_format="markdown",
            dry_run=config.dry_run,
            verbose=True
        )

        pipeline_result = run_pipeline(pipeline_config)
        print_summary(pipeline_result)

        result.pipeline_success = True
        result.tables_total = pipeline_result.total_tables
        result.tables_fixed = pipeline_result.fixed_tables

    return result


def batch_process(config: BatchConfig) -> List[BatchResult]:
    """
    sources/ 폴더의 모든 PDF 일괄 처리
    """
    # 절대 경로로 변환 (marker_single이 상대 경로 처리 못함)
    sources_path = Path(config.sources_dir).resolve()
    marker_dir_abs = str(Path(config.marker_dir).resolve())
    config.marker_dir = marker_dir_abs

    if not sources_path.exists():
        print(f"Sources directory not found: {config.sources_dir}")
        return []

    pdf_files = list(sources_path.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {config.sources_dir}")
        return []

    # 처리 순서 정렬
    pdf_files = get_processing_order(pdf_files)

    print(f"Found {len(pdf_files)} PDF files")
    print("\nProcessing order:")
    for i, pdf in enumerate(pdf_files, 1):
        print(f"  {i:2d}. {pdf.name}")

    results = []
    start_time = time.time()

    skipped_count = 0
    for i, pdf_path in enumerate(pdf_files, 1):
        # 이미 처리된 파일 건너뛰기
        if config.run_marker and is_already_processed(config.marker_dir, pdf_path.name):
            print(f"\n[{i}/{len(pdf_files)}] [SKIP] Already processed: {pdf_path.name}")
            result = BatchResult(pdf_name=pdf_path.name, skipped=True, marker_success=True)
            results.append(result)
            skipped_count += 1
            continue

        print(f"\n[{i}/{len(pdf_files)}]")
        result = process_single_pdf(str(pdf_path), config)
        results.append(result)

    elapsed = time.time() - start_time

    # 최종 요약
    print("\n" + "="*60)
    print("BATCH SUMMARY")
    print("="*60)
    print(f"Total PDFs:     {len(results)}")
    print(f"Skipped:        {skipped_count}")
    print(f"Marker OK:      {sum(1 for r in results if r.marker_success and not r.skipped)}")
    print(f"Pipeline OK:    {sum(1 for r in results if r.pipeline_success)}")
    print(f"Tables fixed:   {sum(r.tables_fixed for r in results)}")
    print(f"Time elapsed:   {elapsed:.1f}s")
    print("="*60)

    # 실패 목록 (skipped 제외)
    failed = [r for r in results if not r.skipped and (not r.marker_success or not r.pipeline_success)]
    if failed:
        print("\nFailed:")
        for r in failed:
            print(f"  - {r.pdf_name}: {r.error_message}")

    return results


def save_batch_report(results: List[BatchResult], output_path: str):
    """배치 결과를 JSON으로 저장"""
    report = []
    for r in results:
        report.append({
            "pdf": r.pdf_name,
            "marker": r.marker_success,
            "pipeline": r.pipeline_success,
            "tables_total": r.tables_total,
            "tables_fixed": r.tables_fixed,
            "error": r.error_message
        })

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nReport saved: {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch PDF Processing")
    parser.add_argument("mode", nargs="?", default="all",
                        choices=["all", "marker", "pipeline"],
                        help="Processing mode")
    parser.add_argument("--sources", default="sources",
                        help="PDF sources directory")
    parser.add_argument("--marker-dir", default="marker",
                        help="Marker output directory")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't modify files")
    parser.add_argument("--report", default="batch_report.json",
                        help="Output report path")

    args = parser.parse_args()

    config = BatchConfig(
        sources_dir=args.sources,
        marker_dir=args.marker_dir,
        run_marker=(args.mode in ["all", "marker"]),
        run_pipeline=(args.mode in ["all", "pipeline"]),
        dry_run=args.dry_run
    )

    results = batch_process(config)

    if results:
        save_batch_report(results, args.report)
