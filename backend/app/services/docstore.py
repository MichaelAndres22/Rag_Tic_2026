from __future__ import annotations
from pathlib import Path
import json
import joblib
import faiss

from app.core.config import settings
from app.services.ingest.chunker import Chunk
from app.services.index.vectorstore import VectorIndex


def load_doc_assets(doc_id: str):
    base = Path(settings.STORAGE_DIR)
    docs_dir = base / "docs" / doc_id
    idx_dir = base / "indexes" / doc_id

    if not docs_dir.exists() or not idx_dir.exists():
        raise FileNotFoundError("doc_id no encontrado")

    chunks_raw = json.loads((docs_dir / "chunks.json").read_text(encoding="utf-8"))
    chunks = [Chunk(**c) for c in chunks_raw]

    lexical = joblib.load(idx_dir / "tfidf.joblib")

    faiss_index = faiss.read_index(str(idx_dir / "faiss.index"))
    vector = VectorIndex(faiss_index=faiss_index, dim=faiss_index.d)

    meta_path = docs_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

    return chunks, lexical, vector, meta
