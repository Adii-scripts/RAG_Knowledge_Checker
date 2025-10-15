"""
Custom exceptions for the RAG Knowledge Base
"""


class RAGException(Exception):
    """Base exception for RAG system"""
    pass


class DocumentProcessingError(RAGException):
    """Exception raised during document processing"""
    pass


class VectorStoreError(RAGException):
    """Exception raised during vector store operations"""
    pass


class EmbeddingError(RAGException):
    """Exception raised during embedding generation"""
    pass


class LLMError(RAGException):
    """Exception raised during LLM operations"""
    pass


class QueryError(RAGException):
    """Exception raised during query processing"""
    pass


class ConfigurationError(RAGException):
    """Exception raised for configuration issues"""
    pass