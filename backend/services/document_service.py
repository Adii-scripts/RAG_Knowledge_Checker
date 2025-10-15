"""
Document processing and management service
"""

import os
import uuid
import aiofiles
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import UploadFile
import asyncio

from core.config import settings
from core.logging import logger
from models.schemas import DocumentInfo, DocumentType, ChunkInfo
from utils.document_processor import DocumentProcessor
from utils.exceptions import DocumentProcessingError
from services.vector_service import VectorService


class DocumentService:
    """Service for document processing and management"""
    
    def __init__(self):
        self.processor = DocumentProcessor()
        self.vector_service = VectorService()
        self.documents: Dict[str, DocumentInfo] = {}
        self.upload_dir = "uploads"
        
    async def initialize(self):
        """Initialize the document service"""
        try:
            # Create upload directory
            os.makedirs(self.upload_dir, exist_ok=True)
            
            # Initialize vector service
            await self.vector_service.initialize()
            
            # Load existing documents from vector store
            await self._load_existing_documents()
            
            logger.info("Document service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize document service: {str(e)}")
            raise
    
    async def _load_existing_documents(self):
        """Load existing documents from vector store metadata"""
        try:
            existing_docs = await self.vector_service.get_all_documents()
            for doc_info in existing_docs:
                self.documents[doc_info.id] = doc_info
            
            logger.info(f"Loaded {len(self.documents)} existing documents")
            
        except Exception as e:
            logger.warning(f"Could not load existing documents: {str(e)}")
    
    async def process_documents(self, files: List[UploadFile]) -> List[DocumentInfo]:
        """
        Process uploaded documents
        
        Args:
            files: List of uploaded files
            
        Returns:
            List of processed document information
        """
        processed_docs = []
        
        for file in files:
            try:
                doc_info = await self._process_single_document(file)
                processed_docs.append(doc_info)
                
            except Exception as e:
                logger.error(f"Failed to process {file.filename}: {str(e)}")
                # Continue processing other files
                continue
        
        if not processed_docs:
            raise DocumentProcessingError("No documents were successfully processed")
        
        return processed_docs
    
    async def _process_single_document(self, file: UploadFile) -> DocumentInfo:
        """Process a single document"""
        try:
            # Validate file
            await self._validate_file(file)
            
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Save file temporarily
            file_path = await self._save_uploaded_file(file, doc_id)
            
            try:
                # Extract text content
                content = await self.processor.extract_text(file_path, file.filename)
                
                # Create chunks
                chunks = await self.processor.create_chunks(
                    content=content,
                    document_id=doc_id,
                    filename=file.filename
                )
                
                # Store in vector database
                await self.vector_service.add_chunks(chunks)
                
                # Create document info
                doc_info = DocumentInfo(
                    id=doc_id,
                    filename=file.filename,
                    file_type=self._get_file_type(file.filename),
                    file_size=file.size or 0,
                    upload_date=datetime.now(),
                    chunk_count=len(chunks),
                    status="processed"
                )
                
                # Store in memory
                self.documents[doc_id] = doc_info
                
                logger.info(f"Successfully processed document: {file.filename} ({len(chunks)} chunks)")
                
                return doc_info
                
            finally:
                # Clean up temporary file
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
        except Exception as e:
            logger.error(f"Error processing document {file.filename}: {str(e)}")
            raise DocumentProcessingError(f"Failed to process {file.filename}: {str(e)}")
    
    async def _validate_file(self, file: UploadFile):
        """Validate uploaded file"""
        if not file.filename:
            raise DocumentProcessingError("Invalid filename")
        
        # Check file size
        if file.size and file.size > settings.max_file_size:
            raise DocumentProcessingError(
                f"File too large: {file.size} bytes. Maximum allowed: {settings.max_file_size} bytes"
            )
        
        # Check file extension
        file_type = self._get_file_type(file.filename)
        if file_type not in [DocumentType.PDF, DocumentType.TXT, DocumentType.DOCX]:
            raise DocumentProcessingError(f"Unsupported file type: {file.filename}")
    
    def _get_file_type(self, filename: str) -> DocumentType:
        """Get file type from filename"""
        ext = filename.lower().split('.')[-1]
        if ext == 'pdf':
            return DocumentType.PDF
        elif ext == 'txt':
            return DocumentType.TXT
        elif ext == 'docx':
            return DocumentType.DOCX
        else:
            raise DocumentProcessingError(f"Unsupported file extension: {ext}")
    
    async def _save_uploaded_file(self, file: UploadFile, doc_id: str) -> str:
        """Save uploaded file temporarily"""
        file_extension = file.filename.split('.')[-1]
        file_path = os.path.join(self.upload_dir, f"{doc_id}.{file_extension}")
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Reset file position for potential re-reading
        await file.seek(0)
        
        return file_path
    
    async def get_all_documents(self) -> List[DocumentInfo]:
        """Get all processed documents"""
        return list(self.documents.values())
    
    async def get_document(self, document_id: str) -> Optional[DocumentInfo]:
        """Get specific document by ID"""
        return self.documents.get(document_id)
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and its chunks
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        try:
            if document_id not in self.documents:
                return False
            
            # Delete from vector store
            await self.vector_service.delete_document(document_id)
            
            # Remove from memory
            del self.documents[document_id]
            
            logger.info(f"Successfully deleted document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for document service"""
        try:
            vector_health = await self.vector_service.health_check()
            
            return {
                "status": "healthy",
                "documents_count": len(self.documents),
                "vector_service": vector_health,
                "upload_dir_exists": os.path.exists(self.upload_dir)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }