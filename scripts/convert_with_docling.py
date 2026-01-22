#!/usr/bin/env python3
"""
Docling PDF Converter for Canadian Building Codes
PDF → MD + JSON (with metadata for BYOD)
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime

from docling.document_converter import DocumentConverter


def calculate_md5(file_path: str) -> str:
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_pdf_metadata(pdf_path: str) -> dict:
    """Extract PDF metadata for version verification."""
    import fitz  # PyMuPDF

    doc = fitz.open(pdf_path)
    metadata = {
        "filename": Path(pdf_path).name,
        "md5": calculate_md5(pdf_path),
        "page_count": len(doc),
        "file_size_bytes": os.path.getsize(pdf_path),
        "modified_date": datetime.fromtimestamp(
            os.path.getmtime(pdf_path)
        ).isoformat(),
    }

    # Get PDF internal metadata if available
    pdf_meta = doc.metadata
    if pdf_meta:
        if pdf_meta.get("title"):
            metadata["pdf_title"] = pdf_meta["title"]
        if pdf_meta.get("author"):
            metadata["pdf_author"] = pdf_meta["author"]
        if pdf_meta.get("creationDate"):
            metadata["pdf_creation_date"] = pdf_meta["creationDate"]

    doc.close()
    return metadata


def convert_pdf(pdf_path: str, output_dir: str = None) -> dict:
    """
    Convert PDF to Markdown + JSON using Docling.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Output directory (default: docling_output/<pdf_name>/)

    Returns:
        dict with paths to output files and metadata
    """
    pdf_path = Path(pdf_path).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Determine output directory
    if output_dir is None:
        base_name = pdf_path.stem.replace(" ", "_").lower()
        output_dir = Path("docling_output") / base_name
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Converting: {pdf_path.name}")
    print(f"Output dir: {output_dir}")

    # Get PDF metadata first (for BYOD verification)
    print("Extracting PDF metadata...")
    pdf_metadata = get_pdf_metadata(str(pdf_path))
    print(f"  Pages: {pdf_metadata['page_count']}")
    print(f"  MD5: {pdf_metadata['md5'][:16]}...")

    # Convert with Docling
    print("Running Docling conversion...")
    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))

    # Export Markdown
    md_content = result.document.export_to_markdown()
    md_path = output_dir / f"{pdf_path.stem}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"  Saved: {md_path.name} ({len(md_content):,} chars)")

    # Export JSON (document structure with coordinates)
    doc_dict = result.document.export_to_dict()

    # Add our metadata
    doc_dict["_source_pdf"] = pdf_metadata
    doc_dict["_conversion"] = {
        "tool": "docling",
        "timestamp": datetime.now().isoformat(),
    }

    json_path = output_dir / f"{pdf_path.stem}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(doc_dict, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {json_path.name}")

    # Save metadata separately for quick access
    meta_path = output_dir / f"{pdf_path.stem}_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "source_pdf": pdf_metadata,
            "conversion": doc_dict["_conversion"],
            "md_file": md_path.name,
            "json_file": json_path.name,
        }, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {meta_path.name}")

    print("Done!")

    return {
        "pdf_path": str(pdf_path),
        "output_dir": str(output_dir),
        "md_path": str(md_path),
        "json_path": str(json_path),
        "meta_path": str(meta_path),
        "pdf_metadata": pdf_metadata,
    }


def convert_all(source_dir: str = "sources", output_base: str = "docling_output"):
    """Convert all PDFs in a directory."""
    source_dir = Path(source_dir)
    pdfs = list(source_dir.glob("*.pdf")) + list(source_dir.glob("*.PDF"))

    print(f"Found {len(pdfs)} PDFs in {source_dir}")
    print("=" * 50)

    results = []
    for i, pdf in enumerate(pdfs, 1):
        print(f"\n[{i}/{len(pdfs)}] {pdf.name}")
        print("-" * 40)

        try:
            result = convert_pdf(str(pdf), None)
            results.append({"status": "success", **result})
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({"status": "error", "pdf": str(pdf), "error": str(e)})

    # Save summary
    summary_path = Path(output_base) / "conversion_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": len(pdfs),
            "success": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "error"),
            "results": results,
        }, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 50)
    print(f"Conversion complete!")
    print(f"  Success: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"  Failed: {sum(1 for r in results if r['status'] == 'error')}")
    print(f"  Summary: {summary_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Building Code PDFs with Docling"
    )
    parser.add_argument(
        "pdf_path",
        nargs="?",
        help="Path to a single PDF file (or 'all' to convert all in sources/)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output directory (default: docling_output/<pdf_name>/)"
    )
    parser.add_argument(
        "--source-dir", "-s",
        default="sources",
        help="Source directory for batch conversion (default: sources/)"
    )

    args = parser.parse_args()

    if args.pdf_path is None or args.pdf_path.lower() == "all":
        convert_all(args.source_dir)
    else:
        convert_pdf(args.pdf_path, args.output)


if __name__ == "__main__":
    main()
