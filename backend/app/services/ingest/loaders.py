from __future__ import annotations
from pathlib import Path
from typing import Tuple
from pypdf import PdfReader
import docx


SUPPORTED_EXT = {".pdf", ".docx", ".txt", ".md"}


def load_text(file_path: Path) -> Tuple[str, dict]:
    ext = file_path.suffix.lower()
    if ext not in SUPPORTED_EXT:
        raise ValueError(f"Formato no soportado: {ext}")

    if ext == ".pdf":
        return _load_pdf(file_path)
    if ext == ".docx":
        return _load_docx(file_path)
    if ext in {".txt", ".md"}:
        return _load_txt(file_path)

    raise ValueError(f"Formato no soportado: {ext}")


def _load_pdf(path: Path) -> Tuple[str, dict]:
    reader = PdfReader(str(path))
    pages_text = []
    for i, page in enumerate(reader.pages):
        pages_text.append(page.extract_text() or "")
    text = "\n".join(pages_text)
    meta = {"type": "pdf", "pages": len(reader.pages)}
    return text, meta


def _load_docx(path: Path) -> Tuple[str, dict]:
    d = docx.Document(str(path))
    text = "\n".join(p.text for p in d.paragraphs)
    meta = {"type": "docx"}
    return text, meta


def _load_txt(path: Path) -> Tuple[str, dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    meta = {"type": "text"}
    return text, meta
