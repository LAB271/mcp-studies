#!/usr/bin/env python3
"""
Generate vector embeddings from text files
Requires: pip install sentence-transformers
"""

import json
import sys
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Error: sentence-transformers not installed")
    print("Install with: pip install sentence-transformers")
    sys.exit(1)


class TextChunker:
    """Split text into chunks for embedding."""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, source: str) -> list[dict]:
        """Split text into overlapping chunks."""
        chunks = []
        words = text.split()

        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i : i + self.chunk_size]
            if chunk_words:
                chunk_text = " ".join(chunk_words)
                chunks.append({"text": chunk_text, "source": source, "position": i // (self.chunk_size - self.overlap)})

        return chunks


def generate_embeddings(text_path: Path, output_path: Path, model_name: str = "all-MiniLM-L6-v2"):
    """Generate embeddings for text file."""
    print(f"Loading model: {model_name}...")
    model = SentenceTransformer(model_name)

    print(f"Reading text from {text_path.name}...")
    with open(text_path, encoding="utf-8") as f:
        text = f.read()

    print(f"Text size: {len(text) / 1024 / 1024:.2f} MB")

    # Chunk text
    print("Chunking text...")
    chunker = TextChunker(chunk_size=512, overlap=50)
    chunks = chunker.chunk_text(text, text_path.stem)
    print(f"Created {len(chunks)} chunks")

    # Generate embeddings
    print("Generating embeddings (this may take a while)...")
    embeddings_data = []

    for i, chunk in enumerate(chunks):
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(chunks)}")

        embedding = model.encode(chunk["text"])

        embeddings_data.append(
            {
                "id": f"{chunk['source']}_{chunk['position']}",
                "chunk_id": i,
                "text": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                "full_text": chunk["text"],
                "embedding": embedding.tolist(),
                "source": chunk["source"],
                "position": chunk["position"],
            }
        )

    # Save embeddings
    print(f"Saving embeddings to {output_path.name}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(embeddings_data, f, indent=2)

    print(f"✓ Generated {len(embeddings_data)} embeddings")
    print(f"  File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")

    return embeddings_data


def main():
    """Generate embeddings for all text files."""
    documents_path = Path(__file__).parent.parent / "graph_data" / "documents"
    embeddings_path = Path(__file__).parent.parent / "graph_data" / "embeddings"

    # Create embeddings directory if needed
    embeddings_path.mkdir(parents=True, exist_ok=True)

    # Find all text files
    text_files = list(documents_path.glob("*.txt")) + list(documents_path.glob("*.md"))

    # Filter out README
    text_files = [f for f in text_files if f.name != "README.md"]

    if not text_files:
        print("No text files found in documents folder")
        print("Run extract_pdfs.py first to extract PDFs to text")
        return

    print(f"Found {len(text_files)} text file(s) to process\n")

    success_count = 0
    for text_file in text_files:
        output_file = embeddings_path / f"{text_file.stem}_embeddings.json"

        # Skip if already generated
        if output_file.exists():
            print(f"⊘ {output_file.name} already exists, skipping...\n")
            continue

        try:
            generate_embeddings(text_file, output_file)
            success_count += 1
            print()
        except Exception as e:
            print(f"✗ Error processing {text_file.name}: {e}\n")

    print(f"✓ Successfully generated embeddings for {success_count}/{len(text_files)} files")


if __name__ == "__main__":
    main()
