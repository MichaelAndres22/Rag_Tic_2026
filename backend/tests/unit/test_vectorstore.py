from app.services.index.vectorstore import build_faiss, query_faiss

def test_faiss_queries_return_neighbors():
    # embeddings falsos pero consistentes
    emb = [
        [1.0, 0.0, 0.0],
        [0.9, 0.1, 0.0],
        [0.0, 1.0, 0.0],
    ]
    index = build_faiss(emb)
    hits = query_faiss(index, [1.0, 0.0, 0.0], top_k=2)
    assert hits
    assert hits[0][0] == 0
