"""
LLM service using OpenAI GPT models
"""

from typing import AsyncGenerator, Dict, Any
import openai
import time

from core.config import settings
from core.logging import logger
from utils.exceptions import LLMError


class LLMService:
    """Service for LLM operations"""
    
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
            
            logger.info("LLM service initialized successfully")
            
        except Exception as e:
            logger.warning(f"OpenAI LLM service failed: {str(e)}")
            logger.info("Falling back to demo LLM service")
            
            # Use demo service as fallback
            from services.demo_service import DemoLLMService
            self.demo_service = DemoLLMService()
            await self.demo_service.initialize()
            self.use_demo = True
    
    async def _test_connection(self):
        """Test OpenAI API connection"""
        try:
            # Test with a simple completion
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
                temperature=0
            )
            
            if not response.choices:
                raise LLMError("No response from OpenAI API")
                
        except Exception as e:
            raise LLMError(f"OpenAI API connection test failed: {str(e)}")
    
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Generate streaming response from LLM
        
        Args:
            prompt: Input prompt for the LLM
            
        Yields:
            Response tokens
        """
        try:
            if not prompt.strip():
                raise LLMError("Cannot generate response for empty prompt")
            
            if self.use_demo:
                async for token in self.demo_service.generate_stream(prompt):
                    yield token
                return
            
            messages = [{"role": "user", "content": prompt.strip()}]
            
            stream = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Error in LLM streaming: {str(e)}")
            if not self.use_demo:
                logger.info("Falling back to demo LLM service")
                from services.demo_service import DemoLLMService
                self.demo_service = DemoLLMService()
                await self.demo_service.initialize()
                self.use_demo = True
                async for token in self.demo_service.generate_stream(prompt):
                    yield token
                return
            raise LLMError(f"Failed to generate streaming response: {str(e)}")
    
    async def generate_response(self, prompt: str) -> Dict[str, Any]:
        """
        Generate complete response from LLM
        
        Args:
            prompt: Input prompt for the LLM
            
        Returns:
            Response with content and metadata
        """
        try:
            if not prompt.strip():
                raise LLMError("Cannot generate response for empty prompt")
            
            messages = [{"role": "user", "content": prompt.strip()}]
            
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature
            )
            
            response_time = time.time() - start_time
            
            if not response.choices:
                raise LLMError("No response generated")
            
            content = response.choices[0].message.content
            
            return {
                "content": content,
                "model": settings.openai_model,
                "response_time": response_time,
                "total_tokens": response.usage.total_tokens if response.usage else None,
                "prompt_tokens": response.usage.prompt_tokens if response.usage else None,
                "completion_tokens": response.usage.completion_tokens if response.usage else None
            }
            
        except Exception as e:
            logger.error(f"Error in LLM generation: {str(e)}")
            raise LLMError(f"Failed to generate response: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for LLM service"""
        try:
            if not self.client:
                return {"status": "unhealthy", "error": "Not initialized"}
            
            # Test with a simple completion
            start_time = time.time()
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": "Say 'OK'"}],
                max_tokens=5,
                temperature=0
            )
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "model": settings.openai_model,
                "response_time": response_time,
                "test_response": response.choices[0].message.content if response.choices else None
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }