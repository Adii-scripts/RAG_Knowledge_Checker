import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  DocumentTextIcon, 
  TrashIcon, 
  ArrowUpTrayIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

import { Document } from '../types/index.ts';
import { documentService } from '../services/api.ts';
import DocumentUpload from './DocumentUpload.tsx';

interface SidebarProps {
  documents: Document[];
  loading: boolean;
  onDocumentDeleted: (documentId: string) => void;
  onRefresh: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  documents, 
  loading, 
  onDocumentDeleted, 
  onRefresh 
}) => {
  const [showUpload, setShowUpload] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDeleteDocument = async (document: Document) => {
    if (!window.confirm(`Are you sure you want to delete "${document.filename}"?`)) {
      return;
    }

    try {
      setDeletingId(document.id);
      await documentService.deleteDocument(document.id);
      onDocumentDeleted(document.id);
      toast.success(`Deleted ${document.filename}`);
    } catch (error) {
      console.error('Failed to delete document:', error);
      toast.error('Failed to delete document');
    } finally {
      setDeletingId(null);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case 'pdf':
        return '📄';
      case 'docx':
        return '📝';
      case 'txt':
        return '📃';
      default:
        return '📄';
    }
  };

  return (
    <div className="h-full glass-strong border-r border-white/10 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Documents</h2>
          <div className="flex space-x-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onRefresh}
              disabled={loading}
              className="p-2 rounded-lg glass hover:bg-white/10 transition-all duration-200 focus-ring disabled:opacity-50"
              title="Refresh documents"
            >
              <ArrowPathIcon className={`w-4 h-4 text-dark-200 ${loading ? 'animate-spin' : ''}`} />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowUpload(!showUpload)}
              className="p-2 rounded-lg glass hover:bg-white/10 transition-all duration-200 focus-ring"
              title="Upload documents"
            >
              <ArrowUpTrayIcon className="w-4 h-4 text-dark-200" />
            </motion.button>
          </div>
        </div>

        {/* Upload Section */}
        <AnimatePresence>
          {showUpload && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <DocumentUpload
                onDocumentsUploaded={(newDocs) => {
                  setShowUpload(false);
                  onRefresh();
                }}
                compact
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Documents List */}
      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          // Loading Skeleton
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="p-4 glass rounded-lg">
                <div className="skeleton h-4 w-3/4 mb-2 rounded"></div>
                <div className="skeleton h-3 w-1/2 mb-1 rounded"></div>
                <div className="skeleton h-3 w-1/3 rounded"></div>
              </div>
            ))}
          </div>
        ) : documents.length === 0 ? (
          // Empty State
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12"
          >
            <DocumentTextIcon className="w-16 h-16 text-dark-400 mx-auto mb-4" />
            <p className="text-dark-300 mb-2">No documents uploaded</p>
            <p className="text-sm text-dark-400">
              Upload documents to start building your knowledge base
            </p>
          </motion.div>
        ) : (
          // Documents List
          <div className="space-y-3">
            {documents.map((document, index) => (
              <motion.div
                key={document.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="group p-4 glass rounded-lg hover:bg-white/5 transition-all duration-200"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-lg">{getFileIcon(document.file_type)}</span>
                      <h3 className="text-sm font-medium text-white truncate">
                        {document.filename}
                      </h3>
                    </div>
                    
                    <div className="space-y-1 text-xs text-dark-300">
                      <div className="flex items-center justify-between">
                        <span>{formatFileSize(document.file_size)}</span>
                        <span>{document.chunk_count} chunks</span>
                      </div>
                      <div>{formatDate(document.upload_date)}</div>
                      
                      {document.status !== 'processed' && (
                        <div className="flex items-center space-x-1 text-yellow-400">
                          <ExclamationTriangleIcon className="w-3 h-3" />
                          <span className="capitalize">{document.status}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Delete Button */}
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => handleDeleteDocument(document)}
                    disabled={deletingId === document.id}
                    className="opacity-0 group-hover:opacity-100 p-1 rounded text-red-400 hover:text-red-300 hover:bg-red-400/10 transition-all duration-200 disabled:opacity-50"
                    title="Delete document"
                  >
                    {deletingId === document.id ? (
                      <div className="spinner w-4 h-4"></div>
                    ) : (
                      <TrashIcon className="w-4 h-4" />
                    )}
                  </motion.button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-white/10">
        <div className="text-xs text-dark-400 text-center">
          <p>Total: {documents.length} documents</p>
          <p className="mt-1">
            {documents.reduce((sum, doc) => sum + doc.chunk_count, 0)} chunks indexed
          </p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;