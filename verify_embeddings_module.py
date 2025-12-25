import os
import sys
from dotenv import load_dotenv

# Ensure src is in pythonpath
sys.path.append(os.getcwd())

load_dotenv()

from src.modules.embeddings.service import GeminiEmbeddingService

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        sys.exit(1)

    print("Initializing GeminiEmbeddingService...")
    # Initialize with default dims=1536 as requested, though model might behave differently
    service = GeminiEmbeddingService(api_key=api_key)

    text = "Hello, world! This is a test for embeddings."
    print(f"Embedding text: '{text}'")

    try:
        embeddings = service.embed_text(text)
        print(f"Successfully generated embeddings.")
        print(f"Number of dimensions: {len(embeddings)}")
        print(f"First 5 values: {embeddings[:5]}")

        if len(embeddings) != 1536:
            print(f"Keep in mind: Returned dimensions ({len(embeddings)}) differ from requested (1536).")
        else:
            print("Dimensions match request (1536).")

    except Exception as e:
        print(f"Error generating embeddings: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
