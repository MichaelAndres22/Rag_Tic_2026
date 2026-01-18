from io import BytesIO

def test_documents_upload_txt(client, monkeypatch):
    # Parchea gemini del router documents
    from app.api.routes import documents as documents_router

    class FakeGemini:
        def embed(self, texts):
            return [[float(len(t)), 1.0, 0.5] for t in texts]
        def generate(self, prompt: str) -> str:
            return "OK"

    monkeypatch.setattr(documents_router, "gemini", FakeGemini())

    file_content = b"FastAPI sirve para crear APIs.\nPython es el lenguaje."
    files = {"file": ("demo.txt", BytesIO(file_content), "text/plain")}

    r = client.post("/documents/upload", files=files)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "doc_id" in data
    assert data["chunks"] > 0