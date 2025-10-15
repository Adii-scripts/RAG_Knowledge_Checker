"""
Embedding service using OpenAI embeddings
"""

from typing import List
import openai
import asyncio
import time

from core.config import settings
from core.logging import logger
from utils.exceptions import EmbeddingError


class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self):
        self.client = None
        self.demo_service = None
        self.use_demo = False
        
    async def initialize(self):
        """Initialize OpenAI client"""
        try:
            self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            
            # Test the connection
            await self._test_connection()
            
            logger.info("Embedding service initialized successfully")
            
        except Exception as e:
            logger.warning(f"OpenAI embedding service failed: {str(e)}")
            logger.info("Falling back to demo embedding service")
            
            # Use demo service as fallback
            from services.demo_service import DemoEmbeddingService
            self.demo_service = DemoEmbeddingService()
            await self.demo_service.initialize()
            self.use_demo = True
    
    async def _test_connection(self):
        """Test OpenAI API connection"""
        try:
            # Test with a simple embedding with timeout
            await asyncio.wait_for(
                self.client.embeddings.create(
                    model=settings.embedding_model,
                    input="test"
                ),
                timeout=10.0  # 10 second timeout
            )
            
        except asyncio.TimeoutError:
            raise EmbeddingError("OpenAI API connection timeout")
        except Exception as e:
            raise EmbeddingError(f"OpenAI API connection test failed: {str(e)}")
    
    async def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            if not text.strip():
                raise EmbeddingError("Cannot create embedding for empty text")
            
            if self.use_demo:
                return await self.demo_service.create_embedding(text)
            
            response = await asyncio.wait_for(
                self.client.embeddings.create(
                    model=settings.embedding_model,
                    input=text.strip()
                ),
                timeout=30.0  # 30 second timeout
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            if not self.use_demo:
                logger.info("Falling back to demo embedding service")
                from services.demo_service import DemoEmbeddingService
                self.demo_service = DemoEmbeddingService()
                await self.demo_service.initialize()
                self.use_demo = True
                return await self.demo_service.create_embedding(text)
            raise EmbeddingError(f"Failed to create embedding: {str(e)}")
    
    async def create_embeddings_batch(
        self, 
        texts: List[str], 
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Create embeddings for multiple texts in batches
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embedding vectors
        """
        try:
            if not texts:
                return []
            
            # Filter out empty texts
            valid_texts = [text.strip() for text in texts if text.strip()]
            
            if not valid_texts:
                raise EmbeddingError("No valid texts to embed")
            
            embeddings = []
            
            # Process in batches
            for i in range(0, len(valid_texts), batch_size):
                batch = valid_texts[i:i + batch_size]
                
                try:
                    response = await self.client.embeddings.create(
                        model=settings.embedding_model,
                        input=batch
                    )
                    
                    batch_embeddings = [item.embedding for item in response.data]
                    embeddings.extend(batch_embeddings)
                    
                    # Add small delay to respect rate limits
                    if i + batch_size < len(valid_texts):
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    logger.error(f"Error in batch {i//batch_size + 1}: {str(e)}")
                    # For failed batches, try individual embeddings
                    for text in batch:
                        try:
                            embedding = await self.create_embedding(text)
                            embeddings.append(embedding)
                        except:
                            # Skip failed individual embeddings
                            logger.warning(f"Skipping failed embedding for text: {text[:50]}...")
                            continue
            
            logger.info(f"Created {len(embeddings)} embeddings from {len(valid_texts)} texts")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error creating batch embeddings: {str(e)}")
            raise EmbeddingError(f"Failed to create batch embeddings: {str(e)}")
    
    async def health_check(self) -> dict:
        """Health check for embedding service"""
        try:
            if not self.client:
                return {"status": "unhealthy", "error": "Not initialized"}
            
            # Test with a simple embedding
            start_time = time.time()
            await self.create_embedding("health check test")
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "model": settings.embedding_model,
                "response_time": response_time
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }