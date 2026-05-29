"""PDF download and text extraction utilities."""

from pathlib import Path

from pypdf import PdfReader


def save_pdf(content: bytes, output_dir: str, filename: str) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    filepath = out / filename
    filepath.write_bytes(content)
    return filepath


def extract_text(pdf_path: str | Path, max_pages: int = 50) -> str:
    reader = PdfReader(str(pdf_path))
    pages = reader.pages[:max_pages]
    text_parts = []
    for page in pages:
        t = page.extract_text()
        if t:
            text_parts.append(t)
    return "\n\n".join(text_parts)
