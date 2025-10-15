import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CloudArrowUpIcon, 
  DocumentTextIcon, 
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

import { Document, UploadProgress } from '../types/index.ts';
import { documentService } from '../services/api.ts';

interface DocumentUploadProps {
  onDocumentsUploaded: (documents: Document[]) => void;
  compact?: boolean;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ 
  onDocumentsUploaded, 
  compact = false 
}) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    setUploading(true);
    setUploadProgress([]);

    try {
      console.log('Starting upload process...');
      
      // Direct fetch call without using the service
      const formData = new FormData();
      acceptedFiles.forEach(file => {
        formData.append('files', file);
      });

      console.log('Making direct fetch request...');
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });

      console.log('Response received:', response.status);

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('Upload successful:', result);

      // Show success message
      toast.success(result.message);
      
      // Notify parent component
      onDocumentsUploaded(result.documents);

    } catch (error: any) {
      console.error('Upload failed:', error);
      toast.error(error.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [onDocumentsUploaded]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    disabled: uploading
  });

  const getStatusIcon = (status: UploadProgress['status']) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return <div className="spinner w-4 h-4"></div>;
      case 'completed':
        return <CheckCircleIcon className="w-4 h-4 text-green-400" />;
      case 'error':
        return <XCircleIcon className="w-4 h-4 text-red-400" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: UploadProgress['status']) => {
    switch (status) {
      case 'uploading':
        return 'bg-blue-500';
      case 'processing':
        return 'bg-yellow-500';
      case 'completed':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (compact) {
    return (
      <div className="space-y-4">
        {/* Compact Upload Area */}
        <motion.div
          {...getRootProps()}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className={`
            relative p-4 border-2 border-dashed rounded-lg cursor-pointer transition-all duration-200
            ${isDragActive && !isDragReject ? 'border-purple-400 bg-purple-400/10' : ''}
            ${isDragReject ? 'border-red-400 bg-red-400/10' : ''}
            ${!isDragActive ? 'border-dark-600 hover:border-purple-400/50 hover:bg-white/5' : ''}
            ${uploading ? 'pointer-events-none opacity-50' : ''}
          `}
        >
          <input {...getInputProps()} />
          <div className="flex items-center space-x-3">
            <CloudArrowUpIcon className="w-6 h-6 text-purple-400" />
            <div className="flex-1">
              <p className="text-sm font-medium text-white">
                {isDragActive ? 'Drop files here' : 'Upload documents'}
              </p>
              <p className="text-xs text-dark-300">
                PDF, TXT, DOCX • Max 10MB
              </p>
            </div>
          </div>
        </motion.div>

        {/* Progress List */}
        <AnimatePresence>
          {uploadProgress.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-2"
            >
              {uploadProgress.map((item, index) => (
                <motion.div
                  key={item.filename}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-3 glass rounded-lg"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-white truncate">
                      {item.filename}
                    </span>
                    {getStatusIcon(item.status)}
                  </div>
                  
                  {item.status !== 'completed' && (
                    <div className="w-full bg-dark-700 rounded-full h-1.5">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${item.progress}%` }}
                        className={`h-1.5 rounded-full ${getStatusColor(item.status)}`}
                      />
                    </div>
                  )}
                  
                  {item.error && (
                    <p className="text-xs text-red-400 mt-1">{item.error}</p>
                  )}
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Main Upload Area */}
      <motion.div
        {...getRootProps()}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className={`
          relative p-12 border-2 border-dashed rounded-2xl cursor-pointer transition-all duration-300
          ${isDragActive && !isDragReject ? 'border-purple-400 bg-purple-400/10 shadow-neon' : ''}
          ${isDragReject ? 'border-red-400 bg-red-400/10' : ''}
          ${!isDragActive ? 'border-dark-600 hover:border-purple-400/50 hover:bg-white/5' : ''}
          ${uploading ? 'pointer-events-none opacity-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="text-center">
          <motion.div
            animate={{ 
              y: isDragActive ? -10 : 0,
              scale: isDragActive ? 1.1 : 1 
            }}
            transition={{ duration: 0.2 }}
            className="mx-auto w-16 h-16 mb-6 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center"
          >
            <CloudArrowUpIcon className="w-8 h-8 text-white" />
          </motion.div>
          
          <h3 className="text-xl font-semibold text-white mb-2">
            {isDragActive ? 'Drop your files here' : 'Upload your documents'}
          </h3>
          
          <p className="text-dark-300 mb-4">
            {isDragReject 
              ? 'Some files are not supported' 
              : 'Drag and drop files here, or click to browse'
            }
          </p>
          
          <div className="flex items-center justify-center space-x-4 text-sm text-dark-400">
            <div className="flex items-center space-x-1">
              <DocumentTextIcon className="w-4 h-4" />
              <span>PDF, TXT, DOCX</span>
            </div>
            <div className="w-1 h-1 bg-dark-400 rounded-full"></div>
            <span>Max 10MB per file</span>
          </div>
        </div>

        {/* Upload overlay */}
        {isDragActive && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 bg-purple-500/20 rounded-2xl flex items-center justify-center"
          >
            <div className="text-center">
              <CloudArrowUpIcon className="w-12 h-12 text-purple-400 mx-auto mb-2" />
              <p className="text-lg font-medium text-white">Drop to upload</p>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Upload Progress */}
      <AnimatePresence>
        {uploadProgress.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            <h4 className="text-lg font-semibold text-white">Upload Progress</h4>
            
            <div className="space-y-3">
              {uploadProgress.map((item, index) => (
                <motion.div
                  key={item.filename}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 glass rounded-lg"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <DocumentTextIcon className="w-5 h-5 text-purple-400" />
                      <span className="font-medium text-white">{item.filename}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(item.status)}
                      <span className="text-sm text-dark-300 capitalize">
                        {item.status}
                      </span>
                    </div>
                  </div>
                  
                  {item.status !== 'completed' && (
                    <div className="w-full bg-dark-700 rounded-full h-2">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${item.progress}%` }}
                        transition={{ duration: 0.5 }}
                        className={`h-2 rounded-full ${getStatusColor(item.status)}`}
                      />
                    </div>
                  )}
                  
                  {item.error && (
                    <div className="mt-2 flex items-center space-x-2 text-red-400">
                      <ExclamationTriangleIcon className="w-4 h-4" />
                      <span className="text-sm">{item.error}</span>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DocumentUpload;