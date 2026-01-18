from app.services.ingest.chunker import simple_chunk

def test_simple_chunk_creates_chunks():
    text = "A" * 2500
    chunks = simple_chunk(text, chunk_size=900, overlap=150)
    assert len(chunks) >= 3
    assert chunks[0].chunk_id == "c0"
    assert chunks[0].text
    # solapamiento: el segundo chunk debería empezar antes de acabar el primero (por overlap)
    assert chunks[1].start < chunks[0].end
