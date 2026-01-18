def test_summary_endpoint(client, fake_storage, patch_gemini):
    doc_id = fake_storage
    r = client.post(f"/documents/{doc_id}/summary")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["doc_id"] == doc_id
    assert "summary" in data
    assert isinstance(data["summary"], str)


def test_study_plan_endpoint(client, fake_storage, patch_gemini):
    doc_id = fake_storage
    r = client.post(f"/documents/{doc_id}/study-plan")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["doc_id"] == doc_id
    assert "study_plan" in data
    assert isinstance(data["study_plan"], str)
