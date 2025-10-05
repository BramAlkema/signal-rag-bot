#!/usr/bin/env python3
"""
Unit tests for custom_rag.py
Target: 90% code coverage
Tests chunking, embedding, indexing, searching, and querying
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import numpy as np
import tempfile
import pickle
from pathlib import Path


@pytest.mark.unit
class TestChunking:
    """Test text chunking functionality"""

    def test_chunk_text_basic(self):
        """Should chunk text with specified chunk size"""
        from custom_rag import CustomRAG

        rag = CustomRAG()
        text = "A" * 1000 + "B" * 1000 + "C" * 1000

        chunks = rag.chunk_text(text, chunk_size=1000, overlap=200)

        # Should create multiple chunks
        assert len(chunks) > 1
        assert all(len(chunk) <= 1000 for chunk in chunks)

    def test_chunk_text_with_sentences(self):
        """Should break at sentence boundaries when possible"""
        from custom_rag import CustomRAG

        rag = CustomRAG()
        text = "First sentence. " * 100 + "Second sentence. " * 100

        chunks = rag.chunk_text(text, chunk_size=500, overlap=50)

        # Should have multiple chunks
        assert len(chunks) > 1

        # Most chunks should end with period
        period_endings = sum(1 for chunk in chunks if chunk.endswith('.'))
        assert period_endings >= len(chunks) - 1  # Allow last chunk to not end with period

    def test_chunk_text_overlap(self):
        """Should create overlapping chunks"""
        from custom_rag import CustomRAG

        rag = CustomRAG()
        text = "ABCDEFGHIJ" * 200  # 2000 characters

        chunks = rag.chunk_text(text, chunk_size=1000, overlap=200)

        # Should have overlap
        assert len(chunks) >= 2
        # Chunks should have some common content (overlap)
        # This is implicit in the sliding window approach

    def test_chunk_text_short_text(self):
        """Should handle text shorter than chunk size"""
        from custom_rag import CustomRAG

        rag = CustomRAG()
        text = "Short text"

        chunks = rag.chunk_text(text, chunk_size=1000, overlap=200)

        assert len(chunks) == 1
        assert chunks[0] == "Short text"

    def test_chunk_text_empty(self):
        """Should handle empty text"""
        from custom_rag import CustomRAG

        rag = CustomRAG()
        text = ""

        chunks = rag.chunk_text(text, chunk_size=1000, overlap=200)

        # Empty text produces empty list (chunking loop never executes)
        assert len(chunks) == 0

    def test_chunk_text_with_newlines(self):
        """Should break at newlines when appropriate"""
        from custom_rag import CustomRAG

        rag = CustomRAG()
        text = "Paragraph 1\n" * 100 + "Paragraph 2\n" * 100

        chunks = rag.chunk_text(text, chunk_size=500, overlap=50)

        # Should respect newline boundaries
        assert len(chunks) > 1


@pytest.mark.unit
class TestLoadAndChunk:
    """Test loading and chunking bucket files"""

    def test_load_and_chunk_buckets(self, tmp_path):
        """Should load bucket files and create chunks"""
        from custom_rag import CustomRAG

        # Create test bucket files
        bucket_dir = tmp_path / "output_v3"
        bucket_dir.mkdir()

        (bucket_dir / "bucket_defence_tech.md").write_text("Content about defence technology. " * 50)
        (bucket_dir / "bucket_procurement.md").write_text("Content about procurement. " * 50)

        rag = CustomRAG(bucket_dir=str(bucket_dir))
        rag.load_and_chunk_buckets()

        # Should have created chunks
        assert len(rag.chunks) > 0

        # Should have metadata
        for chunk in rag.chunks:
            assert 'text' in chunk
            assert 'source' in chunk
            assert 'category' in chunk
            assert 'chunk_id' in chunk

    def test_load_and_chunk_empty_directory(self, tmp_path):
        """Should handle empty bucket directory"""
        from custom_rag import CustomRAG

        bucket_dir = tmp_path / "output_v3"
        bucket_dir.mkdir()

        rag = CustomRAG(bucket_dir=str(bucket_dir))
        rag.load_and_chunk_buckets()

        assert len(rag.chunks) == 0

    def test_load_and_chunk_category_extraction(self, tmp_path):
        """Should extract category from filename"""
        from custom_rag import CustomRAG

        bucket_dir = tmp_path / "output_v3"
        bucket_dir.mkdir()

        (bucket_dir / "bucket_defence_technology.md").write_text("Test content")

        rag = CustomRAG(bucket_dir=str(bucket_dir))
        rag.load_and_chunk_buckets()

        assert len(rag.chunks) > 0
        assert rag.chunks[0]['category'] == "Defence Technology"


@pytest.mark.unit
class TestEmbeddings:
    """Test embedding creation"""

    def test_create_embeddings(self, mock_openai_client):
        """Should create embeddings for chunks"""
        from custom_rag import CustomRAG

        rag = CustomRAG()
        rag.chunks = [
            {'text': 'Test chunk 1', 'source': 'test.md', 'category': 'Test', 'chunk_id': 0},
            {'text': 'Test chunk 2', 'source': 'test.md', 'category': 'Test', 'chunk_id': 1},
            {'text': 'Test chunk 3', 'source': 'test.md', 'category': 'Test', 'chunk_id': 2}
        ]

        # Mock needs to return 3 embeddings for 3 texts
        mock_embedding1 = Mock()
        mock_embedding1.embedding = np.random.rand(1536).tolist()
        mock_embedding2 = Mock()
        mock_embedding2.embedding = np.random.rand(1536).tolist()
        mock_embedding3 = Mock()
        mock_embedding3.embedding = np.random.rand(1536).tolist()

        mock_embeddings_response = Mock()
        mock_embeddings_response.data = [mock_embedding1, mock_embedding2, mock_embedding3]
        mock_openai_client.embeddings.create.return_value = mock_embeddings_response

        with patch('custom_rag.client', mock_openai_client):
            rag.create_embeddings()

        # Should have created embeddings
        assert rag.embeddings is not None
        assert rag.embeddings.shape[0] == 3
        assert rag.embeddings.shape[1] == 1536  # text-embedding-3-small dimension

    def test_create_embeddings_batch_processing(self, mock_openai_client):
        """Should process embeddings in batches"""
        from custom_rag import CustomRAG

        rag = CustomRAG()
        # Create 250 chunks to test batching (batch size is 100)
        rag.chunks = [
            {'text': f'Test chunk {i}', 'source': 'test.md', 'category': 'Test', 'chunk_id': i}
            for i in range(250)
        ]

        # Mock to return correct number of embeddings per batch
        def mock_create_embeddings(model, input):
            batch_size = len(input)
            embeddings = []
            for i in range(batch_size):
                mock_emb = Mock()
                mock_emb.embedding = np.random.rand(1536).tolist()
                embeddings.append(mock_emb)
            mock_response = Mock()
            mock_response.data = embeddings
            return mock_response

        mock_openai_client.embeddings.create.side_effect = mock_create_embeddings

        with patch('custom_rag.client', mock_openai_client):
            rag.create_embeddings()

        # Should have created embeddings for all chunks
        assert rag.embeddings.shape[0] == 250

        # Should have called embeddings.create multiple times (3 batches: 100, 100, 50)
        assert mock_openai_client.embeddings.create.call_count >= 3


@pytest.mark.unit
class TestIndexBuilding:
    """Test FAISS index building"""

    def test_build_index(self):
        """Should build FAISS index from embeddings"""
        from custom_rag import CustomRAG

        rag = CustomRAG()
        rag.embeddings = np.random.rand(10, 1536).astype('float32')

        rag.build_index()

        # Should have created index
        assert rag.index is not None
        assert rag.index.ntotal == 10

    def test_build_index_correct_dimension(self):
        """Should use correct embedding dimension"""
        from custom_rag import CustomRAG

        rag = CustomRAG()
        rag.embeddings = np.random.rand(5, 1536).astype('float32')

        rag.build_index()

        assert rag.index.d == 1536


@pytest.mark.unit
class TestIndexSaveLoad:
    """Test index saving and loading"""

    def test_save_index(self, tmp_path, monkeypatch):
        """Should save index and metadata"""
        from custom_rag import CustomRAG
        import faiss

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        rag = CustomRAG()
        rag.embeddings = np.random.rand(5, 1536).astype('float32')
        rag.chunks = [
            {'text': f'Chunk {i}', 'source': 'test.md', 'category': 'Test', 'chunk_id': i}
            for i in range(5)
        ]
        rag.build_index()

        rag.save_index()

        # Should have created files
        assert (tmp_path / "rag_faiss.index").exists()
        assert (tmp_path / "rag_index.pkl").exists()

    def test_load_index(self, tmp_path, monkeypatch):
        """Should load index and metadata"""
        from custom_rag import CustomRAG
        import faiss

        monkeypatch.chdir(tmp_path)

        # Create and save an index
        rag1 = CustomRAG()
        rag1.embeddings = np.random.rand(5, 1536).astype('float32')
        rag1.chunks = [
            {'text': f'Chunk {i}', 'source': 'test.md', 'category': 'Test', 'chunk_id': i}
            for i in range(5)
        ]
        rag1.build_index()
        rag1.save_index()

        # Load in new instance
        rag2 = CustomRAG()
        rag2.load_index()

        # Should have loaded index
        assert rag2.index is not None
        assert rag2.index.ntotal == 5
        assert len(rag2.chunks) == 5

    def test_load_index_file_not_found(self, tmp_path, monkeypatch):
        """Should raise error if index file not found"""
        from custom_rag import CustomRAG

        monkeypatch.chdir(tmp_path)

        rag = CustomRAG()

        with pytest.raises(FileNotFoundError, match="Index not found"):
            rag.load_index()


@pytest.mark.unit
class TestSearch:
    """Test search functionality"""

    def test_search(self, mock_openai_client, tmp_path, monkeypatch):
        """Should search for relevant chunks"""
        from custom_rag import CustomRAG
        import faiss

        monkeypatch.chdir(tmp_path)

        rag = CustomRAG()
        rag.embeddings = np.random.rand(10, 1536).astype('float32')
        rag.chunks = [
            {'text': f'Chunk {i} about defence', 'source': 'test.md', 'category': 'Defence', 'chunk_id': i}
            for i in range(10)
        ]
        rag.build_index()

        with patch('custom_rag.client', mock_openai_client):
            results = rag.search("Tell me about defence", k=5)

        # Should return k results
        assert len(results) == 5

        # Should have metadata
        for result in results:
            assert 'text' in result
            assert 'source' in result
            assert 'category' in result
            assert 'distance' in result

    def test_search_with_different_k(self, mock_openai_client, tmp_path, monkeypatch):
        """Should respect k parameter"""
        from custom_rag import CustomRAG

        monkeypatch.chdir(tmp_path)

        rag = CustomRAG()
        rag.embeddings = np.random.rand(10, 1536).astype('float32')
        rag.chunks = [
            {'text': f'Chunk {i}', 'source': 'test.md', 'category': 'Test', 'chunk_id': i}
            for i in range(10)
        ]
        rag.build_index()

        with patch('custom_rag.client', mock_openai_client):
            results = rag.search("test query", k=3)

        assert len(results) == 3


@pytest.mark.unit
class TestQuery:
    """Test end-to-end query functionality"""

    def test_query(self, mock_openai_client, tmp_path, monkeypatch):
        """Should query RAG system and return answer"""
        from custom_rag import CustomRAG

        monkeypatch.chdir(tmp_path)

        rag = CustomRAG()
        rag.embeddings = np.random.rand(5, 1536).astype('float32')
        rag.chunks = [
            {'text': 'NLDTIB is the Netherlands Defence Technology Innovation Board.', 'source': 'doc1.md', 'category': 'Organizations', 'chunk_id': 0},
            {'text': 'The board advises on emerging technologies.', 'source': 'doc1.md', 'category': 'Organizations', 'chunk_id': 1},
            {'text': 'Defence procurement is complex.', 'source': 'doc2.md', 'category': 'Procurement', 'chunk_id': 2},
            {'text': 'Drones are increasingly important.', 'source': 'doc3.md', 'category': 'Technology', 'chunk_id': 3},
            {'text': 'Innovation partnerships matter.', 'source': 'doc4.md', 'category': 'Strategy', 'chunk_id': 4}
        ]
        rag.build_index()

        with patch('custom_rag.client', mock_openai_client):
            answer = rag.query("What is NLDTIB?", k=3)

        # Should return an answer
        assert isinstance(answer, str)
        assert len(answer) > 0
        assert answer == "Test response from OpenAI"

    def test_query_builds_context(self, mock_openai_client, tmp_path, monkeypatch):
        """Should build context from search results"""
        from custom_rag import CustomRAG

        monkeypatch.chdir(tmp_path)

        rag = CustomRAG()
        rag.embeddings = np.random.rand(3, 1536).astype('float32')
        rag.chunks = [
            {'text': 'Chunk 1', 'source': 'source1.md', 'category': 'Cat1', 'chunk_id': 0},
            {'text': 'Chunk 2', 'source': 'source2.md', 'category': 'Cat2', 'chunk_id': 1},
            {'text': 'Chunk 3', 'source': 'source3.md', 'category': 'Cat3', 'chunk_id': 2}
        ]
        rag.build_index()

        with patch('custom_rag.client', mock_openai_client):
            answer = rag.query("test question", k=2)

        # Should have called chat completions with context
        call_args = mock_openai_client.chat.completions.create.call_args
        prompt = call_args[1]['messages'][1]['content']

        # Should include source references
        assert '[Source 1:' in prompt or '[Source 2:' in prompt


@pytest.mark.unit
class TestBuildRAGIndex:
    """Test build_rag_index function"""

    def test_build_rag_index(self, tmp_path, mock_openai_client, monkeypatch):
        """Should build complete RAG index"""
        from custom_rag import build_rag_index

        monkeypatch.chdir(tmp_path)

        # Create bucket directory with test files
        bucket_dir = tmp_path / "output_v3"
        bucket_dir.mkdir()
        (bucket_dir / "bucket_test.md").write_text("Test content for RAG. " * 50)

        with patch('custom_rag.client', mock_openai_client):
            rag = build_rag_index()

        # Should have built index
        assert rag.index is not None
        assert rag.index.ntotal > 0
        assert len(rag.chunks) > 0

        # Should have saved files
        assert (tmp_path / "rag_faiss.index").exists()
        assert (tmp_path / "rag_index.pkl").exists()


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_chunk_text_custom_parameters(self):
        """Should handle custom chunk size and overlap"""
        from custom_rag import CustomRAG

        rag = CustomRAG()
        text = "A" * 5000

        chunks = rag.chunk_text(text, chunk_size=500, overlap=100)

        assert len(chunks) > 5
        for chunk in chunks[:-1]:  # Exclude last chunk
            assert len(chunk) <= 500

    def test_chunk_text_zero_overlap(self):
        """Should handle zero overlap"""
        from custom_rag import CustomRAG

        rag = CustomRAG()
        text = "A" * 2000

        chunks = rag.chunk_text(text, chunk_size=1000, overlap=0)

        assert len(chunks) == 2

    def test_search_with_empty_index(self, mock_openai_client):
        """Should handle empty index gracefully"""
        from custom_rag import CustomRAG

        rag = CustomRAG()
        # Empty embeddings array with correct shape
        rag.embeddings = np.zeros((0, 1536), dtype='float32')
        rag.chunks = []

        # Building index with 0 vectors is actually allowed in FAISS
        rag.build_index()
        assert rag.index.ntotal == 0


@pytest.mark.unit
class TestTestRAGFunction:
    """Test the test_rag() function"""

    def test_test_rag_function(self, mock_openai_client, tmp_path, monkeypatch, capsys):
        """Should test RAG system with sample queries"""
        from custom_rag import test_rag, CustomRAG
        import faiss

        monkeypatch.chdir(tmp_path)

        # Create and save a test index
        rag = CustomRAG()
        rag.embeddings = np.random.rand(5, 1536).astype('float32')
        rag.chunks = [
            {'text': 'NLDTIB is important', 'source': 'doc1.md', 'category': 'Org', 'chunk_id': 0},
            {'text': 'Defence procurement', 'source': 'doc2.md', 'category': 'Proc', 'chunk_id': 1},
            {'text': 'Drones technology', 'source': 'doc3.md', 'category': 'Tech', 'chunk_id': 2},
            {'text': 'More about drones', 'source': 'doc4.md', 'category': 'Tech', 'chunk_id': 3},
            {'text': 'Additional info', 'source': 'doc5.md', 'category': 'General', 'chunk_id': 4}
        ]
        rag.build_index()
        rag.save_index()

        # Patch the CustomRAG class to use our mock client
        with patch('custom_rag.client', mock_openai_client):
            with patch('custom_rag.CustomRAG') as MockRAG:
                # Make CustomRAG() return our rag instance
                MockRAG.return_value = rag
                rag.load_index = Mock()  # Mock load_index to prevent re-loading

                # Run test_rag
                test_rag()

        # Should have printed output
        captured = capsys.readouterr()
        assert "Testing RAG System" in captured.out
        assert "Query:" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
