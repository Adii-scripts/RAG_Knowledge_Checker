"""
Document processing utilities
"""

import os
import uuid
from typing import List, Dict, Any
import PyPDF2
import docx
import tiktoken
from io import BytesIO

from core.config import settings
from core.logging import logger
from models.schemas import ChunkInfo
from utils.exceptions import DocumentProcessingError


class DocumentProcessor:
    """Utility class for document processing"""
    
    def __init__(self):
        # Initialize tokenizer for chunk size calculation
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        except:
            # Fallback to cl100k_base encoding
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    async def extract_text(self, file_path: str, filename: str) -> str:
        """
        Extract text from various document formats
        
        Args:
            file_path: Path to the document file
            filename: Original filename for type detection
            
        Returns:
            Extracted text content
        """
        try:
            file_ext = filename.lower().split('.')[-1]
            
            if file_ext == 'pdf':
                return await self._extract_pdf_text(file_path)
            elif file_ext == 'txt':
                return await self._extract_txt_text(file_path)
            elif file_ext == 'docx':
                return await self._extract_docx_text(file_path)
            else:
                raise DocumentProcessingError(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {str(e)}")
            raise DocumentProcessingError(f"Failed to extract text: {str(e)}")
    
    async def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text_content = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            # Add page marker for citation purposes
                            text_content.append(f"[PAGE {page_num + 1}]\n{page_text}")
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                        continue
            
            if not text_content:
                raise DocumentProcessingError("No text could be extracted from PDF")
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            raise DocumentProcessingError(f"PDF extraction failed: {str(e)}")
    
    async def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if not content.strip():
                raise DocumentProcessingError("Text file is empty")
            
            return content
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    content = file.read()
                return content
            except Exception as e:
                raise DocumentProcessingError(f"Could not decode text file: {str(e)}")
        except Exception as e:
            raise DocumentProcessingError(f"TXT extraction failed: {str(e)}")
    
    async def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text_content = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            if not text_content:
                raise DocumentProcessingError("No text could be extracted from DOCX")
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            raise DocumentProcessingError(f"DOCX extraction failed: {str(e)}")
    
    async def create_chunks(
        self, 
        content: str, 
        document_id: str, 
        filename: str
    ) -> List[ChunkInfo]:
        """
        Create chunks from document content
        
        Args:
            content: Document text content
            document_id: Unique document identifier
            filename: Original filename
            
        Returns:
            List of document chunks
        """
        try:
            if not content.strip():
                raise DocumentProcessingError("Cannot create chunks from empty content")
            
            # Split content into chunks
            chunks = self._split_text_into_chunks(content)
            
            # Create ChunkInfo objects
            chunk_infos = []
            
            for i, chunk_text in enumerate(chunks):
                # Extract page number if available
                page_number = self._extract_page_number(chunk_text)
                
                # Clean chunk text (remove page markers)
                clean_text = self._clean_chunk_text(chunk_text)
                
                chunk_info = ChunkInfo(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document_id,
                    content=clean_text,
                    page_number=page_number,
                    chunk_index=i,
                    metadata={
                        "filename": filename,
                        "chunk_size": len(self.tokenizer.encode(clean_text)),
                        "original_length": len(chunk_text)
                    }
                )
                
                chunk_infos.append(chunk_info)
            
            logger.info(f"Created {len(chunk_infos)} chunks from {filename}")
            
            return chunk_infos
            
        except Exception as e:
            logger.error(f"Error creating chunks: {str(e)}")
            raise DocumentProcessingError(f"Failed to create chunks: {str(e)}")
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks based on token count"""
        try:
            # Tokenize the entire text
            tokens = self.tokenizer.encode(text)
            
            if len(tokens) <= settings.chunk_size:
                return [text]
            
            chunks = []
            start_idx = 0
            
            while start_idx < len(tokens):
                # Calculate end index for this chunk
                end_idx = min(start_idx + settings.chunk_size, len(tokens))
                
                # Extract chunk tokens
                chunk_tokens = tokens[start_idx:end_idx]
                
                # Decode back to text
                chunk_text = self.tokenizer.decode(chunk_tokens)
                
                chunks.append(chunk_text)
                
                # Move start index with overlap
                start_idx = end_idx - settings.chunk_overlap
                
                # Prevent infinite loop
                if start_idx >= end_idx:
                    break
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting text into chunks: {str(e)}")
            # Fallback to simple character-based splitting
            return self._fallback_text_splitting(text)
    
    def _fallback_text_splitting(self, text: str) -> List[str]:
        """Fallback text splitting method"""
        # Approximate tokens as 4 characters per token
        approx_chunk_size = settings.chunk_size * 4
        approx_overlap = settings.chunk_overlap * 4
        
        chunks = []
        start_idx = 0
        
        while start_idx < len(text):
            end_idx = min(start_idx + approx_chunk_size, len(text))
            
            # Try to break at sentence or paragraph boundaries
            chunk_text = text[start_idx:end_idx]
            
            # Look for good break points
            if end_idx < len(text):
                for break_char in ['\n\n', '\n', '. ', '! ', '? ']:
                    last_break = chunk_text.rfind(break_char)
                    if last_break > len(chunk_text) * 0.7:  # At least 70% of chunk
                        chunk_text = chunk_text[:last_break + len(break_char)]
                        break
            
            chunks.append(chunk_text)
            
            # Move start index with overlap
            start_idx = start_idx + len(chunk_text) - approx_overlap
            
            if start_idx >= end_idx:
                break
        
        return chunks
    
    def _extract_page_number(self, chunk_text: str) -> int:
        """Extract page number from chunk text if available"""
        try:
            # Look for page markers like [PAGE 1]
            import re
            page_match = re.search(r'\[PAGE (\d+)\]', chunk_text)
            if page_match:
                return int(page_match.group(1))
            return None
        except:
            return None
    
    def _clean_chunk_text(self, chunk_text: str) -> str:
        """Clean chunk text by removing page markers and extra whitespace"""
        try:
            import re
            # Remove page markers
            cleaned = re.sub(r'\[PAGE \d+\]\n?', '', chunk_text)
            
            # Clean up whitespace
            cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)  # Multiple newlines to double
            cleaned = re.sub(r' +', ' ', cleaned)  # Multiple spaces to single
            
            return cleaned.strip()
        except:
            return chunk_text.strip()