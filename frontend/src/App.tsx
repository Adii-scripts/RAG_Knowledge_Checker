import React, { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

// Components
import Header from './components/Header.tsx';
import Sidebar from './components/Sidebar.tsx';
import SearchInterface from './components/SearchInterface.tsx';
import DocumentUpload from './components/DocumentUpload.tsx';
import FloatingParticles from './components/FloatingParticles.tsx';

// Types
import { Document } from './types/index.ts';

// Services
import { documentService } from './services/api.ts';

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const docs = await documentService.getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentsUploaded = (newDocuments: Document[]) => {
    setDocuments(prev => [...prev, ...newDocuments]);
  };

  const handleDocumentDeleted = (documentId: string) => {
    setDocuments(prev => prev.filter(doc => doc.id !== documentId));
  };

  return (
    <div className="min-h-screen bg-dark-gradient animated-bg">
      <FloatingParticles />
      
      <div className="flex h-screen overflow-hidden">
        {/* Sidebar */}
        <AnimatePresence>
          {sidebarOpen && (
            <motion.div
              initial={{ x: -300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -300, opacity: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              className="w-80 flex-shrink-0"
            >
              <Sidebar
                documents={documents}
                loading={loading}
                onDocumentDeleted={handleDocumentDeleted}
                onRefresh={loadDocuments}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <Header
            sidebarOpen={sidebarOpen}
            onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
            documentsCount={documents.length}
          />

          {/* Main Content Area */}
          <main className="flex-1 overflow-hidden">
            {documents.length === 0 && !loading ? (
              // Upload State
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="h-full flex items-center justify-center p-8"
              >
                <div className="max-w-2xl w-full">
                  <div className="text-center mb-8">
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.2, duration: 0.5 }}
                      className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center"
                    >
                      <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </motion.div>
                    <h2 className="text-3xl font-bold gradient-text mb-4">
                      Welcome to RAG Knowledge Base
                    </h2>
                    <p className="text-dark-300 text-lg">
                      Upload your documents to start building your intelligent knowledge base
                    </p>
                  </div>
                  
                  <DocumentUpload onDocumentsUploaded={handleDocumentsUploaded} />
                </div>
              </motion.div>
            ) : (
              // Search Interface
              <SearchInterface documents={documents} />
            )}
          </main>
        </div>
      </div>

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'rgba(30, 41, 59, 0.9)',
            color: '#f8fafc',
            border: '1px solid rgba(124, 58, 237, 0.3)',
            backdropFilter: 'blur(10px)',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#f8fafc',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#f8fafc',
            },
          },
        }}
      />
    </div>
  );
}

export default App;