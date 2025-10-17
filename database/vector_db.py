import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import pickle
import os

class VectorDatabase:
    """FAISS-based vector database for semantic search"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the vector database
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product for cosine similarity
        
        # Store documents and metadata
        self.documents = []
        self.metadata = []
        
    def add_document(self, text: str, metadata: Dict[str, Any] = None):
        """
        Add a document to the vector database
        
        Args:
            text: Document text content
            metadata: Optional metadata dictionary
        """
        try:
            # Split text into chunks if it's too long (to avoid token limits)
            chunks = self._chunk_text(text, max_chunk_size=500)
            
            for i, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self.model.encode([chunk])[0]
                
                # Normalize embedding for cosine similarity
                embedding = embedding / np.linalg.norm(embedding)
                
                # Add to FAISS index
                self.index.add(np.array([embedding], dtype=np.float32))
                
                # Store document and metadata
                chunk_metadata = metadata.copy() if metadata else {}
                if len(chunks) > 1:
                    chunk_metadata['chunk_id'] = i
                    chunk_metadata['total_chunks'] = len(chunks)
                
                self.documents.append(chunk)
                self.metadata.append(chunk_metadata)
                
        except Exception as e:
            raise Exception(f"Error adding document to vector database: {str(e)}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of search results with content, metadata, and scores
        """
        try:
            if len(self.documents) == 0:
                return []
            
            # Generate query embedding
            query_embedding = self.model.encode([query])[0]
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            
            # Search in FAISS index
            scores, indices = self.index.search(
                np.array([query_embedding], dtype=np.float32), 
                min(top_k, len(self.documents))
            )
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx != -1:  # Valid index
                    results.append({
                        'content': self.documents[idx],
                        'metadata': self.metadata[idx],
                        'score': float(score),
                        'rank': i + 1
                    })
            
            return results
            
        except Exception as e:
            raise Exception(f"Error searching vector database: {str(e)}")
    
    def _chunk_text(self, text: str, max_chunk_size: int = 500) -> List[str]:
        """
        Split text into chunks for better processing
        
        Args:
            text: Input text
            max_chunk_size: Maximum characters per chunk
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_chunk_size:
            return [text]
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed the limit
            if len(current_chunk) + len(paragraph) + 2 > max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # If paragraph itself is too long, split by sentences
                if len(paragraph) > max_chunk_size:
                    sentences = paragraph.split('. ')
                    temp_chunk = ""
                    
                    for sentence in sentences:
                        if len(temp_chunk) + len(sentence) + 2 > max_chunk_size:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                                temp_chunk = ""
                        temp_chunk += sentence + ". "
                    
                    if temp_chunk:
                        current_chunk = temp_chunk.strip()
                else:
                    current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get database statistics
        
        Returns:
            Dictionary with database stats
        """
        return {
            'total_documents': len(self.documents),
            'total_vectors': self.index.ntotal,
            'dimension': self.dimension
        }
