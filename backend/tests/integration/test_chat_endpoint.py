def test_chat_endpoint_returns_answer(client, fake_storage, patch_gemini):
    doc_id = fake_storage
    payload = {"doc_id": doc_id, "question": "¿Para qué sirve FastAPI?"}
    r = client.post("/chat", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["doc_id"] == doc_id
    assert data["answer"] == "RESPUESTA_FAKE"
    assert "citations" in data
    assert len(data["citations"]) > 0

