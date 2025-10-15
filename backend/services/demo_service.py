"""
Demo services that work without OpenAI API for testing
"""

import asyncio
import random
from typing import List, Dict, Any, AsyncGenerator

from core.logging import logger
from models.schemas import SourceCitation


class DemoEmbeddingService:
    """Demo embedding service that generates random embeddings"""
    
    async def initialize(self):
        logger.info("Demo embedding service initialized")
    
    async def create_embedding(self, text: str) -> List[float]:
        """Generate a consistent embedding vector based on text content"""
        import hashlib
        import math
        import re
        
        # Normalize text more aggressively for better matching
        text = text.lower().strip()
        # Remove punctuation and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        words = text.split()
        
        # Create embedding based on word frequencies and positions
        embedding = [0.0] * 1536
        
        # Use word-based features to make similar texts have similar embeddings
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Generate embedding based on word content
        for word, count in word_counts.items():
            if len(word) < 2:  # Skip very short words
                continue
                
            word_hash = int(hashlib.md5(word.encode()).hexdigest(), 16)
            
            # Map word to multiple dimensions to increase similarity chances
            for i in range(5):  # Use 5 dimensions per word
                dim_idx = (word_hash + i) % 1536
                # Weight by word frequency and add some randomness
                weight = math.log(count + 1) * 0.1
                embedding[dim_idx] += weight * math.sin(word_hash + i)
        
        # Add some global text features
        text_length = len(words)
        if text_length > 0:
            # Add length-based features
            for i in range(0, 50, 5):  # Use first 50 dimensions for global features
                embedding[i] += math.sin(text_length + i) * 0.05
        
        # Normalize the embedding
        magnitude = math.sqrt(sum(x*x for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        else:
            # Fallback to small random embedding
            random.seed(42)
            embedding = [random.uniform(-0.01, 0.01) for _ in range(1536)]
        
        return embedding
    
    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "model": "demo-embedding",
            "response_time": 0.001
        }


class DemoLLMService:
    """Demo LLM service that generates sample responses"""
    
    async def initialize(self):
        logger.info("Demo LLM service initialized")
    
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate a streaming demo response"""
        
        # Sample responses based on prompt content
        if "challenge" in prompt.lower() or "problem" in prompt.lower():
            response = """Based on the provided documents, there are several key challenges in implementing RAG systems:

1. **Data Quality and Preprocessing**: Ensuring that the source documents are properly cleaned, structured, and chunked for optimal retrieval performance.

2. **Embedding Quality**: Selecting appropriate embedding models that can capture semantic meaning effectively for the specific domain.

3. **Retrieval Accuracy**: Balancing between retrieving enough relevant context while avoiding information overload that might confuse the language model.

4. **Latency Optimization**: Managing the trade-off between response quality and speed, especially when dealing with large document collections.

5. **Context Window Management**: Efficiently utilizing the limited context window of language models while providing sufficient relevant information.

These challenges require careful consideration of the specific use case and iterative optimization of the RAG pipeline components."""

        elif "method" in prompt.lower() or "approach" in prompt.lower():
            response = """The documents describe several methodological approaches for RAG implementation:

1. **Hybrid Retrieval**: Combining dense and sparse retrieval methods for improved accuracy.

2. **Multi-stage Ranking**: Using initial retrieval followed by re-ranking for better relevance.

3. **Adaptive Chunking**: Dynamically adjusting chunk sizes based on document structure and content type.

4. **Query Expansion**: Enhancing user queries with related terms to improve retrieval coverage.

5. **Feedback Loops**: Implementing mechanisms to learn from user interactions and improve system performance over time."""

        else:
            response = """Based on the uploaded documents, I can provide information about the topics covered. The documents contain relevant information that addresses your question. 

Key points from the analysis:
- The content covers important aspects of the subject matter
- Multiple perspectives and approaches are discussed
- Practical implementations and theoretical foundations are both addressed
- The information appears to be current and well-researched

For more specific insights, please feel free to ask more targeted questions about particular aspects you're interested in."""

        # Stream the response word by word
        words = response.split()
        for i, word in enumerate(words):
            if i > 0:
                yield " "
            yield word
            await asyncio.sleep(0.01)  # Simulate typing delay
    
    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "model": "demo-llm",
            "response_time": 0.1
        }


def create_demo_sources(query: str) -> List[SourceCitation]:
    """Create demo source citations"""
    sources = [
        SourceCitation(
            document_id="demo-doc-1",
            document_name="AI_Research_Paper.pdf",
            page_number=5,
            chunk_index=12,
            relevance_score=0.92,
            excerpt="This section discusses the fundamental challenges in retrieval-augmented generation systems, particularly focusing on the balance between retrieval accuracy and computational efficiency..."
        ),
        SourceCitation(
            document_id="demo-doc-2", 
            document_name="Machine_Learning_Guide.pdf",
            page_number=23,
            chunk_index=45,
            relevance_score=0.87,
            excerpt="The implementation of RAG systems requires careful consideration of embedding models, chunk size optimization, and retrieval strategies to ensure high-quality responses..."
        ),
        SourceCitation(
            document_id="demo-doc-3",
            document_name="Technical_Documentation.pdf", 
            page_number=8,
            chunk_index=19,
            relevance_score=0.83,
            excerpt="Modern approaches to information retrieval in large-scale systems emphasize the importance of semantic understanding and contextual relevance in document processing..."
        )
    ]
    
    return sources