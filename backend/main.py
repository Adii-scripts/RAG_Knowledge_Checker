"""
RAG Knowledge Base Search Engine - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List, Optional
import asyncio
import json
from contextlib import asynccontextmanager

from core.config import settings
from core.logging import logger
from services.document_service import DocumentService
from services.rag_service import RAGService
from models.schemas import QueryRequest, QueryResponse, DocumentInfo
from utils.exceptions import DocumentProcessingError, QueryError


# Initialize services
document_service = DocumentService()
rag_service = RAGService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting RAG Knowledge Base Search Engine")
    
    # Initialize services
    await document_service.initialize()
    await rag_service.initialize()
    
    yield
    
    # Cleanup
    logger.info("Shutting down RAG Knowledge Base Search Engine")


# Create FastAPI app
app = FastAPI(
    title="RAG Knowledge Base Search Engine",
    description="Production-ready Knowledge-Base Search Engine with RAG capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "RAG Knowledge Base Search Engine",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.options("/api/upload")
async def upload_options():
    """Handle preflight requests for upload endpoint"""
    return {"message": "OK"}

@app.post("/api/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload and process multiple documents
    
    Args:
        files: List of uploaded files (PDF, TXT, DOCX)
        
    Returns:
        Success message with processed document count
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Validate file types and sizes
        for file in files:
            if not file.filename:
                raise HTTPException(status_code=400, detail="Invalid file")
            
            # Check file extension
            allowed_extensions = {'.pdf', '.txt', '.docx'}
            file_ext = '.' + file.filename.split('.')[-1].lower()
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
                )
        
        # Process documents
        processed_docs = await document_service.process_documents(files)
        
        logger.info(f"Successfully processed {len(processed_docs)} documents")
        
        return {
            "message": f"Successfully processed {len(processed_docs)} documents",
            "documents": processed_docs
        }
        
    except DocumentProcessingError as e:
        logger.error(f"Document processing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.options("/api/query")
async def query_options():
    """Handle preflight requests for query endpoint"""
    return {"message": "OK"}

@app.post("/api/query")
async def query_knowledge_base(request: QueryRequest):
    """
    Query the knowledge base using RAG
    
    Args:
        request: Query request with question and optional parameters
        
    Returns:
        Streaming response with answer and sources
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Check if we have any documents
        documents = await document_service.get_all_documents()
        if not documents:
            raise HTTPException(
                status_code=400, 
                detail="No documents available. Please upload documents first."
            )
        
        # Generate streaming response
        async def generate_response():
            try:
                async for chunk in rag_service.query_stream(
                    query=request.query,
                    top_k=request.top_k
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"
                
                # Send end signal
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                
            except Exception as e:
                logger.error(f"Error during streaming: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except QueryError as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/documents", response_model=List[DocumentInfo])
async def get_documents():
    """
    Get list of all uploaded documents
    
    Returns:
        List of document information
    """
    try:
        documents = await document_service.get_all_documents()
        return documents
        
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and its associated chunks
    
    Args:
        document_id: ID of the document to delete
        
    Returns:
        Success message
    """
    try:
        success = await document_service.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        logger.info(f"Successfully deleted document: {document_id}")
        
        return {"message": f"Document {document_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check document service
        doc_health = await document_service.health_check()
        
        # Check RAG service
        rag_health = await rag_service.health_check()
        
        return {
            "status": "healthy",
            "services": {
                "document_service": doc_health,
                "rag_service": rag_health
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )