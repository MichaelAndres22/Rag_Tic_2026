from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.services.docstore import load_doc_assets
from app.services.llm.gemini_client import GeminiClient
from app.services.rag.pipeline import hybrid_retrieve, build_prompt
from app.core.config import settings
import json

router = APIRouter(prefix="/documents", tags=["outputs"])
gemini = GeminiClient()


def _context_from_top_chunks(doc_id: str, question: str, top_k: int = 10):
    chunks, lexical, vector, meta = load_doc_assets(doc_id)
    retrieved = hybrid_retrieve(
        question=question,
        chunks=chunks,
        lexical=lexical,
        vector=vector,
        gemini=gemini,
        top_k=top_k,
        alpha=settings.HYBRID_ALPHA,
    )
    context = "\n\n".join([f"[Fuente {i+1} | {ch.chunk_id}] {ch.text}" for i, (ch, _, _) in enumerate(retrieved)])
    citations = [
        {
            "source": f"Fuente {i+1}",
            "chunk_id": ch.chunk_id,
            "snippet": ch.text[:240] + ("..." if len(ch.text) > 240 else ""),
        }
        for i, (ch, _, _) in enumerate(retrieved)
    ]
    return context, citations, meta


@router.post("/{doc_id}/summary")
def summary(doc_id: str):
    try:
        context, citations, meta = _context_from_top_chunks(
            doc_id,
            question="Resume el documento completo destacando ideas principales, conceptos clave y estructura.",
            top_k=14,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="doc_id no encontrado")

    prompt = f"""Eres un asistente académico. Responde SOLO con base en el CONTEXTO.

CONTEXTO:
{context}

TAREA:
Escribe un resumen claro en español:
- 1 párrafo general (3-5 líneas)
- 6-10 viñetas de ideas clave
- Glosario corto (5-10 términos) si aplica

No inventes información.
"""
    text = gemini.generate(prompt)
    return {"doc_id": doc_id, "meta": meta, "summary": text, "citations": citations}


@router.post("/{doc_id}/study-plan")
def study_plan(doc_id: str):
    try:
        context, citations, meta = _context_from_top_chunks(
            doc_id,
            question="Crea un plan de estudio práctico para dominar el documento.",
            top_k=14,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="doc_id no encontrado")

    prompt = f"""Eres un tutor. Responde SOLO con base en el CONTEXTO.

CONTEXTO:
{context}

TAREA:
Crea un plan de estudio en español para alguien que quiere entender el documento:
- Duración sugerida: 1 a 2 semanas (puedes dividir por días)
- Para cada sesión: objetivo, lectura (qué sección/tema), actividad (resumen, mapa mental, preguntas)
- Al final: checklist de dominio y 5 preguntas de autoevaluación

No inventes secciones que no estén soportadas por el contexto: describe por temas.
"""
    text = gemini.generate(prompt)
    return {"doc_id": doc_id, "meta": meta, "study_plan": text, "citations": citations}


@router.post("/{doc_id}/practice/generate")
def practice_generate(doc_id: str, n: int = 8):
    # Genera preguntas a partir del documento (top chunks)
    try:
        context, citations, meta = _context_from_top_chunks(
            doc_id,
            question="Genera preguntas de práctica sobre el contenido del documento.",
            top_k=16,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="doc_id no encontrado")

    prompt = f"""Genera EXACTAMENTE {n} preguntas de práctica en español usando SOLO el CONTEXTO.
Devuelve SOLO JSON válido con este formato:

{{
  "questions": [
    {{
      "id": "q1",
      "type": "short",
      "question": "..."
    }}
  ]
}}

Reglas:
- type: "short" (respuesta corta) o "mcq" (opción múltiple)
- Si type="mcq", incluye "options": ["A", "B", "C", "D"] y "answer": "A|B|C|D"
- No incluyas explicaciones fuera del JSON.

CONTEXTO:
{context}
"""
    raw = gemini.generate(prompt).strip()

    # Intento de parseo robusto (si el modelo mete texto extra)
    try:
        start = raw.find("{")
        end = raw.rfind("}")
        data = json.loads(raw[start:end+1])
        return {"doc_id": doc_id, "meta": meta, "questions": data.get("questions", []), "citations": citations}
    except Exception:
        raise HTTPException(status_code=500, detail=f"No se pudo parsear JSON de preguntas. Respuesta cruda:\n{raw[:2000]}")


@router.post("/{doc_id}/practice/grade")
def practice_grade(doc_id: str, question_id: str, question: str, user_answer: str):
    # Corrige la respuesta del usuario usando RAG (recupera evidencia) para evaluar
    try:
        context, citations, meta = _context_from_top_chunks(
            doc_id,
            question=question,
            top_k=10,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="doc_id no encontrado")

    prompt = f"""Eres un corrector. Evalúa la respuesta del estudiante usando SOLO el CONTEXTO.
Devuelve SOLO JSON válido:

{{
  "question_id": "{question_id}",
  "is_correct": true/false,
  "score": 0 a 1,
  "expected_answer": "...",
  "feedback": "..."
}}

CONTEXTO:
{context}

PREGUNTA:
{question}

RESPUESTA DEL ESTUDIANTE:
{user_answer}
"""
    raw = gemini.generate(prompt).strip()

    try:
        start = raw.find("{")
        end = raw.rfind("}")
        data = json.loads(raw[start:end+1])
        data["doc_id"] = doc_id
        data["citations"] = citations
        return data
    except Exception:
        raise HTTPException(status_code=500, detail=f"No se pudo parsear JSON de corrección. Respuesta cruda:\n{raw[:2000]}")
