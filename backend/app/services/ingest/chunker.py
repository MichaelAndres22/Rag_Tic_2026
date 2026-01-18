from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass
class Chunk:
    chunk_id: str
    text: str
    start: int
    end: int


def simple_chunk(text: str, chunk_size: int, overlap: int) -> List[Chunk]:
    text = normalize_text(text)
    chunks: List[Chunk] = []

    if not text.strip():
        return chunks

    step = max(1, chunk_size - overlap)
    n = len(text)

    idx = 0
    k = 0
    while idx < n:
        start = idx
        end = min(n, idx + chunk_size)
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(Chunk(chunk_id=f"c{k}", text=chunk_text, start=start, end=end))
            k += 1
        idx += step

    return chunks


def normalize_text(t: str) -> str:
    # Normalización simple, suficiente para MVP
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = "\n".join(line.strip() for line in t.split("\n"))
    return t.strip()
