from app.services.index.lexical import build_tfidf, query_tfidf

def test_tfidf_retrieves_relevant_chunk():
    texts = [
        "Python es un lenguaje de programación.",
        "La fotosíntesis ocurre en las plantas.",
        "FastAPI sirve para crear APIs."
    ]
    idx = build_tfidf(texts)
    hits = query_tfidf(idx, "APIs con FastAPI", top_k=2)
    assert hits, "Debe recuperar algo"
    # el chunk más relevante debería ser el de FastAPI
    assert hits[0][0] == 2
