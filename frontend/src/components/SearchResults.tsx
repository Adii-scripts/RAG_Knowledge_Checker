import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { 
  DocumentTextIcon, 
  ChevronDownIcon, 
  ChevronUpIcon,
  LinkIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

import { SourceCitation } from '../types';

interface SearchResultsProps {
  query: string;
  answer: string;
  sources: SourceCitation[];
  isLoading?: boolean;
  timestamp?: Date;
  isHistorical?: boolean;
}

const SearchResults: React.FC<SearchResultsProps> = ({
  query,
  answer,
  sources,
  isLoading = false,
  timestamp,
  isHistorical = false
}) => {
  const [showSources, setShowSources] = useState(!isHistorical);
  const [expandedSource, setExpandedSource] = useState<number | null>(null);

  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 0.9) return 'text-green-400';
    if (score >= 0.8) return 'text-blue-400';
    if (score >= 0.7) return 'text-yellow-400';
    return 'text-orange-400';
  };

  const getRelevanceLabel = (score: number) => {
    if (score >= 0.9) return 'Highly Relevant';
    if (score >= 0.8) return 'Very Relevant';
    if (score >= 0.7) return 'Relevant';
    return 'Somewhat Relevant';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`space-y-6 ${isHistorical ? 'opacity-80' : ''}`}
    >
      {/* Query */}
      <div className="flex items-start space-x-3">
        <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
          <span className="text-white text-sm font-bold">Q</span>
        </div>
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="font-semibold text-white">Your Question</h3>
            {timestamp && (
              <div className="flex items-center space-x-1 text-xs text-dark-400">
                <ClockIcon className="w-3 h-3" />
                <span>{formatTimestamp(timestamp)}</span>
              </div>
            )}
          </div>
          <p className="text-dark-200 bg-dark-800/50 rounded-lg p-3 border border-white/10">
            {query}
          </p>
        </div>
      </div>

      {/* Answer */}
      <div className="flex items-start space-x-3">
        <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-teal-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
          <span className="text-white text-sm font-bold">A</span>
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-white mb-2">Answer</h3>
          <div className="glass-strong rounded-lg p-4 border border-white/10">
            {isLoading && !answer ? (
              <div className="space-y-3">
                <div className="flex items-center space-x-2 text-purple-400">
                  <div className="spinner w-4 h-4"></div>
                  <span className="text-sm">Searching knowledge base...</span>
                </div>
                <div className="space-y-2">
                  <div className="skeleton h-4 w-full rounded"></div>
                  <div className="skeleton h-4 w-3/4 rounded"></div>
                  <div className="skeleton h-4 w-1/2 rounded"></div>
                </div>
              </div>
            ) : (
              <div className="prose prose-invert max-w-none">
                <ReactMarkdown
                  components={{
                    p: ({ children }) => (
                      <p className="text-dark-100 leading-relaxed mb-3 last:mb-0">
                        {children}
                      </p>
                    ),
                    strong: ({ children }) => (
                      <strong className="text-white font-semibold">
                        {children}
                      </strong>
                    ),
                    em: ({ children }) => (
                      <em className="text-purple-300">
                        {children}
                      </em>
                    ),
                    ul: ({ children }) => (
                      <ul className="list-disc list-inside space-y-1 text-dark-100">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="list-decimal list-inside space-y-1 text-dark-100">
                        {children}
                      </ol>
                    ),
                    li: ({ children }) => (
                      <li className="text-dark-100">
                        {children}
                      </li>
                    ),
                  }}
                >
                  {answer || 'Generating response...'}
                </ReactMarkdown>
                
                {isLoading && answer && (
                  <span className="typing-cursor inline-block ml-1"></span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Sources */}
      {sources.length > 0 && (
        <div className="flex items-start space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
            <DocumentTextIcon className="w-4 h-4 text-white" />
          </div>
          <div className="flex-1">
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex items-center space-x-2 mb-3 hover:text-purple-400 transition-colors"
            >
              <h3 className="font-semibold text-white">
                Sources ({sources.length})
              </h3>
              {showSources ? (
                <ChevronUpIcon className="w-4 h-4" />
              ) : (
                <ChevronDownIcon className="w-4 h-4" />
              )}
            </button>

            <AnimatePresence>
              {showSources && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-3"
                >
                  {sources.map((source, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="glass rounded-lg border border-white/10 overflow-hidden"
                    >
                      <div className="p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center space-x-2">
                            <DocumentTextIcon className="w-4 h-4 text-purple-400" />
                            <span className="font-medium text-white text-sm">
                              {source.document_name}
                            </span>
                            {source.page_number && (
                              <span className="text-xs text-dark-300 bg-dark-700 px-2 py-1 rounded">
                                Page {source.page_number}
                              </span>
                            )}
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <span className={`text-xs font-medium ${getRelevanceColor(source.relevance_score)}`}>
                              {getRelevanceLabel(source.relevance_score)}
                            </span>
                            <span className="text-xs text-dark-400">
                              {Math.round(source.relevance_score * 100)}%
                            </span>
                          </div>
                        </div>

                        <div className="text-sm text-dark-200 leading-relaxed">
                          {expandedSource === index ? (
                            <div>
                              <p className="mb-3">{source.excerpt}</p>
                              <button
                                onClick={() => setExpandedSource(null)}
                                className="text-purple-400 hover:text-purple-300 text-xs flex items-center space-x-1"
                              >
                                <ChevronUpIcon className="w-3 h-3" />
                                <span>Show less</span>
                              </button>
                            </div>
                          ) : (
                            <div>
                              <p className="mb-3">
                                {source.excerpt.length > 150
                                  ? `${source.excerpt.substring(0, 150)}...`
                                  : source.excerpt
                                }
                              </p>
                              {source.excerpt.length > 150 && (
                                <button
                                  onClick={() => setExpandedSource(index)}
                                  className="text-purple-400 hover:text-purple-300 text-xs flex items-center space-x-1"
                                >
                                  <ChevronDownIcon className="w-3 h-3" />
                                  <span>Show more</span>
                                </button>
                              )}
                            </div>
                          )}
                        </div>

                        <div className="mt-3 pt-3 border-t border-white/10 flex items-center justify-between text-xs text-dark-400">
                          <span>Chunk {source.chunk_index + 1}</span>
                          <div className="flex items-center space-x-1">
                            <LinkIcon className="w-3 h-3" />
                            <span>Reference</span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default SearchResults;