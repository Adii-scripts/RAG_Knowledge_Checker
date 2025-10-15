import axios from 'axios';
import { Document, QueryResponse, StreamChunk } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    if (error.response?.status === 422) {
      throw new Error('Invalid request data');
    } else if (error.response?.status === 500) {
      throw new Error('Server error. Please try again later.');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please try again.');
    } else if (!error.response) {
      throw new Error('Network error. Please check your connection.');
    }
    
    throw error;
  }
);

export const documentService = {
  async uploadDocuments(files: File[]): Promise<{ documents: Document[]; message: string }> {
    console.log('Starting upload for files:', files.map(f => f.name));
    
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    console.log('FormData created, making request to:', `${API_BASE_URL}/api/upload`);

    try {
      // Use fetch instead of axios for better multipart handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

      const response = await fetch(`${API_BASE_URL}/api/upload`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
        // Don't set Content-Type header - let browser set it with boundary
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Upload successful:', data);
      return data;
    } catch (error) {
      console.error('Upload failed with error:', error);
      throw error;
    }
  },

  async getDocuments(): Promise<Document[]> {
    const response = await api.get('/api/documents');
    return response.data;
  },

  async deleteDocument(documentId: string): Promise<void> {
    await api.delete(`/api/documents/${documentId}`);
  },
};

export const queryService = {
  async queryStream(
    query: string,
    topK: number = 5,
    onChunk: (chunk: StreamChunk) => void
  ): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        top_k: topK,
        include_sources: true,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Failed to get response reader');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // Process complete lines
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onChunk(data);
              
              if (data.type === 'end' || data.type === 'error') {
                return;
              }
            } catch (error) {
              console.warn('Failed to parse SSE data:', line);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },
};

export const healthService = {
  async checkHealth(): Promise<any> {
    const response = await api.get('/api/health');
    return response.data;
  },
};

export default api;