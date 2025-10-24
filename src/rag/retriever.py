"""
Document retrieval system for RAG.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .vector_store import VectorStore
from .document_processor import Document

logger = logging.getLogger(__name__)


@dataclass
class RetrievedDocument:
    """Container for retrieved document with similarity score."""
    content: str
    metadata: Dict[str, Any]
    similarity: float
    rank: int


class DocumentRetriever:
    """Retrieves relevant documents for query answering."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        rerank: bool = True
    ):
        """
        Initialize document retriever.
        
        Args:
            vector_store: Vector store instance
            top_k: Number of documents to retrieve
            similarity_threshold: Minimum similarity score
            rerank: Whether to apply reranking
        """
        self.vector_store = vector_store
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.rerank = rerank
    
    async def retrieve(self, query: str, **kwargs) -> List[RetrievedDocument]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            **kwargs: Additional parameters (top_k, similarity_threshold)
            
        Returns:
            List of retrieved documents
        """
        # Override defaults with kwargs
        top_k = kwargs.get('top_k', self.top_k)
        similarity_threshold = kwargs.get('similarity_threshold', self.similarity_threshold)
        
        try:
            logger.info(f"Retrieving documents for query: '{query[:50]}...'")
            
            # Search vector store
            search_results = await self.vector_store.search(
                query=query,
                top_k=top_k * 2,  # Get more results for potential reranking
                similarity_threshold=similarity_threshold
            )
            
            if not search_results:
                logger.info("No relevant documents found")
                return []
            
            # Convert to RetrievedDocument objects
            retrieved_docs = []
            for result in search_results:
                retrieved_docs.append(RetrievedDocument(
                    content=result['content'],
                    metadata=result['metadata'],
                    similarity=result['similarity'],
                    rank=result['rank']
                ))
            
            # Apply reranking if enabled
            if self.rerank and len(retrieved_docs) > 1:
                retrieved_docs = await self._rerank_documents(query, retrieved_docs)
            
            # Limit to requested number
            retrieved_docs = retrieved_docs[:top_k]
            
            logger.info(f"Retrieved {len(retrieved_docs)} relevant documents")
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"Document retrieval failed: {e}")
            return []
    
    async def retrieve_by_source(
        self,
        query: str,
        source_filter: str,
        **kwargs
    ) -> List[RetrievedDocument]:
        """
        Retrieve documents filtered by source.
        
        Args:
            query: Search query
            source_filter: Source file pattern to filter by
            **kwargs: Additional parameters
            
        Returns:
            List of retrieved documents from matching sources
        """
        # Get all documents first
        all_docs = await self.retrieve(query, **kwargs)
        
        # Filter by source
        filtered_docs = []
        for doc in all_docs:
            source = doc.metadata.get('source', '')
            if source_filter.lower() in source.lower():
                filtered_docs.append(doc)
        
        logger.info(f"Filtered to {len(filtered_docs)} documents matching '{source_filter}'")
        return filtered_docs
    
    async def retrieve_by_type(
        self,
        query: str,
        doc_type: str,
        **kwargs
    ) -> List[RetrievedDocument]:
        """
        Retrieve documents filtered by document type.
        
        Args:
            query: Search query
            doc_type: Document type to filter by (pdf, txt, etc.)
            **kwargs: Additional parameters
            
        Returns:
            List of retrieved documents of specified type
        """
        # Get all documents first
        all_docs = await self.retrieve(query, **kwargs)
        
        # Filter by type
        filtered_docs = []
        for doc in all_docs:
            doc_doc_type = doc.metadata.get('type', '')
            if doc_type.lower() == doc_doc_type.lower():
                filtered_docs.append(doc)
        
        logger.info(f"Filtered to {len(filtered_docs)} documents of type '{doc_type}'")
        return filtered_docs
    
    async def get_document_context(
        self,
        query: str,
        max_chars: int = 4000
    ) -> str:
        """
        Get concatenated context from retrieved documents.
        
        Args:
            query: Search query
            max_chars: Maximum characters to return
            
        Returns:
            Concatenated document context
        """
        docs = await self.retrieve(query)
        
        if not docs:
            return ""
        
        context_parts = []
        total_chars = 0
        
        for i, doc in enumerate(docs):
            # Add source information
            source = doc.metadata.get('filename', f'Document {i+1}')
            doc_text = f"[Source: {source}]\n{doc.content}\n"
            
            if total_chars + len(doc_text) > max_chars:
                # Truncate the last document to fit
                remaining_chars = max_chars - total_chars
                if remaining_chars > 100:  # Only add if meaningful
                    truncated = doc_text[:remaining_chars] + "..."
                    context_parts.append(truncated)
                break
            
            context_parts.append(doc_text)
            total_chars += len(doc_text)
        
        context = "\n---\n".join(context_parts)
        logger.info(f"Generated context with {len(context)} characters from {len(context_parts)} documents")
        
        return context
    
    async def _rerank_documents(
        self,
        query: str,
        documents: List[RetrievedDocument]
    ) -> List[RetrievedDocument]:
        """
        Rerank documents using simple heuristics.
        
        Args:
            query: Original query
            documents: Documents to rerank
            
        Returns:
            Reranked documents
        """
        try:
            # Simple reranking based on query term frequency and document recency
            query_terms = set(query.lower().split())
            
            for doc in documents:
                # Count query term matches
                doc_text = doc.content.lower()
                term_matches = sum(1 for term in query_terms if term in doc_text)
                
                # Boost score based on term frequency
                term_boost = term_matches / len(query_terms) if query_terms else 0
                
                # Boost newer documents slightly
                modified_time = doc.metadata.get('modified', 0)
                recency_boost = min(0.1, modified_time / 1000000000000)  # Small boost for recent docs
                
                # Calculate new similarity score
                doc.similarity = doc.similarity + (term_boost * 0.1) + recency_boost
            
            # Sort by new similarity scores
            documents.sort(key=lambda x: x.similarity, reverse=True)
            
            # Update ranks
            for i, doc in enumerate(documents):
                doc.rank = i + 1
            
            logger.info("Documents reranked successfully")
            return documents
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return documents
    
    async def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get retrieval statistics."""
        try:
            vector_info = await self.vector_store.get_collection_info()
            
            return {
                'total_documents': vector_info.get('document_count', 0),
                'top_k': self.top_k,
                'similarity_threshold': self.similarity_threshold,
                'rerank_enabled': self.rerank,
                'embedding_model': vector_info.get('embedding_model', 'unknown')
            }
        except Exception as e:
            logger.error(f"Failed to get retrieval stats: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    from .vector_store import VectorStore
    from .document_processor import Document
    
    async def main():
        # Initialize components
        vector_store = VectorStore()
        retriever = DocumentRetriever(vector_store)
        
        # Add sample documents
        sample_docs = [
            Document(
                content="Python is a high-level programming language known for its simplicity and readability.",
                metadata={"source": "python_intro.txt", "type": "text", "modified": 1640995200},
                doc_id="doc1"
            ),
            Document(
                content="Machine learning algorithms can be used to build predictive models from data.",
                metadata={"source": "ml_basics.pdf", "type": "pdf", "modified": 1641081600},
                doc_id="doc2"
            ),
            Document(
                content="Flask is a lightweight web framework for Python applications.",
                metadata={"source": "flask_guide.md", "type": "markdown", "modified": 1641168000},
                doc_id="doc3"
            )
        ]
        
        try:
            await vector_store.add_documents(sample_docs)
            
            # Test retrieval
            query = "What is Python programming?"
            docs = await retriever.retrieve(query, top_k=2)
            
            print(f"Retrieved {len(docs)} documents for: '{query}'")
            for doc in docs:
                print(f"Rank {doc.rank}: {doc.content[:100]}... (similarity: {doc.similarity:.3f})")
                print(f"Source: {doc.metadata.get('source', 'unknown')}")
                print("---")
            
            # Test context generation
            context = await retriever.get_document_context(query, max_chars=500)
            print(f"\nGenerated context ({len(context)} chars):\n{context}")
            
            # Get stats
            stats = await retriever.get_retrieval_stats()
            print(f"\nRetrieval stats: {stats}")
            
        finally:
            await vector_store.cleanup()
    
    asyncio.run(main())