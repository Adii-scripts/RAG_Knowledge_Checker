"""
Simple in-memory vector service as fallback when ChromaDB is not available
"""

import json
import os
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from core.config import settings
from core.logging import logger
from models.schemas import DocumentInfo, ChunkInfo
from services.embedding_service import EmbeddingService
from utils.exceptions import VectorStoreError


class SimpleVectorService:
    """Simple in-memory vector service as ChromaDB fallback"""
    
    def __init__(self):
        self.chunks: Dict[str, Dict[str, Any]] = {}
        self.embeddings: Dict[str, List[float]] = {}
        self.embedding_service = EmbeddingService()
        self.storage_file = "simple_vector_store.json"
        
    async def initialize(self):
        """Initialize the simple vector service"""
        try:
            await self.embedding_service.initialize()
            self._load_from_disk()
            logger.info("Simple vector service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize simple vector service: {str(e)}")
            raise VectorStoreError(f"Simple vector service initialization failed: {str(e)}")
    
    def _load_from_disk(self):
        """Load stored vectors from disk"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.chunks = data.get('chunks', {})
                    self.embeddings = data.get('embeddings', {})
                logger.info(f"Loaded {len(self.chunks)} chunks from disk")
        except Exception as e:
            logger.warning(f"Could not load from disk: {str(e)}")
    
    def _save_to_disk(self):
        """Save vectors to disk"""
        try:
            data = {
                'chunks': self.chunks,
                'embeddings': self.embeddings
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Could not save to disk: {str(e)}")
    
    async def add_chunks(self, chunks: List[ChunkInfo]):
        """Add document chunks to vector store"""
        try:
            for chunk in chunks:
                # Generate embedding
                embedding = await self.embedding_service.create_embedding(chunk.content)
                
                # Store chunk data
                self.chunks[chunk.chunk_id] = {
                    'content': chunk.content,
                    'metadata': {
                        'document_id': chunk.document_id,
                        'filename': chunk.metadata.get('filename', ''),
                        'page_number': chunk.page_number,
                        'chunk_index': chunk.chunk_index,
                        **chunk.metadata
                    }
                }
                
                # Store embedding
                self.embeddings[chunk.chunk_id] = embedding
            
            # Save to disk
            self._save_to_disk()
            
            logger.info(f"Added {len(chunks)} chunks to simple vector store")
            
        except Exception as e:
            logger.error(f"Error adding chunks: {str(e)}")
            raise VectorStoreError(f"Failed to add chunks: {str(e)}")
    
    async def similarity_search(
        self, 
        query: str, 
        top_k: int = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform similarity search"""
        try:
            if top_k is None:
                top_k = settings.top_k_results
            
            if not self.chunks:
                return []
            
            # Generate query embedding
            query_embedding = await self.embedding_service.create_embedding(query)
            
            # Calculate similarities
            similarities = []
            
            for chunk_id, chunk_data in self.chunks.items():
                if filter_metadata:
                    # Apply metadata filters
                    metadata = chunk_data['metadata']
                    if not all(metadata.get(k) == v for k, v in filter_metadata.items()):
                        continue
                
                chunk_embedding = self.embeddings[chunk_id]
                
                # Calculate cosine similarity
                similarity = cosine_similarity(
                    [query_embedding], 
                    [chunk_embedding]
                )[0][0]
                
                if similarity >= settings.similarity_threshold:
                    similarities.append({
                        'chunk_id': chunk_id,
                        'content': chunk_data['content'],
                        'metadata': chunk_data['metadata'],
                        'score': float(similarity)
                    })
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x['score'], reverse=True)
            results = similarities[:top_k]
            
            logger.info(f"Found {len(results)} relevant chunks for query")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            raise VectorStoreError(f"Similarity search failed: {str(e)}")
    
    async def delete_document(self, document_id: str):
        """Delete all chunks for a document"""
        try:
            chunks_to_delete = []
            
            for chunk_id, chunk_data in self.chunks.items():
                if chunk_data['metadata'].get('document_id') == document_id:
                    chunks_to_delete.append(chunk_id)
            
            for chunk_id in chunks_to_delete:
                del self.chunks[chunk_id]
                del self.embeddings[chunk_id]
            
            self._save_to_disk()
            
            logger.info(f"Deleted {len(chunks_to_delete)} chunks for document {document_id}")
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            raise VectorStoreError(f"Failed to delete document: {str(e)}")
    
    async def get_all_documents(self) -> List[DocumentInfo]:
        """Get information about all documents"""
        try:
            documents_dict = {}
            
            for chunk_data in self.chunks.values():
                metadata = chunk_data['metadata']
                doc_id = metadata.get('document_id')
                
                if doc_id and doc_id not in documents_dict:
                    documents_dict[doc_id] = DocumentInfo(
                        id=doc_id,
                        filename=metadata.get('filename', 'Unknown'),
                        file_type=metadata.get('file_type', 'unknown'),
                        file_size=metadata.get('file_size', 0),
                        upload_date=metadata.get('upload_date', ''),
                        chunk_count=0,
                        status="processed"
                    )
            
            # Count chunks for each document
            for chunk_data in self.chunks.values():
                doc_id = chunk_data['metadata'].get('document_id')
                if doc_id in documents_dict:
                    documents_dict[doc_id].chunk_count += 1
            
            return list(documents_dict.values())
            
        except Exception as e:
            logger.error(f"Error getting all documents: {str(e)}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for simple vector service"""
        try:
            return {
                "status": "healthy",
                "service_type": "simple_vector_service",
                "total_chunks": len(self.chunks),
                "storage_file": self.storage_file
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }