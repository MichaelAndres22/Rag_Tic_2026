def test_practice_generate_endpoint(client, fake_storage, patch_gemini, monkeypatch):
    # En este test, el FakeGemini.generate devuelve texto simple.
    # Entonces aquí conviene parchear generate para que devuelva JSON válido.
    from app.api.routes import outputs as outputs_router

    class FakeGeminiForPractice:
        def embed(self, texts):
            return [[float(len(t)), 1.0, 0.5] for t in texts]
        def generate(self, prompt: str) -> str:
            return '{"questions":[{"id":"q1","type":"short","question":"¿Qué es FastAPI?"}]}'

    monkeypatch.setattr(outputs_router, "gemini", FakeGeminiForPractice())

    doc_id = fake_storage
    r = client.post(f"/documents/{doc_id}/practice/generate?n=1")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "questions" in data
    assert len(data["questions"]) == 1


def test_practice_grade_endpoint(client, fake_storage, monkeypatch):
    from app.api.routes import outputs as outputs_router

    class FakeGeminiForGrade:
        def embed(self, texts):
            return [[float(len(t)), 1.0, 0.5] for t in texts]
        def generate(self, prompt: str) -> str:
            return """{
              "question_id": "q1",
              "is_correct": true,
              "score": 1,
              "expected_answer": "FastAPI sirve para crear APIs.",
              "feedback": "Bien."
            }"""

    monkeypatch.setattr(outputs_router, "gemini", FakeGeminiForGrade())

    doc_id = fake_storage
    r = client.post(
        f"/documents/{doc_id}/practice/grade"
        f"?question_id=q1"
        f"&question=%C2%BFQu%C3%A9%20es%20FastAPI%3F"
        f"&user_answer=Sirve%20para%20crear%20APIs"
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["question_id"] == "q1"
    assert data["is_correct"] is True
