# RAG NotebookLM-like (Gemini) — Backend + UI mínima

Proyecto tipo RAG inspirado en NotebookLM: el usuario sube un documento y el sistema:
- Indexa el contenido en fragmentos (chunks)
- Permite chatear con el documento (RAG)
- Genera un resumen
- Genera un plan de estudio
- Genera preguntas de práctica y corrige respuestas usando evidencia del documento

El enfoque es híbrido:
- Recuperación **lexical** con TF-IDF
- Recuperación **semántica** con embeddings y FAISS
- Respuesta generada con **Gemini** usando el contexto recuperado (con citas por chunk)

---

## Estructura del repositorio

```text
rag-notebooklm-like/
  backend/
    app/
      main.py
      core/
        config.py
      api/
        routes/
          documents.py
          chat.py
          outputs.py
      schemas/
        common.py
      services/
        ingest/
          loaders.py
          chunker.py
        index/
          lexical.py
          vectorstore.py
        llm/
          gemini_client.py
        rag/
          pipeline.py
      storage/
        uploads/
        docs/
        indexes/
    requirements.txt
    requirements-dev.txt
    .env.example
  tests/
    conftest.py
    unit/
      test_chunker.py
      test_lexical.py
      test_vectorstore.py
      test_rag_prompt.py
      test_loaders_docx.py
      test_loaders_txt_md.py
    integration/
      test_chat_endpoint.py
      test_documents_upload.py
      test_outputs_endpoints.py
      test_practice_endpoints.py
  web_min/
    index.html
    app.js
  README.md

  

