import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

@pytest.fixture
def client():
    return TestClient(app)

class FakeGemini:
    def embed(self, texts):
        # devuelve embeddings deterministas por texto
        out = []
        for t in texts:
            # embedding 3D simple basado en longitud (solo para test)
            n = float(len(t))
            out.append([n, 1.0, 0.5])
        return out

    def generate(self, prompt: str) -> str:
        # respuesta determinista
        return "RESPUESTA_FAKE"

@pytest.fixture
def fake_storage(tmp_path, monkeypatch):
    """
    Crea un doc_id de prueba con chunks + índices mínimos en un storage temporal.
    """
    monkeypatch.setattr(settings, "STORAGE_DIR", str(tmp_path))

    doc_id = "doc_test_1"
    docs_dir = tmp_path / "docs" / doc_id
    idx_dir = tmp_path / "indexes" / doc_id
    docs_dir.mkdir(parents=True, exist_ok=True)
    idx_dir.mkdir(parents=True, exist_ok=True)

    # chunks
    chunks = [
        {"chunk_id": "c0", "text": "FastAPI sirve para crear APIs rápidas.", "start": 0, "end": 35},
        {"chunk_id": "c1", "text": "Python es muy usado en backend.", "start": 36, "end": 65},
    ]
    (docs_dir / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")
    (docs_dir / "meta.json").write_text(json.dumps({"doc_id": doc_id}, ensure_ascii=False), encoding="utf-8")

    # crea índices reales (TF-IDF + FAISS) usando tus funciones
    from app.services.index.lexical import build_tfidf
    from app.services.index.vectorstore import build_faiss
    import joblib
    import faiss

    texts = [c["text"] for c in chunks]
    lexical = build_tfidf(texts)
    joblib.dump(lexical, idx_dir / "tfidf.joblib")

    # embeddings fake
    fake = FakeGemini()
    vec = build_faiss(fake.embed(texts))
    faiss.write_index(vec.faiss_index, str(idx_dir / "faiss.index"))

    return doc_id

@pytest.fixture
def patch_gemini(monkeypatch):
    """
    Parchea el objeto global gemini en los routers para que no llame a la API real.
    """
    from app.api.routes import chat as chat_router
    from app.api.routes import outputs as outputs_router  # si lo creaste

    monkeypatch.setattr(chat_router, "gemini", FakeGemini())
    # outputs_router solo existe si agregaste outputs.py
    if hasattr(outputs_router, "gemini"):
        monkeypatch.setattr(outputs_router, "gemini", FakeGemini())
