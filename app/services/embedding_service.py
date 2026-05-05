from sentence_transformers import SentenceTransformer

print("📦 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Embedding model loaded")

EMBEDDING_DIMENSIONS = 384


def create_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    cleaned = [text.replace("\n", " ").strip() for text in texts]
    print(f"🔢 Creating embeddings for {len(cleaned)} chunks...")

    vectors = model.encode(cleaned, show_progress_bar=False)
    result = [vector.tolist() for vector in vectors]

    print(f"✅ Created {len(result)} embeddings (each has {len(result[0])} dimensions)")
    return result


def create_single_embedding(text: str) -> list[float]:
    vector = model.encode([text.replace("\n", " ").strip()])
    return vector[0].tolist()