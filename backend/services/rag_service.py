"""
RAG (Retrieval-Augmented Generation) service
"""

import time
import asyncio
from typing import List, Dict, Any, AsyncGenerator
import json

from core.config import settings
from core.logging import logger
from models.schemas import SourceCitation, StreamChunk
from services.vector_service import VectorService
from services.llm_service import LLMService
from utils.exceptions import QueryError


class RAGService:
    """Service for Retrieval-Augmented Generation"""
    
    def __init__(self):
        self.vector_service = VectorService()
        self.llm_service = LLMService()
        
    async def initialize(self):
        """Initialize the RAG service"""
        try:
            await self.vector_service.initialize()
            await self.llm_service.initialize()
            
            logger.info("RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {str(e)}")
            raise
    
    async def query_stream(
        self, 
        query: str, 
        top_k: int = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream RAG query response
        
        Args:
            query: User query
            top_k: Number of top results to retrieve
            
        Yields:
            Stream chunks with answer tokens and sources
        """
        start_time = time.time()
        
        try:
            if top_k is None:
                top_k = settings.top_k_results
            
            logger.info(f"Processing RAG query: {query[:100]}...")
            
            # Step 1: Retrieve relevant chunks
            yield {
                "type": "status",
                "message": "Searching knowledge base..."
            }
            
            relevant_chunks = await self.vector_service.similarity_search(
                query=query,
                top_k=top_k
            )
            
            # If using demo services and no chunks found, create demo response anyway
            if not relevant_chunks:
                if hasattr(self.llm_service, 'use_demo') and self.llm_service.use_demo:
                    logger.info("No chunks found, but using demo mode - generating demo response")
                    # Generate demo response without context
                    yield {
                        "type": "status",
                        "message": "Generating response..."
                    }
                    
                    async for token in self.llm_service.generate_stream(f"Answer this question based on general knowledge: {query}"):
                        yield {
                            "type": "token",
                            "content": token
                        }
                    
                    # Send demo sources
                    from services.demo_service import create_demo_sources
                    sources = create_demo_sources(query)
                    response_time = time.time() - start_time
                    
                    yield {
                        "type": "sources",
                        "sources": [source.dict() for source in sources],
                        "response_time": response_time,
                        "model_used": "demo-llm"
                    }
                    return
                else:
                    yield {
                        "type": "error",
                        "message": "No relevant information found in the knowledge base."
                    }
                    return
            
            # Step 2: Prepare context and sources
            context = self._prepare_context(relevant_chunks)
            sources = self._prepare_sources(relevant_chunks)
            
            yield {
                "type": "status",
                "message": "Generating response..."
            }
            
            # Step 3: Generate streaming response
            prompt = self._create_rag_prompt(query, context)
            
            async for token in self.llm_service.generate_stream(prompt):
                yield {
                    "type": "token",
                    "content": token
                }
            
            # Step 4: Send sources
            response_time = time.time() - start_time
            
            # If no sources found, create demo sources
            if not sources and hasattr(self.llm_service, 'use_demo') and self.llm_service.use_demo:
                from services.demo_service import create_demo_sources
                sources = create_demo_sources(query)
            
            yield {
                "type": "sources",
                "sources": [source.dict() for source in sources],
                "response_time": response_time,
                "model_used": getattr(self.llm_service, 'use_demo', False) and "demo-llm" or settings.openai_model
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}")
            yield {
                "type": "error",
                "message": f"An error occurred while processing your query: {str(e)}"
            }
    
    def _prepare_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Prepare context from retrieved chunks"""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get('metadata', {})
            document_name = metadata.get('filename', 'Unknown Document')
            page_num = metadata.get('page_number', 'N/A')
            
            context_part = f"[Source {i}: {document_name}, Page {page_num}]\n{chunk['content']}\n"
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _prepare_sources(self, chunks: List[Dict[str, Any]]) -> List[SourceCitation]:
        """Prepare source citations from retrieved chunks"""
        sources = []
        
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            
            source = SourceCitation(
                document_id=metadata.get('document_id', ''),
                document_name=metadata.get('filename', 'Unknown Document'),
                page_number=metadata.get('page_number'),
                chunk_index=metadata.get('chunk_index', 0),
                relevance_score=chunk.get('score', 0.0),
                excerpt=chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content']
            )
            sources.append(source)
        
        return sources
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Create RAG prompt for the LLM"""
        prompt = f"""You are a helpful AI assistant that answers questions based on the provided context. 

Instructions:
1. Use ONLY the information provided in the context below to answer the question
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Be concise but comprehensive in your response
4. Cite specific sources when making claims
5. If you're uncertain about any information, express that uncertainty

Context:
{context}

Question: {query}

Answer:"""
        
        return prompt
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for RAG service"""
        try:
            vector_health = await self.vector_service.health_check()
            llm_health = await self.llm_service.health_check()
            
            return {
                "status": "healthy",
                "vector_service": vector_health,
                "llm_service": llm_health
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }