import React from 'react';
import { motion } from 'framer-motion';
import { Bars3Icon, DocumentTextIcon, CpuChipIcon } from '@heroicons/react/24/outline';

interface HeaderProps {
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
  documentsCount: number;
}

const Header: React.FC<HeaderProps> = ({ sidebarOpen, onToggleSidebar, documentsCount }) => {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="glass-strong border-b border-white/10 px-6 py-4"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {/* Sidebar Toggle */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onToggleSidebar}
            className="p-2 rounded-lg glass hover:bg-white/10 transition-all duration-200 focus-ring"
            aria-label="Toggle sidebar"
          >
            <Bars3Icon className="w-6 h-6 text-dark-200" />
          </motion.button>

          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <motion.div
              initial={{ rotate: 0 }}
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center"
            >
              <CpuChipIcon className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <h1 className="text-xl font-bold gradient-text">
                RAG Knowledge Base
              </h1>
              <p className="text-sm text-dark-300">
                Intelligent Document Search
              </p>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="flex items-center space-x-6">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="flex items-center space-x-2 px-4 py-2 glass rounded-lg"
          >
            <DocumentTextIcon className="w-5 h-5 text-purple-400" />
            <span className="text-sm font-medium text-dark-200">
              {documentsCount} {documentsCount === 1 ? 'Document' : 'Documents'}
            </span>
          </motion.div>

          {/* Status Indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="flex items-center space-x-2"
          >
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-dark-300">Online</span>
          </motion.div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;