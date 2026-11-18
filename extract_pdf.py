"""Extract text from a PDF as the first step toward reviewing a paper."""

import argparse
from pathlib import Path
from typing import BinaryIO

import pdfplumber


def extract_text(pdf_path: Path | BinaryIO) -> str:
    """Return the text from each page, preserving page boundaries."""
    with pdfplumber.open(pdf_path) as pdf:
        return "\n\n".join(
            f"--- Page {number} ---\n{page.extract_text() or '[No text found]'}"
            for number, page in enumerate(pdf.pages, start=1)
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text from a paper in PDF format.")
    parser.add_argument("pdf", type=Path, help="Path to the PDF file")
    args = parser.parse_args()
    if not args.pdf.is_file():
        parser.error(f"File not found: {args.pdf}")
    try:
        print(extract_text(args.pdf))
    except Exception as error:
        parser.exit(1, f"Could not read PDF: {error}\n")


if __name__ == "__main__":
    main()
