import numpy as np
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Any
import pickle
import os
from database.db_schema import DatabaseSchema

class VectorDatabase:
    """FAISS-based vector database for semantic search with PostgreSQL persistence"""
    
    def __init__(self):
        """
        Initialize the vector database with TF-IDF vectorization and PostgreSQL persistence
        """
        self.vectorizer = TfidfVectorizer(
            max_features=512,
            ngram_range=(1, 2),
            min_df=1,
            stop_words='english'
        )
        self.dimension = None  # Will be set dynamically
        self.index = None  # Will be created when first document is added
        
        # Store documents and metadata
        self.documents = []
        self.metadata = []
        self.is_fitted = False
        
        # Initialize database (optional for local use)
        self.db = None
        if os.getenv("DATABASE_URL"):
            try:
                self.db = DatabaseSchema()
                self._load_from_database()
            except Exception as e:
                print(f"Warning: Could not initialize database persistence: {e}")
                self.db = None
    
    def _load_from_database(self):
        """Load existing documents from database"""
        if not self.db:
            return
            
        try:
            stored_docs = self.db.load_all_documents()
            if stored_docs:
                for doc in stored_docs:
                    self.documents.append(doc['content'])
                    self.metadata.append(doc['metadata'])
                
                # Rebuild index with loaded documents
                self._rebuild_index()
                print(f"Loaded {len(stored_docs)} documents from database")
        except Exception as e:
            print(f"Error loading from database: {e}")
    
    def add_document(self, text: str, metadata: Dict[str, Any] = None):
        """
        Add a document to the vector database and persist to PostgreSQL
        
        Args:
            text: Document text content
            metadata: Optional metadata dictionary
        """
        try:
            # Split text into chunks if it's too long
            chunks = self._chunk_text(text, max_chunk_size=500)
            
            for i, chunk in enumerate(chunks):
                # Store document and metadata
                chunk_metadata = metadata.copy() if metadata else {}
                if len(chunks) > 1:
                    chunk_metadata['chunk_id'] = i
                    chunk_metadata['total_chunks'] = len(chunks)
                
                self.documents.append(chunk)
                self.metadata.append(chunk_metadata)
                
                # Save to database if available
                if self.db:
                    try:
                        self.db.save_document(chunk, chunk_metadata)
                    except Exception as e:
                        print(f"Warning: Could not save document to database: {e}")
            
            # Rebuild index with all documents
            self._rebuild_index()
                
        except Exception as e:
            raise Exception(f"Error adding document to vector database: {str(e)}")
    
    def _rebuild_index(self):
        """Rebuild the FAISS index with all documents"""
        if not self.documents:
            return
            
        # Fit vectorizer on all documents
        try:
            tfidf_matrix = self.vectorizer.fit_transform(self.documents)
            
            # Convert to dense numpy array and normalize
            embeddings = tfidf_matrix.toarray().astype(np.float32)
            
            # Set dimension based on actual TF-IDF output
            self.dimension = embeddings.shape[1]
            
            # Normalize for cosine similarity
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1  # Avoid division by zero
            embeddings = embeddings / norms
            
            # Create new FAISS index with correct dimension
            self.index = faiss.IndexFlatIP(self.dimension)
            self.index.add(embeddings)
            self.is_fitted = True
            
        except Exception as e:
            raise Exception(f"Error rebuilding index: {str(e)}")
    
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
            if len(self.documents) == 0 or not self.is_fitted:
                return []
            
            # Transform query using the fitted vectorizer
            query_vector = self.vectorizer.transform([query]).toarray().astype(np.float32)
            
            # Normalize query vector
            query_norm = np.linalg.norm(query_vector)
            if query_norm > 0:
                query_vector = query_vector / query_norm
            
            # Search in FAISS index
            scores, indices = self.index.search(
                query_vector, 
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
    
    def clear_all(self):
        """Clear all documents from memory and database"""
        self.documents = []
        self.metadata = []
        self.index = None
        self.dimension = None
        self.is_fitted = False
        
        if self.db:
            try:
                self.db.clear_all_documents()
            except Exception as e:
                print(f"Warning: Could not clear database: {e}")
    
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
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension or 0
        }
