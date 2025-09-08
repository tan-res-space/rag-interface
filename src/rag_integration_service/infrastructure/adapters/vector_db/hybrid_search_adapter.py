"""
Hybrid Search Adapter

Advanced vector storage adapter that combines semantic vector search
with traditional keyword search for improved retrieval accuracy.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID
import asyncio
from collections import defaultdict
import math

from rag_integration_service.application.ports.secondary.vector_storage_port import VectorStoragePort as BaseVectorStorageAdapter
from rag_integration_service.domain.entities.vector_embedding import VectorEmbedding
from rag_integration_service.domain.value_objects.similarity_result import SimilarityResult

logger = logging.getLogger(__name__)


class HybridSearchAdapter(BaseVectorStorageAdapter):
    """
    Hybrid search adapter combining semantic and keyword search.
    
    Provides advanced search capabilities by combining:
    - Semantic vector similarity search
    - Traditional keyword/BM25 search
    - Intelligent result fusion and ranking
    """

    def __init__(
        self,
        vector_adapter: BaseVectorStorageAdapter,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
        enable_fuzzy_matching: bool = True,
        min_keyword_score: float = 0.1
    ):
        """
        Initialize hybrid search adapter.
        
        Args:
            vector_adapter: Base vector storage adapter
            semantic_weight: Weight for semantic search results
            keyword_weight: Weight for keyword search results
            enable_fuzzy_matching: Whether to enable fuzzy keyword matching
            min_keyword_score: Minimum keyword score threshold
        """
        self.vector_adapter = vector_adapter
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.enable_fuzzy_matching = enable_fuzzy_matching
        self.min_keyword_score = min_keyword_score
        
        # Keyword index for fast text search
        self.keyword_index: Dict[str, Set[UUID]] = defaultdict(set)
        self.document_frequencies: Dict[str, int] = defaultdict(int)
        self.total_documents = 0
        
        # Text storage for keyword search
        self.text_storage: Dict[UUID, str] = {}
        
        logger.info(f"Initialized hybrid search with weights: semantic={semantic_weight}, keyword={keyword_weight}")

    async def store_embedding(self, embedding: VectorEmbedding) -> bool:
        """Store embedding and update keyword index."""
        try:
            # Store in vector adapter
            success = await self.vector_adapter.store_embedding(embedding)
            
            if success:
                # Update keyword index
                await self._update_keyword_index(embedding)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to store embedding in hybrid adapter: {e}")
            return False

    async def store_batch_embeddings(self, embeddings: List[VectorEmbedding]) -> bool:
        """Store batch embeddings and update keyword index."""
        try:
            # Store in vector adapter
            success = await self.vector_adapter.store_batch_embeddings(embeddings)
            
            if success:
                # Update keyword index for all embeddings
                for embedding in embeddings:
                    await self._update_keyword_index(embedding)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to store batch embeddings in hybrid adapter: {e}")
            return False

    async def find_similar(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        threshold: float = 0.7,
    ) -> List[SimilarityResult]:
        """Find similar vectors using semantic search only."""
        return await self.vector_adapter.find_similar(query_vector, top_k, filters, threshold)

    async def hybrid_search(
        self,
        query_text: str,
        query_vector: Optional[List[float]] = None,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        threshold: float = 0.7,
        semantic_weight: Optional[float] = None,
        keyword_weight: Optional[float] = None
    ) -> List[SimilarityResult]:
        """
        Perform hybrid search combining semantic and keyword search.
        
        Args:
            query_text: Query text for keyword search
            query_vector: Query vector for semantic search
            top_k: Number of results to return
            filters: Optional metadata filters
            threshold: Similarity threshold
            semantic_weight: Override semantic weight
            keyword_weight: Override keyword weight
            
        Returns:
            Ranked list of hybrid search results
        """
        try:
            # Use instance weights if not overridden
            sem_weight = semantic_weight or self.semantic_weight
            key_weight = keyword_weight or self.keyword_weight
            
            # Perform semantic search if vector provided
            semantic_results = []
            if query_vector:
                semantic_results = await self.vector_adapter.find_similar(
                    query_vector, top_k * 2, filters, threshold  # Get more results for fusion
                )
            
            # Perform keyword search
            keyword_results = await self._keyword_search(query_text, top_k * 2, filters)
            
            # Fuse and rank results
            hybrid_results = await self._fuse_results(
                semantic_results, keyword_results, sem_weight, key_weight
            )
            
            # Return top-k results
            return hybrid_results[:top_k]
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            # Fallback to semantic search if available
            if query_vector:
                return await self.vector_adapter.find_similar(query_vector, top_k, filters, threshold)
            return []

    async def _keyword_search(
        self,
        query_text: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[UUID, float]]:
        """
        Perform keyword-based search using BM25-like scoring.
        
        Args:
            query_text: Query text
            top_k: Number of results
            filters: Optional filters
            
        Returns:
            List of (embedding_id, score) tuples
        """
        try:
            # Tokenize query
            query_tokens = self._tokenize(query_text.lower())
            
            if not query_tokens:
                return []
            
            # Calculate BM25 scores
            scores: Dict[UUID, float] = defaultdict(float)
            
            for token in query_tokens:
                # Get documents containing this token
                doc_ids = self.keyword_index.get(token, set())
                
                if not doc_ids:
                    continue
                
                # Calculate IDF
                df = self.document_frequencies.get(token, 0)
                idf = math.log((self.total_documents + 1) / (df + 1))
                
                # Calculate scores for documents containing this token
                for doc_id in doc_ids:
                    if doc_id in self.text_storage:
                        doc_text = self.text_storage[doc_id]
                        tf = self._calculate_term_frequency(token, doc_text)
                        
                        # BM25 scoring (simplified)
                        k1, b = 1.5, 0.75
                        doc_length = len(self._tokenize(doc_text))
                        avg_doc_length = sum(len(self._tokenize(text)) for text in self.text_storage.values()) / len(self.text_storage)
                        
                        score = idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_length / avg_doc_length)))
                        scores[doc_id] += score
            
            # Apply filters if provided
            if filters:
                filtered_scores = {}
                for doc_id, score in scores.items():
                    # Get embedding to check filters
                    embedding = await self.vector_adapter.get_embedding(doc_id)
                    if embedding and self._matches_filters(embedding.metadata, filters):
                        filtered_scores[doc_id] = score
                scores = filtered_scores
            
            # Sort by score and return top-k
            sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return [(doc_id, score) for doc_id, score in sorted_results[:top_k] if score >= self.min_keyword_score]
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []

    async def _fuse_results(
        self,
        semantic_results: List[SimilarityResult],
        keyword_results: List[Tuple[UUID, float]],
        semantic_weight: float,
        keyword_weight: float
    ) -> List[SimilarityResult]:
        """
        Fuse semantic and keyword search results.
        
        Args:
            semantic_results: Semantic search results
            keyword_results: Keyword search results
            semantic_weight: Weight for semantic scores
            keyword_weight: Weight for keyword scores
            
        Returns:
            Fused and ranked results
        """
        try:
            # Create combined score dictionary
            combined_scores: Dict[UUID, Dict[str, Any]] = {}
            
            # Add semantic results
            for result in semantic_results:
                combined_scores[result.embedding_id] = {
                    "semantic_score": result.similarity_score,
                    "keyword_score": 0.0,
                    "embedding": result.embedding,
                    "metadata": result.metadata
                }
            
            # Add keyword results
            for doc_id, keyword_score in keyword_results:
                if doc_id in combined_scores:
                    combined_scores[doc_id]["keyword_score"] = keyword_score
                else:
                    # Get embedding for keyword-only results
                    embedding = await self.vector_adapter.get_embedding(doc_id)
                    if embedding:
                        combined_scores[doc_id] = {
                            "semantic_score": 0.0,
                            "keyword_score": keyword_score,
                            "embedding": embedding,
                            "metadata": embedding.metadata
                        }
            
            # Calculate combined scores
            fused_results = []
            for doc_id, scores in combined_scores.items():
                # Normalize scores to 0-1 range
                norm_semantic = min(scores["semantic_score"], 1.0)
                norm_keyword = min(scores["keyword_score"] / 10.0, 1.0)  # Assuming max keyword score ~10
                
                # Calculate weighted combined score
                combined_score = (
                    semantic_weight * norm_semantic + 
                    keyword_weight * norm_keyword
                )
                
                # Create result
                result = SimilarityResult(
                    embedding_id=doc_id,
                    similarity_score=combined_score,
                    embedding=scores["embedding"],
                    metadata=scores["metadata"]
                )
                fused_results.append(result)
            
            # Sort by combined score
            fused_results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            logger.debug(f"Fused {len(semantic_results)} semantic + {len(keyword_results)} keyword results")
            return fused_results
            
        except Exception as e:
            logger.error(f"Result fusion failed: {e}")
            return semantic_results  # Fallback to semantic results

    async def _update_keyword_index(self, embedding: VectorEmbedding):
        """Update keyword index with new embedding."""
        try:
            # Store text for keyword search
            self.text_storage[embedding.id] = embedding.text
            
            # Tokenize text
            tokens = self._tokenize(embedding.text.lower())
            
            # Update keyword index
            for token in set(tokens):  # Use set to avoid counting duplicates
                self.keyword_index[token].add(embedding.id)
                self.document_frequencies[token] += 1
            
            self.total_documents += 1
            
        except Exception as e:
            logger.error(f"Failed to update keyword index: {e}")

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for keyword search."""
        # Simple tokenization - split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        # Remove very short tokens
        tokens = [token for token in tokens if len(token) > 2]
        
        return tokens

    def _calculate_term_frequency(self, term: str, text: str) -> float:
        """Calculate term frequency in text."""
        tokens = self._tokenize(text.lower())
        if not tokens:
            return 0.0
        
        count = tokens.count(term)
        return count / len(tokens)

    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches filters."""
        for key, value in filters.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True

    # Delegate other methods to vector adapter
    async def get_embedding(self, embedding_id: UUID) -> Optional[VectorEmbedding]:
        return await self.vector_adapter.get_embedding(embedding_id)

    async def delete_embedding(self, embedding_id: UUID) -> bool:
        success = await self.vector_adapter.delete_embedding(embedding_id)
        if success and embedding_id in self.text_storage:
            # Remove from keyword index
            text = self.text_storage[embedding_id]
            tokens = self._tokenize(text.lower())
            for token in set(tokens):
                self.keyword_index[token].discard(embedding_id)
                if not self.keyword_index[token]:
                    del self.keyword_index[token]
                    self.document_frequencies[token] -= 1
            del self.text_storage[embedding_id]
            self.total_documents -= 1
        return success

    async def health_check(self) -> bool:
        return await self.vector_adapter.health_check()

    async def get_storage_info(self) -> Dict[str, Any]:
        base_info = await self.vector_adapter.get_storage_info()
        hybrid_info = {
            "adapter_type": "hybrid_search",
            "semantic_weight": self.semantic_weight,
            "keyword_weight": self.keyword_weight,
            "keyword_index_size": len(self.keyword_index),
            "total_documents": self.total_documents,
            "base_adapter": base_info
        }
        return hybrid_info

    # Implement remaining abstract methods by delegating
    async def find_embedding(self, embedding_id: UUID) -> Optional[VectorEmbedding]:
        return await self.vector_adapter.find_embedding(embedding_id)

    async def find_similar_by_text(self, query_text: str, embedding_type: str, top_k: int = 10, filters: Optional[Dict[str, Any]] = None, threshold: float = 0.7) -> List[SimilarityResult]:
        # Use hybrid search for text queries
        return await self.hybrid_search(query_text, None, top_k, filters, threshold)

    async def find_by_speaker(self, speaker_id: str, query_vector: List[float], top_k: int = 10, threshold: float = 0.7) -> List[SimilarityResult]:
        return await self.vector_adapter.find_by_speaker(speaker_id, query_vector, top_k, threshold)

    async def find_by_job(self, job_id: str, query_vector: List[float], top_k: int = 10, threshold: float = 0.7) -> List[SimilarityResult]:
        return await self.vector_adapter.find_by_job(job_id, query_vector, top_k, threshold)

    async def find_by_category(self, category: str, query_vector: List[float], top_k: int = 10, threshold: float = 0.7) -> List[SimilarityResult]:
        return await self.vector_adapter.find_by_category(category, query_vector, top_k, threshold)

    async def delete_embeddings_by_job(self, job_id: str) -> int:
        return await self.vector_adapter.delete_embeddings_by_job(job_id)

    async def get_embedding_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        return await self.vector_adapter.get_embedding_count(filters)

    async def get_statistics(self) -> Dict[str, Any]:
        return await self.get_storage_info()

    async def create_index(self, index_config: Dict[str, Any]) -> bool:
        return await self.vector_adapter.create_index(index_config)
