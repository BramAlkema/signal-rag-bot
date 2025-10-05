# Custom RAG API Reference

Auto-generated API documentation for the CustomRAG class.

---

## Overview

The `CustomRAG` class implements the core Retrieval-Augmented Generation functionality using FAISS vector store and OpenAI embeddings.

**Key Features:**
- PDF text extraction with metadata
- Intelligent text chunking with overlap
- OpenAI embeddings (text-embedding-3-small, 1536 dimensions)
- FAISS vector similarity search
- Context-aware response generation

---

## Quick Example

```python
from custom_rag import CustomRAG

# Initialize RAG
rag = CustomRAG(bucket_dir="output_v3")

# Build index from PDFs
rag.build_index()

# Query the knowledge base
response = rag.query("What is the main topic?", k=3)
print(response)
```

---

## Class Reference

::: custom_rag.CustomRAG
    options:
      show_root_heading: true
      show_source: true
      members:
        - __init__
        - load_pdfs
        - extract_text_from_pdf
        - chunk_text
        - create_embeddings
        - build_index
        - save_index
        - load_index
        - search
        - query
      show_signature_annotations: true
      separate_signature: true

---

## Usage Examples

### Building an Index

```python
from custom_rag import CustomRAG

# Initialize with custom bucket directory
rag = CustomRAG(bucket_dir="my_documents")

# Build index from PDFs in bucket_dir
rag.build_index()

# Save index to disk
rag.save_index("my_index.faiss", "my_index.pkl")
```

**Output:**
```
Processing PDFs...
✓ Loaded 5 PDFs
✓ Extracted 250 text chunks
✓ Created embeddings (1536 dimensions)
✓ Built FAISS index
✓ Saved index successfully
```

### Loading an Existing Index

```python
from custom_rag import CustomRAG

rag = CustomRAG()
rag.load_index("my_index.faiss", "my_index.pkl")

print(f"Loaded index with {len(rag.chunks)} chunks")
```

### Searching the Knowledge Base

```python
# Search for relevant chunks
results = rag.search("authentication methods", k=5)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Source: {result['metadata']['filename']}")
    print(f"Text: {result['text'][:200]}...")
    print()
```

**Example Output:**
```
Score: 0.892
Source: security_guide.pdf, page 12
Text: Authentication methods include OAuth2, JWT tokens...

Score: 0.856
Source: api_docs.pdf, page 45
Text: The authentication flow begins with...
```

### Querying with Context

```python
# Query with automatic context retrieval
response = rag.query(
    question="How do I implement OAuth2?",
    k=3  # Retrieve top 3 relevant chunks
)

print(response)
```

**Example Output:**
```
To implement OAuth2, you need to:

1. Register your application to get client credentials
2. Implement the authorization code flow
3. Exchange authorization code for access token

[Source: security_guide.pdf, page 12]
[Source: api_docs.pdf, page 45]
```

---

## Configuration

### Initialization Parameters

```python
CustomRAG(
    bucket_dir: str = "output_v3",  # Directory containing PDFs
    model: str = "text-embedding-3-small",  # OpenAI embedding model
    chunk_size: int = 1000,  # Characters per chunk
    chunk_overlap: int = 200,  # Overlap between chunks
)
```

### Environment Variables

The CustomRAG class uses these environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `CHUNK_SIZE` | No | 1000 | Text chunk size |
| `CHUNK_OVERLAP` | No | 200 | Chunk overlap size |
| `SEARCH_K` | No | 3 | Number of chunks to retrieve |

---

## Advanced Usage

### Custom Chunking Strategy

```python
# Custom chunk size and overlap
rag = CustomRAG()
rag.chunk_size = 500  # Smaller chunks
rag.chunk_overlap = 100  # Less overlap

text = "Long document text..."
chunks = rag.chunk_text(text, chunk_size=500, overlap=100)
```

### Batch Embedding Generation

