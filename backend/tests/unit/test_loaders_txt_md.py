from pathlib import Path
from app.services.ingest.loaders import load_text

def test_load_text_txt(tmp_path: Path):
    p = tmp_path / "a.txt"
    p.write_text("hola mundo", encoding="utf-8")
    text, meta = load_text(p)
    assert "hola" in text
    assert meta["type"] == "text"

def test_load_text_md(tmp_path: Path):
    p = tmp_path / "a.md"
    p.write_text("# Título\ncontenido", encoding="utf-8")
    text, meta = load_text(p)
    assert "Título" in text
    assert meta["type"] == "text"