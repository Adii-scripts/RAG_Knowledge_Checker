"""
Pydantic models for request/response schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types"""
    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"


class DocumentInfo(BaseModel):
    """Document information model"""
    id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    file_type: DocumentType = Field(..., description="Document type")
    file_size: int = Field(..., description="File size in bytes")
    upload_date: datetime = Field(..., description="Upload timestamp")
    chunk_count: int = Field(..., description="Number of chunks created")
    status: str = Field(default="processed", description="Processing status")


class ChunkInfo(BaseModel):
    """Document chunk information"""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Parent document ID")
    content: str = Field(..., description="Chunk content")
    page_number: Optional[int] = Field(None, description="Page number if applicable")
    chunk_index: int = Field(..., description="Chunk index within document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class QueryRequest(BaseModel):
    """Query request model"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of top results to retrieve")
    include_sources: bool = Field(default=True, description="Include source citations")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()


class SourceCitation(BaseModel):
    """Source citation model"""
    document_id: str = Field(..., description="Source document ID")
    document_name: str = Field(..., description="Source document name")
    page_number: Optional[int] = Field(None, description="Page number")
    chunk_index: int = Field(..., description="Chunk index")
    relevance_score: float = Field(..., description="Similarity score")
    excerpt: str = Field(..., description="Relevant text excerpt")


class QueryResponse(BaseModel):
    """Query response model"""
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceCitation] = Field(default_factory=list, description="Source citations")
    response_time: float = Field(..., description="Response time in seconds")
    model_used: str = Field(..., description="LLM model used")
    total_tokens: Optional[int] = Field(None, description="Total tokens used")


class StreamChunk(BaseModel):
    """Streaming response chunk"""
    type: str = Field(..., description="Chunk type: 'token', 'sources', 'end', 'error'")
    content: Optional[str] = Field(None, description="Content for token chunks")
    sources: Optional[List[SourceCitation]] = Field(None, description="Sources for final response")
    message: Optional[str] = Field(None, description="Error message if type is 'error'")


class HealthStatus(BaseModel):
    """Health check status"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")