```python
# Generate embeddings for large datasets
rag = CustomRAG()

# Embeddings are generated in batches of 100
rag.chunks = [{'text': f'Chunk {i}', ...} for i in range(1000)]
rag.create_embeddings()  # Automatically batches requests

print(f"Generated {rag.embeddings.shape[0]} embeddings")
```

### FAISS Index Configuration

```python
import faiss
import numpy as np

# Create custom FAISS index
dimension = 1536
index = faiss.IndexFlatL2(dimension)  # L2 distance

# Add vectors
vectors = np.random.rand(100, dimension).astype('float32')
index.add(vectors)

# Use with CustomRAG
rag = CustomRAG()
rag.index = index
rag.embeddings = vectors
```

---

## Performance Considerations

### Index Size

- **Small** (< 100 chunks): < 1MB, < 10ms search
- **Medium** (100-1000 chunks): ~10MB, ~50ms search
- **Large** (1000-10000 chunks): ~100MB, ~100ms search
- **Very Large** (> 10000 chunks): > 1GB, > 500ms search

### Memory Usage

Approximate memory requirements:

```python
chunks = 1000
dimension = 1536
embedding_size = chunks * dimension * 4  # float32 = 4 bytes
# = 1000 * 1536 * 4 = 6.1 MB

# Plus FAISS index overhead (~2x)
total_memory = embedding_size * 2  # ~12 MB
```

### Optimization Tips

1. **Reduce Chunk Size**: Smaller chunks = faster search, less context
2. **Limit Search K**: Return fewer results for faster queries
3. **Use FAISS GPU**: For very large indexes (> 100K chunks)
4. **Batch Embeddings**: Process in batches of 100 for better throughput

---

## Error Handling

### Common Errors

**Missing API Key:**
```python
try:
    rag = CustomRAG()
    rag.create_embeddings()
except ValueError as e:
    print(f"Error: {e}")
    # Error: OPENAI_API_KEY not set
```

**Empty Index:**
```python
try:
    rag = CustomRAG()
    rag.search("query")
except RuntimeError as e:
    print(f"Error: {e}")
    # Error: Index not built. Call build_index() first.
```

**Invalid PDF:**
```python
try:
    rag = CustomRAG()
    rag.extract_text_from_pdf("corrupted.pdf")
except Exception as e:
    print(f"Failed to extract: {e}")
```

---

## Testing

### Unit Tests

Run the CustomRAG test suite:

```bash
pytest tests/test_custom_rag.py -v
```

**Coverage:**
- Text extraction: 8 tests
- Chunking: 6 tests
- Embeddings: 5 tests
- Search: 6 tests
- Overall coverage: **90%**

### Integration Tests

```python
# Test end-to-end RAG pipeline
def test_rag_pipeline():
    rag = CustomRAG(bucket_dir="test_data")
    rag.build_index()

    response = rag.query("test question")
    assert len(response) > 0
    assert "Source:" in response
```

---

## Migration Guide

### From OpenAI Assistant API

If migrating from OpenAI Assistant API:

```python
# Before (OpenAI Assistant)
assistant = client.beta.assistants.create(
    model="gpt-4",
    tools=[{"type": "file_search"}]
)
response = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Question"
)

# After (CustomRAG)
rag = CustomRAG()
rag.build_index()
response = rag.query("Question")
```

**Benefits:**
- ✅ Lower cost (no assistant API fees)
- ✅ Faster responses (local FAISS search)
- ✅ Full control over chunking and embedding
- ✅ No file upload limits

---

## Next Steps

- 📖 [Security API](security.md) - Security controls reference
- 🔧 [Error Handling API](error-handling.md) - Error handling utilities
- 📊 [Monitoring API](monitoring.md) - Metrics and logging

---

## Source Code

[View source on GitHub](https://github.com/BramAlkema/signal-rag-bot/blob/main/custom_rag.py)
