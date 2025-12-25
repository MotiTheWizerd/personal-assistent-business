from google import genai
from google.genai import types

class GeminiEmbeddingService:
    def __init__(self, api_key: str, model_name: str = "gemini-embedding-001", dims: int = 1536):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.dims = dims

    def embed_text(self, text: str) -> list[float]:
        # Using output_dimensionality to attempt to valid the requested dims if model supports it
        # For gemini-embedding-001, it might ignore it if not supported, but latest SDK allows config.
        result = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=self.dims
            )
        )
        return result.embeddings[0].values
