from __future__ import annotations
from dataclasses import asdict
from typing import Dict, List, Tuple
import numpy as np

from app.core.config import settings
from app.services.llm.gemini_client import GeminiClient
from app.services.index.lexical import LexicalIndex, query_tfidf
from app.services.index.vectorstore import VectorIndex, query_faiss
from app.services.ingest.chunker import Chunk


def hybrid_retrieve(
    question: str,
    chunks: List[Chunk],
    lexical: LexicalIndex,
    vector: VectorIndex,
    gemini: GeminiClient,
    top_k: int,
    alpha: float,
) -> List[Tuple[Chunk, float, dict]]:
    # 1) lexical
    lex_hits = query_tfidf(lexical, question, top_k=top_k * 3)

    # 2) vector
    q_emb = gemini.embed([question])[0]
    vec_hits = query_faiss(vector, q_emb, top_k=top_k * 3)

    # 3) combinar por índice (posición del chunk)
    scores: Dict[int, dict] = {}
    for idx, s in lex_hits:
        scores.setdefault(idx, {})["lex"] = s
    for idx, s in vec_hits:
        scores.setdefault(idx, {})["vec"] = s

    # normalización simple
    lex_vals = np.array([v.get("lex", 0.0) for v in scores.values()], dtype=float)
    vec_vals = np.array([v.get("vec", 0.0) for v in scores.values()], dtype=float)
    lex_max = float(lex_vals.max()) if lex_vals.size else 1.0
    vec_max = float(vec_vals.max()) if vec_vals.size else 1.0

    combined: List[Tuple[int, float, dict]] = []
    keys = list(scores.keys())
    for k in keys:
        lex = scores[k].get("lex", 0.0) / (lex_max or 1.0)
        vec = scores[k].get("vec", 0.0) / (vec_max or 1.0)
        score = (1 - alpha) * lex + alpha * vec
        combined.append((k, float(score), {"lex": lex, "vec": vec}))

    combined.sort(key=lambda x: x[1], reverse=True)
    best = combined[:top_k]

    return [(chunks[i], s, dbg) for i, s, dbg in best]


def build_prompt(question: str, retrieved: List[Tuple[Chunk, float, dict]]) -> str:
    sources = []
    for j, (ch, score, dbg) in enumerate(retrieved, start=1):
        sources.append(
            f"[Fuente {j} | {ch.chunk_id}] {ch.text}"
        )

    context_block = "\n\n".join(sources)

    return f"""Eres un asistente de estudio. Responde usando SOLO la información del CONTEXTO.
Si falta información, dilo y sugiere qué buscar en el documento.

CONTEXTO:
{context_block}

PREGUNTA:
{question}

RESPUESTA (incluye referencias tipo [Fuente 1], [Fuente 2] donde corresponda):
"""


def answer_question(
    doc_id: str,
    question: str,
    chunks: List[Chunk],
    lexical: LexicalIndex,
    vector: VectorIndex,
    gemini: GeminiClient,
) -> dict:
    retrieved = hybrid_retrieve(
        question=question,
        chunks=chunks,
        lexical=lexical,
        vector=vector,
        gemini=gemini,
        top_k=settings.TOP_K,
        alpha=settings.HYBRID_ALPHA,
    )

    prompt = build_prompt(question, retrieved)
    answer = gemini.generate(prompt)

    citations = []
    for i, (ch, score, dbg) in enumerate(retrieved, start=1):
        citations.append({
            "source": f"Fuente {i}",
            "chunk_id": ch.chunk_id,
            "snippet": ch.text[:240] + ("..." if len(ch.text) > 240 else ""),
            "score": score,
        })

    return {"doc_id": doc_id, "answer": answer, "citations": citations}
