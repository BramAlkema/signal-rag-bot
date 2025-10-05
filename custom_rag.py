#!/usr/bin/env python3
"""
Custom RAG implementation using:
- FAISS for vector storage (local, fast)
- OpenAI embeddings for vectorization
- OpenAI chat completions for responses
"""
import os
import json
import pickle
from pathlib import Path
from typing import List, Dict
import numpy as np
from openai import OpenAI

# Will install: pip install faiss-cpu
try:
    import faiss
except ImportError:
    print("Installing FAISS...")
    import subprocess
    subprocess.run(["pip", "install", "faiss-cpu"], check=True)
    import faiss

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class CustomRAG:
    def __init__(self, bucket_dir: str = "output_v3"):
        self.bucket_dir = Path(bucket_dir)
        self.chunks = []
        self.embeddings = None
        self.index = None
        self.metadata_file = "rag_index.pkl"

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < text_len:
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                if break_point > chunk_size * 0.5:  # Only if we're past halfway
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks

    def load_and_chunk_buckets(self):
        """Load all bucket files and create chunks"""
        print("📚 Loading bucket files...")

        for bucket_file in sorted(self.bucket_dir.glob("bucket_*.md")):
            print(f"  Processing: {bucket_file.name}")

            with open(bucket_file, 'r') as f:
                content = f.read()

            # Extract category from filename
            category = bucket_file.stem.replace('bucket_', '').replace('_', ' ').title()

            # Create chunks with metadata
            text_chunks = self.chunk_text(content)

            for i, chunk in enumerate(text_chunks):
                self.chunks.append({
                    'text': chunk,
                    'source': bucket_file.name,
                    'category': category,
                    'chunk_id': i
                })

        print(f"✅ Created {len(self.chunks)} chunks from {len(list(self.bucket_dir.glob('bucket_*.md')))} buckets")

    def create_embeddings(self):
        """Create embeddings for all chunks"""
        print("\n🔢 Creating embeddings...")

        texts = [chunk['text'] for chunk in self.chunks]

        # Batch embeddings (max 2048 per request)
        batch_size = 100
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            print(f"  Embedding batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}...")

            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=batch
            )

            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)

        self.embeddings = np.array(all_embeddings).astype('float32')
        print(f"✅ Created {len(all_embeddings)} embeddings")

    def build_index(self):
        """Build FAISS index"""
        print("\n🔍 Building FAISS index...")

        dimension = self.embeddings.shape[1]

        # Use IndexFlatL2 for exact search (good for < 1M vectors)
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings)

        print(f"✅ Index built with {self.index.ntotal} vectors")

    def save_index(self):
        """Save index and metadata"""
        print("\n💾 Saving index...")

        # Save FAISS index
        faiss.write_index(self.index, "rag_faiss.index")

        # Save chunks metadata
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self.chunks, f)

        print("✅ Saved: rag_faiss.index, rag_index.pkl")

    def load_index(self):
        """Load pre-built index"""
        print("📂 Loading index...")

        if not Path("rag_faiss.index").exists():
            raise FileNotFoundError("Index not found. Run build_index() first.")

        self.index = faiss.read_index("rag_faiss.index")

        with open(self.metadata_file, 'rb') as f:
            self.chunks = pickle.load(f)

        print(f"✅ Loaded index with {self.index.ntotal} vectors")

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for relevant chunks"""
        # Embed query
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        query_embedding = np.array([response.data[0].embedding]).astype('float32')

        # Search
        distances, indices = self.index.search(query_embedding, k)

        # Return results with metadata
        results = []
        for i, idx in enumerate(indices[0]):
            results.append({
                **self.chunks[idx],
                'distance': float(distances[0][i])
            })

        return results

    def query(self, question: str, k: int = 3) -> str:
        """Query the RAG system and get an answer"""
        # Get relevant chunks
        results = self.search(question, k=k)

        # Build context
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Source {i}: {result['source']}, {result['category']}]\n{result['text']}\n")

        context = "\n---\n".join(context_parts)

        # Create prompt
        prompt = f"""You are a knowledgeable assistant specializing in Dutch defense industry, policy, and procurement.

Use the following context to answer the question. Always cite your sources using the [Source X] references.

Context:
{context}

Question: {question}

Answer:"""

        # Get response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context. Always cite your sources."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content


def build_rag_index():
    """Build RAG index from bucket files"""
    rag = CustomRAG()
    rag.load_and_chunk_buckets()
    rag.create_embeddings()
    rag.build_index()
    rag.save_index()
    print("\n🎉 RAG index built successfully!")
    return rag


def test_rag():
    """Test the RAG system"""
    rag = CustomRAG()
    rag.load_index()

    # Test queries
    test_queries = [
        "What are the main challenges in Dutch defense procurement?",
        "Tell me about drones in the Dutch military",
        "What is the NLDTIB?"
    ]

    print("\n" + "="*70)
    print("Testing RAG System")
    print("="*70)

    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 70)
        answer = rag.query(query, k=3)
        print(answer)
        print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "build":
        build_rag_index()
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        test_rag()
    else:
        print("Usage:")
        print("  python custom_rag.py build  - Build RAG index from buckets")
        print("  python custom_rag.py test   - Test RAG queries")
