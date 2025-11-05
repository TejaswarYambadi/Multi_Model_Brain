import os
import psycopg2
from psycopg2.extras import Json
import pickle

class DatabaseSchema:
    """Manages PostgreSQL database schema and operations"""
    
    def __init__(self):
        self.__database_url = os.getenv("DATABASE_URL")
        if not self.__database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        self.init_tables()
    
    def _get_connection(self):
        """Get a new database connection"""
        return psycopg2.connect(self.__database_url)
    
    def init_tables(self):
        """Initialize database tables"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # Create documents table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        metadata JSONB,
                        vector BYTEA,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create index on metadata for faster queries
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_documents_metadata 
                    ON documents USING GIN (metadata)
                """)
                
                # Create query history table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS query_history (
                        id SERIAL PRIMARY KEY,
                        query TEXT NOT NULL,
                        answer TEXT,
                        sources JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
        finally:
            conn.close()
    
    def save_document(self, content: str, metadata: dict, vector: bytes = None):
        """Save a document with its vector to the database"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO documents (content, metadata, vector)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (content, Json(metadata), vector)
                )
                doc_id = cur.fetchone()[0]
                conn.commit()
                return doc_id
        finally:
            conn.close()
    
    def load_all_documents(self):
        """Load all documents from the database"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, content, metadata, vector
                    FROM documents
                    ORDER BY created_at
                """)
                rows = cur.fetchall()
                return [
                    {
                        'id': row[0],
                        'content': row[1],
                        'metadata': row[2],
                        'vector': row[3]
                    }
                    for row in rows
                ]
        finally:
            conn.close()
    
    def clear_all_documents(self):
        """Clear all documents from the database"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM documents")
                conn.commit()
        finally:
            conn.close()
    
    def save_query(self, query: str, answer: str, sources: list):
        """Save a query and its answer to history"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO query_history (query, answer, sources)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (query, answer, Json(sources))
                )
                query_id = cur.fetchone()[0]
                conn.commit()
                return query_id
        finally:
            conn.close()
    
    def get_query_history(self, limit: int = 50):
        """Get recent query history"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, query, answer, sources, created_at
                    FROM query_history
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (limit,))
                rows = cur.fetchall()
                return [
                    {
                        'id': row[0],
                        'query': row[1],
                        'answer': row[2],
                        'sources': row[3],
                        'created_at': row[4]
                    }
                    for row in rows
                ]
        finally:
            conn.close()
    
    def clear_query_history(self):
        """Clear all query history"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM query_history")
                conn.commit()
        finally:
            conn.close()
