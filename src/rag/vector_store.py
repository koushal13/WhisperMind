"""
Vector store implementation using ChromaDB.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import uuid

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    logging.warning(f"ChromaDB or sentence-transformers not available: {e}")

from .document_processor import Document

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB-based vector store for document embeddings."""
    
    def __init__(
        self,
        persist_directory: str = "models/chromadb",
        collection_name: str = "documents",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize vector store.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
            embedding_model: Sentence transformer model for embeddings
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        
        self.client = None
        self.collection = None
        self.embedding_model = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize ChromaDB client and collection."""
        if self._initialized:
            return
        
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Document embeddings for RAG"}
            )
            
            # Initialize embedding model
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            
            self._initialized = True
            logger.info("Vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    async def add_documents(self, documents: List[Document]) -> bool:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents to add
            
        Returns:
            True if successful
        """
        if not self._initialized:
            await self.initialize()
        
        if not documents:
            logger.warning("No documents to add")
            return True
        
        try:
            logger.info(f"Adding {len(documents)} documents to vector store")
            
            # Prepare data for ChromaDB
            ids = []
            embeddings = []
            metadatas = []
            documents_text = []
            
            for doc in documents:
                # Generate embedding
                embedding = await self._generate_embedding(doc.content)
                
                ids.append(doc.doc_id)
                embeddings.append(embedding)
                metadatas.append(doc.metadata)
                documents_text.append(doc.content)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents_text
            )
            
            logger.info(f"Successfully added {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of search results with documents and scores
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Process results
            search_results = []
            
            if results['documents'] and results['documents'][0]:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(documents)
                distances = results['distances'][0] if results['distances'] else [0.0] * len(documents)
                
                for i, (doc_text, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                    # Convert distance to similarity score (ChromaDB uses L2 distance)
                    similarity = 1.0 / (1.0 + distance)
                    
                    if similarity >= similarity_threshold:
                        search_results.append({
                            'content': doc_text,
                            'metadata': metadata,
                            'similarity': similarity,
                            'rank': i + 1
                        })
            
            logger.info(f"Found {len(search_results)} relevant documents for query")
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def get_document_count(self) -> int:
        """Get total number of documents in the store."""
        if not self._initialized:
            await self.initialize()
        
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            return 0
    
    async def delete_documents(self, doc_ids: List[str]) -> bool:
        """
        Delete documents by ID.
        
        Args:
            doc_ids: List of document IDs to delete
            
        Returns:
            True if successful
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            self.collection.delete(ids=doc_ids)
            logger.info(f"Deleted {len(doc_ids)} documents")
            return True
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return False
    
    async def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document embeddings for RAG"}
            )
            logger.info("Collection cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        if not self._initialized:
            await self.initialize()
        
        try:
            count = await self.get_document_count()
            return {
                'name': self.collection_name,
                'document_count': count,
                'embedding_model': self.embedding_model_name,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # Use sentence transformer to generate embedding
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 384  # MiniLM embedding dimension
    
    async def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up vector store resources")
        self._initialized = False


# Example usage
if __name__ == "__main__":
    from .document_processor import Document
    
    async def main():
        vector_store = VectorStore()
        
        # Create sample documents
        sample_docs = [
            Document(
                content="Machine learning is a subset of artificial intelligence.",
                metadata={"source": "sample1.txt", "topic": "AI"},
                doc_id="doc1"
            ),
            Document(
                content="Deep learning uses neural networks with multiple layers.",
                metadata={"source": "sample2.txt", "topic": "AI"},
                doc_id="doc2"
            )
        ]
        
        try:
            # Add documents
            await vector_store.add_documents(sample_docs)
            
            # Search
            results = await vector_store.search("What is machine learning?", top_k=2)
            
            print(f"Search results: {len(results)}")
            for result in results:
                print(f"Content: {result['content'][:100]}...")
                print(f"Similarity: {result['similarity']:.3f}")
                print("---")
            
            # Get info
            info = await vector_store.get_collection_info()
            print(f"Collection info: {info}")
            
        finally:
            await vector_store.cleanup()
    
    asyncio.run(main())