export interface Document {
  id: string;
  filename: string;
  file_type: 'pdf' | 'txt' | 'docx';
  file_size: number;
  upload_date: string;
  chunk_count: number;
  status: string;
}

export interface SourceCitation {
  document_id: string;
  document_name: string;
  page_number?: number;
  chunk_index: number;
  relevance_score: number;
  excerpt: string;
}

export interface QueryResponse {
  query: string;
  answer: string;
  sources: SourceCitation[];
  response_time: number;
  model_used: string;
  total_tokens?: number;
}

export interface StreamChunk {
  type: 'token' | 'sources' | 'status' | 'end' | 'error';
  content?: string;
  sources?: SourceCitation[];
  message?: string;
  response_time?: number;
  model_used?: string;
}

export interface UploadProgress {
  filename: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}