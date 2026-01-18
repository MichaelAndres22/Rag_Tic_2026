from app.services.rag.pipeline import build_prompt
from app.services.ingest.chunker import Chunk

def test_build_prompt_includes_sources_and_question():
    chunks = [
        (Chunk(chunk_id="c0", text="Contenido A", start=0, end=10), 0.9, {}),
        (Chunk(chunk_id="c1", text="Contenido B", start=11, end=20), 0.8, {}),
    ]
    prompt = build_prompt("¿Qué dice?", chunks)
    assert "CONTEXTO" in prompt
    assert "PREGUNTA" in prompt
    assert "¿Qué dice?" in prompt
    assert "[Fuente 1 | c0]" in prompt
