from __future__ import annotations
from typing import List
from google import genai
from app.core.config import settings


class GeminiClient:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def embed(self, texts: List[str]) -> List[List[float]]:
        # Embed batch. Mantén batches pequeños si tienes límites del free tier.
        out = self.client.models.embed_content(
            model=settings.GEMINI_EMBED_MODEL,
            contents=texts,
        )
        # out.embeddings es una lista; cada embedding tiene .values
        return [e.values for e in out.embeddings]

    def generate(self, prompt: str) -> str:
        resp = self.client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )
        return resp.text or ""
