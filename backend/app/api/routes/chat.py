from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import joblib
import faiss

from app.core.config import settings
from app.schemas.common import ChatRequest
from app.services.ingest.chunker import Chunk
from app.services.llm.gemini_client import GeminiClient
from app.services.rag.pipeline import answer_question
from app.services.index.vectorstore import VectorIndex

router = APIRouter(prefix="", tags=["chat"])
gemini = GeminiClient()


def _doc_base() -> Path:
    return Path(settings.STORAGE_DIR)


@router.post("/chat")
def chat(req: ChatRequest):
    try:
        base = _doc_base()
        docs_dir = base / "docs" / req.doc_id
        idx_dir = base / "indexes" / req.doc_id

        if not docs_dir.exists() or not idx_dir.exists():
            raise HTTPException(status_code=404, detail="doc_id no encontrado")

        chunks_path = docs_dir / "chunks.json"
        if not chunks_path.exists():
            raise HTTPException(status_code=500, detail="No existe chunks.json para este doc_id")

        chunks_raw = json.loads(chunks_path.read_text(encoding="utf-8"))
        chunks = [Chunk(**c) for c in chunks_raw]

        tfidf_path = idx_dir / "tfidf.joblib"
        if not tfidf_path.exists():
            raise HTTPException(status_code=500, detail="No existe tfidf.joblib para este doc_id")

        lexical = joblib.load(tfidf_path)

        faiss_path = idx_dir / "faiss.index"
        if not faiss_path.exists():
            raise HTTPException(status_code=500, detail="No existe faiss.index para este doc_id")

        faiss_index = faiss.read_index(str(faiss_path))
        vector = VectorIndex(faiss_index=faiss_index, dim=faiss_index.d)

        out = answer_question(
            doc_id=req.doc_id,
            question=req.question,
            chunks=chunks,
            lexical=lexical,
            vector=vector,
            gemini=gemini,
        )
        return out

    except HTTPException:
        # Deja pasar errores controlados tal cual (404, 400, etc.)
        raise

    except FileNotFoundError:
        # Por si algo falla por rutas, aunque ya controlamos arriba
        raise HTTPException(status_code=404, detail="doc_id no encontrado")

    except Exception as e:
        # Esto hará que Swagger muestre el error real
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
