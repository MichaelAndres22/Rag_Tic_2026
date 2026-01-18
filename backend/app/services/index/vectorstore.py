from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
import faiss


@dataclass
class VectorIndex:
    faiss_index: any  # faiss.Index
    dim: int


def _l2_normalize(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v, axis=1, keepdims=True) + 1e-12
    return v / norm


def build_faiss(embeddings: List[List[float]]) -> VectorIndex:
    vecs = np.array(embeddings, dtype="float32")
    if vecs.ndim != 2:
        raise ValueError("Embeddings inválidos")
    vecs = _l2_normalize(vecs)
    dim = vecs.shape[1]
    index = faiss.IndexFlatIP(dim)  # inner product sobre vectores normalizados = cosine
    index.add(vecs)
    return VectorIndex(faiss_index=index, dim=dim)


def query_faiss(index: VectorIndex, query_emb: List[float], top_k: int) -> List[Tuple[int, float]]:
    q = np.array([query_emb], dtype="float32")
    q = _l2_normalize(q)
    scores, ids = index.faiss_index.search(q, top_k)
    out: List[Tuple[int, float]] = []
    for i, s in zip(ids[0], scores[0]):
        if i == -1:
            continue
        out.append((int(i), float(s)))
    return out
