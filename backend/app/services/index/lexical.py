from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


@dataclass
class LexicalIndex:
    vectorizer: TfidfVectorizer
    matrix: any  # sparse


def build_tfidf(texts: List[str]) -> LexicalIndex:
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words=None,
        max_features=50000,
    )
    matrix = vectorizer.fit_transform(texts)
    return LexicalIndex(vectorizer=vectorizer, matrix=matrix)


def query_tfidf(index: LexicalIndex, query: str, top_k: int) -> List[Tuple[int, float]]:
    q = index.vectorizer.transform([query])
    scores = (index.matrix @ q.T).toarray().ravel()  # cosine en TF-IDF si ya normaliza
    if scores.size == 0:
        return []
    top_idx = np.argsort(-scores)[:top_k]
    return [(int(i), float(scores[i])) for i in top_idx if scores[i] > 0]
