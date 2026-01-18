from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
import json
import joblib
import faiss

from app.core.config import settings
from app.services.ingest.loaders import load_text
from app.services.ingest.chunker import simple_chunk
from app.services.index.lexical import build_tfidf
from app.services.index.vectorstore import build_faiss
from app.services.llm.gemini_client import GeminiClient

router = APIRouter(prefix="/documents", tags=["documents"])
gemini = GeminiClient()


def _paths(doc_id: str) -> dict:
    base = Path(settings.STORAGE_DIR)
    return {
        "base": base,
        "uploads": base / "uploads",
        "docs": base / "docs" / doc_id,
        "indexes": base / "indexes" / doc_id,
    }


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # tamaño (rápido): ojo que UploadFile no da tamaño directo sin leer
    ext = Path(file.filename).suffix.lower()

    doc_id = str(uuid.uuid4())
    p = _paths(doc_id)
    p["uploads"].mkdir(parents=True, exist_ok=True)
    p["docs"].mkdir(parents=True, exist_ok=True)
    p["indexes"].mkdir(parents=True, exist_ok=True)

    raw_path = p["uploads"] / f"{doc_id}{ext}"

    data = await file.read()
    if len(data) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Archivo demasiado grande")

    raw_path.write_bytes(data)

    # 1) extraer texto
    try:
        text, meta = load_text(raw_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo leer el archivo: {e}")

    if not text.strip():
        raise HTTPException(status_code=400, detail="El documento no contiene texto extraíble")

    # 2) chunking
    chunks = simple_chunk(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    chunk_texts = [c.text for c in chunks]

    # 3) índices
    lexical = build_tfidf(chunk_texts)
    embeddings = gemini.embed(chunk_texts)
    vector = build_faiss(embeddings)

    # 4) persistir
    (p["docs"] / "meta.json").write_text(json.dumps({
        "doc_id": doc_id,
        "filename": file.filename,
        "ext": ext,
        "meta": meta,
        "num_chunks": len(chunks),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    (p["docs"] / "chunks.json").write_text(json.dumps([
        {"chunk_id": c.chunk_id, "text": c.text, "start": c.start, "end": c.end}
        for c in chunks
    ], ensure_ascii=False), encoding="utf-8")

    joblib.dump(lexical, p["indexes"] / "tfidf.joblib")
    faiss.write_index(vector.faiss_index, str(p["indexes"] / "faiss.index"))

    return {"doc_id": doc_id, "filename": file.filename, "chunks": len(chunks)}
