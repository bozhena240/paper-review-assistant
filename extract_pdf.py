"""Extract text from a PDF as the first step toward reviewing a paper."""

import argparse
import re
from pathlib import Path
from statistics import median
from typing import BinaryIO

import pdfplumber


def extract_page_text(page) -> str:
    """Suggest paragraph breaks using spacing, indentation, and list markers."""
    lines = page.extract_text_lines()
    if not lines:
        return "[No text found]"

    heights = [line["bottom"] - line["top"] for line in lines]
    typical_height = median(heights)
    left_edge = min(line["x0"] for line in lines)
    right_edge = max(line["x1"] for line in lines)
    typical_width = max(right_edge - left_edge, 1)
    paragraphs = [[lines[0]["text"]]]

    for previous, current in zip(lines, lines[1:]):
        gap = current["top"] - previous["bottom"]
        indented = current["x0"] - previous["x0"] > typical_height
        previous_short = previous["x1"] < right_edge - typical_width * 0.12
        list_item = re.match(r"^\s*(?:\d+[.)）]|[•●▪])\s*", current["text"])
        new_paragraph = (
            gap > typical_height * 0.8
            or (indented and previous_short)
            or bool(list_item)
        )
        if new_paragraph:
            paragraphs.append([])
        paragraphs[-1].append(current["text"])

    return "\n\n".join("\n".join(paragraph) for paragraph in paragraphs)


def extract_text(pdf_path: Path | BinaryIO) -> str:
    """Return extracted pages with suggested paragraph breaks."""
    with pdfplumber.open(pdf_path) as pdf:
        return "\n\n".join(
            f"--- Page {number} ---\n{extract_page_text(page)}"
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
