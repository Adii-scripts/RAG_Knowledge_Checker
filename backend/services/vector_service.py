"""
Vector database service with automatic fallback
"""

import os
from typing import List, Dict, Any, Optional

from core.config import settings
from core.logging import logger
from models.schemas import DocumentInfo, ChunkInfo
from utils.exceptions import VectorStoreError

# Try to import ChromaDB, fallback to simple service if not available
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
    logger.info("ChromaDB is available")
except ImportError:
    logger.warning("ChromaDB not available, will use simple vector service")
    CHROMADB_AVAILABLE = False

# Try to import numpy for simple service
try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    NUMPY_AVAILABLE = True
except ImportError:
    logger.warning("NumPy/scikit-learn not available, simple vector service will be limited")
    NUMPY_AVAILABLE = False


class VectorService:
    """Unified vector service with automatic fallback"""
    
    def __init__(self):
        self.use_chromadb = CHROMADB_AVAILABLE
        self.client = None
        self.collection = None
        
        # Simple service fallback
        self.chunks = {}
        self.embeddings = {}
        self.storage_file = "simple_vector_store.json"
        
        # Import embedding service
        from services.embedding_service import EmbeddingService
        self.embedding_service = EmbeddingService()
        
    async def initialize(self):
        """Initialize vector service"""
        try:
            await self.embedding_service.initialize()
            
            if self.use_chromadb:
                await self._init_chromadb()
                logger.info("Using ChromaDB vector service")
            else:
                await self._init_simple()
                logger.info("Using simple vector service")
                
        except Exception as e:
            logger.error(f"Vector service initialization failed: {str(e)}")
            if self.use_chromadb:
                logger.info("Falling back to simple vector service")
                self.use_chromadb = False
                await self._init_simple()
            else:
                raise VectorStoreError(f"All vector services failed: {str(e)}")
    
    async def _init_chromadb(self):
        """Initialize ChromaDB"""
        os.makedirs(settings.chroma_persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"description": "RAG Knowledge Base Collection"}
        )
    
    async def _init_simple(self):
        """Initialize simple vector service"""
        import json
        
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.chunks = data.get('chunks', {})
                    self.embeddings = data.get('embeddings', {})
                logger.info(f"Loaded {len(self.chunks)} chunks from simple storage")
        except Exception as e:
            logger.warning(f"Could not load simple storage: {str(e)}")
    
    def _save_simple(self):
        """Save simple vector data"""
        import json
        
        try:
            data = {
                'chunks': self.chunks,
                'embeddings': self.embeddings
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Could not save simple storage: {str(e)}")
    
    async def add_chunks(self, chunks: List[ChunkInfo]):
        """Add chunks to vector store"""
        try:
            if not chunks:
                return
            
            if self.use_chromadb:
                await self._add_chunks_chromadb(chunks)
            else:
                await self._add_chunks_simple(chunks)
                
        except Exception as e:
            logger.error(f"Error adding chunks: {str(e)}")
            raise VectorStoreError(f"Failed to add chunks: {str(e)}")
    
    async def _add_chunks_chromadb(self, chunks: List[ChunkInfo]):
        """Add chunks to ChromaDB"""
        ids = []
        documents = []
        metadatas = []
        embeddings = []
        
        for chunk in chunks:
            embedding = await self.embedding_service.create_embedding(chunk.content)
            
            ids.append(chunk.chunk_id)
            documents.append(chunk.content)
            # Prepare metadata, ensuring no None values
            metadata = {
                "document_id": chunk.document_id,
                "filename": chunk.metadata.get("filename", ""),
                "page_number": chunk.page_number if chunk.page_number is not None else 0,
                "chunk_index": chunk.chunk_index,
            }
            
            # Add other metadata, filtering out None values
            for key, value in chunk.metadata.items():
                if value is not None:
                    metadata[key] = value
            
            metadatas.append(metadata)
            embeddings.append(embedding)
        
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        logger.info(f"Added {len(chunks)} chunks to ChromaDB")
    
    async def _add_chunks_simple(self, chunks: List[ChunkInfo]):
        """Add chunks to simple storage"""
        for chunk in chunks:
            embedding = await self.embedding_service.create_embedding(chunk.content)
            
            # Prepare metadata, ensuring no None values
            metadata = {
                'document_id': chunk.document_id,
                'filename': chunk.metadata.get('filename', ''),
                'page_number': chunk.page_number if chunk.page_number is not None else 0,
                'chunk_index': chunk.chunk_index,
            }
            
            # Add other metadata, filtering out None values
            for key, value in chunk.metadata.items():
                if value is not None:
                    metadata[key] = value
            
            self.chunks[chunk.chunk_id] = {
                'content': chunk.content,
                'metadata': metadata
            }
            
            self.embeddings[chunk.chunk_id] = embedding
        
        self._save_simple()
        logger.info(f"Added {len(chunks)} chunks to simple storage")
    
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
            
            if self.use_chromadb:
                return await self._search_chromadb(query, top_k, filter_metadata)
            else:
                return await self._search_simple(query, top_k, filter_metadata)
                
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            raise VectorStoreError(f"Similarity search failed: {str(e)}")
    
    async def _search_chromadb(self, query: str, top_k: int, filter_metadata):
        """Search using ChromaDB"""
        query_embedding = await self.embedding_service.create_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"]
        )
        
        formatted_results = []
        
        if results['documents'] and results['documents'][0]:
            # Use lower threshold for demo embeddings
            threshold = 0.1 if hasattr(self.embedding_service, 'use_demo') and self.embedding_service.use_demo else settings.similarity_threshold
            logger.info(f"Using similarity threshold: {threshold}, found {len(results['documents'][0])} results")
            
            for doc, metadata, distance in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ):
                similarity_score = 1 - distance
                logger.info(f"Chunk similarity: {similarity_score:.3f} (threshold: {threshold})")
                
                if similarity_score >= threshold:
                    formatted_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "score": similarity_score
                    })
        
        logger.info(f"Returning {len(formatted_results)} results after filtering")
        return formatted_results
    
    async def _search_simple(self, query: str, top_k: int, filter_metadata):
        """Search using simple storage"""
        if not self.chunks or not NUMPY_AVAILABLE:
            return []
        
        query_embedding = await self.embedding_service.create_embedding(query)
        similarities = []
        
        for chunk_id, chunk_data in self.chunks.items():
            if filter_metadata:
                metadata = chunk_data['metadata']
                if not all(metadata.get(k) == v for k, v in filter_metadata.items()):
                    continue
            
            chunk_embedding = self.embeddings[chunk_id]
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                [query_embedding], 
                [chunk_embedding]
            )[0][0]
            
            # Use lower threshold for demo embeddings
            threshold = 0.1 if hasattr(self.embedding_service, 'use_demo') and self.embedding_service.use_demo else settings.similarity_threshold
            if similarity >= threshold:
                similarities.append({
                    'content': chunk_data['content'],
                    'metadata': chunk_data['metadata'],
                    'score': float(similarity)
                })
        
        # Sort and return top_k
        similarities.sort(key=lambda x: x['score'], reverse=True)
        return similarities[:top_k]
    
    async def delete_document(self, document_id: str):
        """Delete document chunks"""
        try:
            if self.use_chromadb:
                await self._delete_chromadb(document_id)
            else:
                await self._delete_simple(document_id)
                
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise VectorStoreError(f"Failed to delete document: {str(e)}")
    
    async def _delete_chromadb(self, document_id: str):
        """Delete from ChromaDB"""
        results = self.collection.get(
            where={"document_id": document_id},
            include=["metadatas"]
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            logger.info(f"Deleted {len(results['ids'])} chunks from ChromaDB")
    
    async def _delete_simple(self, document_id: str):
        """Delete from simple storage"""
        chunks_to_delete = []
        
        for chunk_id, chunk_data in self.chunks.items():
            if chunk_data['metadata'].get('document_id') == document_id:
                chunks_to_delete.append(chunk_id)
        
        for chunk_id in chunks_to_delete:
            del self.chunks[chunk_id]
            del self.embeddings[chunk_id]
        
        self._save_simple()
        logger.info(f"Deleted {len(chunks_to_delete)} chunks from simple storage")
    
    async def get_all_documents(self) -> List[DocumentInfo]:
        """Get all documents"""
        try:
            if self.use_chromadb:
                return await self._get_docs_chromadb()
            else:
                return await self._get_docs_simple()
        except Exception as e:
            logger.error(f"Error getting documents: {str(e)}")
            return []
    
    async def _get_docs_chromadb(self) -> List[DocumentInfo]:
        """Get documents from ChromaDB"""
        results = self.collection.get(include=["metadatas"])
        documents_dict = {}
        
        for metadata in results['metadatas']:
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
        
        # Count chunks
        for metadata in results['metadatas']:
            doc_id = metadata.get('document_id')
            if doc_id in documents_dict:
                documents_dict[doc_id].chunk_count += 1
        
        return list(documents_dict.values())
    
    async def _get_docs_simple(self) -> List[DocumentInfo]:
        """Get documents from simple storage"""
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
        
        # Count chunks
        for chunk_data in self.chunks.values():
            doc_id = chunk_data['metadata'].get('document_id')
            if doc_id in documents_dict:
                documents_dict[doc_id].chunk_count += 1
        
        return list(documents_dict.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check"""
        try:
            if self.use_chromadb:
                count = self.collection.count()
                return {
                    "status": "healthy",
                    "service_type": "chromadb",
                    "total_chunks": count,
                    "collection_name": settings.collection_name
                }
            else:
                return {
                    "status": "healthy",
                    "service_type": "simple",
                    "total_chunks": len(self.chunks),
                    "storage_file": self.storage_file
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }