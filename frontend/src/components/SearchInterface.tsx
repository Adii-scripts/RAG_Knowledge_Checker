import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MagnifyingGlassIcon, 
  PaperAirplaneIcon,
  SparklesIcon,
  DocumentTextIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

import { Document, StreamChunk, SourceCitation } from '../types/index.ts';
import { queryService } from '../services/api.ts';
import SearchResults from './SearchResults.tsx';

interface SearchInterfaceProps {
  documents: Document[];
}

const SearchInterface: React.FC<SearchInterfaceProps> = ({ documents }) => {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [sources, setSources] = useState<SourceCitation[]>([]);
  const [searchHistory, setSearchHistory] = useState<Array<{
    query: string;
    answer: string;
    sources: SourceCitation[];
    timestamp: Date;
  }>>([]);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Focus input on mount
    inputRef.current?.focus();
  }, []);

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim() || isSearching) return;

    setIsSearching(true);
    setCurrentAnswer('');
    setSources([]);

    try {
      let fullAnswer = '';
      let searchSources: SourceCitation[] = [];

      await queryService.queryStream(
        searchQuery.trim(),
        5,
        (chunk: StreamChunk) => {
          switch (chunk.type) {
            case 'status':
              // Handle status updates if needed
              break;
              
            case 'token':
              if (chunk.content) {
                fullAnswer += chunk.content;
                setCurrentAnswer(fullAnswer);
              }
              break;
              
            case 'sources':
              if (chunk.sources) {
                searchSources = chunk.sources;
                setSources(searchSources);
              }
              break;
              
            case 'end':
              // Search completed
              if (fullAnswer && searchSources) {
                setSearchHistory(prev => [{
                  query: searchQuery,
                  answer: fullAnswer,
                  sources: searchSources,
                  timestamp: new Date()
                }, ...prev.slice(0, 9)]); // Keep last 10 searches
              }
              break;
              
            case 'error':
              throw new Error(chunk.message || 'Search failed');
          }
        }
      );

    } catch (error: any) {
      console.error('Search failed:', error);
      toast.error(error.message || 'Search failed');
      setCurrentAnswer('');
      setSources([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch(query);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    handleSearch(suggestion);
  };

  const suggestions = [
    "What are the main topics covered in these documents?",
    "Summarize the key findings from the research papers",
    "What methodologies are discussed?",
    "What are the limitations mentioned?",
    "Compare the different approaches presented"
  ];

  return (
    <div className="h-full flex flex-col">
      {/* Search Header */}
      <div className="p-6 border-b border-white/10">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl font-bold gradient-text mb-2">
            Ask your documents anything
          </h2>
          <p className="text-dark-300">
            Search through {documents.length} documents using natural language
          </p>
        </motion.div>
      </div>

      {/* Search Input */}
      <div className="p-6">
        <motion.form
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          onSubmit={handleSubmit}
          className="relative"
        >
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              {isSearching ? (
                <div className="spinner w-5 h-5"></div>
              ) : (
                <MagnifyingGlassIcon className="w-5 h-5 text-dark-400" />
              )}
            </div>
            
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about your documents..."
              disabled={isSearching}
              className="
                w-full pl-12 pr-12 py-4 
                glass-strong rounded-2xl 
                text-white placeholder-dark-400 
                border border-white/10 
                focus:border-purple-400/50 focus:ring-2 focus:ring-purple-400/20 
                transition-all duration-200
                disabled:opacity-50 disabled:cursor-not-allowed
              "
            />
            
            <div className="absolute inset-y-0 right-0 pr-2 flex items-center">
              <motion.button
                type="submit"
                disabled={!query.trim() || isSearching}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="
                  p-2 rounded-xl
                  bg-gradient-to-r from-purple-500 to-blue-500
                  text-white
                  disabled:opacity-50 disabled:cursor-not-allowed
                  hover:shadow-neon
                  transition-all duration-200
                "
              >
                <PaperAirplaneIcon className="w-5 h-5" />
              </motion.button>
            </div>
          </div>
        </motion.form>

        {/* Suggestions */}
        {!currentAnswer && !isSearching && searchHistory.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-6"
          >
            <div className="flex items-center space-x-2 mb-4">
              <SparklesIcon className="w-5 h-5 text-purple-400" />
              <span className="text-sm font-medium text-dark-200">
                Try asking:
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {suggestions.map((suggestion, index) => (
                <motion.button
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + index * 0.1 }}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="
                    p-4 text-left glass rounded-lg 
                    hover:bg-white/5 hover:border-purple-400/30
                    border border-transparent
                    transition-all duration-200
                    group
                  "
                >
                  <p className="text-sm text-dark-200 group-hover:text-white transition-colors">
                    {suggestion}
                  </p>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </div>

      {/* Results Area */}
      <div className="flex-1 overflow-hidden">
        <div ref={resultsRef} className="h-full overflow-y-auto px-6 pb-6">
          {/* Current Search Results */}
          {(currentAnswer || isSearching) && (
            <SearchResults
              query={query}
              answer={currentAnswer}
              sources={sources}
              isLoading={isSearching}
            />
          )}

          {/* Search History */}
          {searchHistory.length > 0 && !currentAnswer && !isSearching && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="space-y-6"
            >
              <div className="flex items-center space-x-2 mb-6">
                <ClockIcon className="w-5 h-5 text-dark-400" />
                <h3 className="text-lg font-semibold text-white">Recent Searches</h3>
              </div>

              {searchHistory.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="space-y-4"
                >
                  <SearchResults
                    query={item.query}
                    answer={item.answer}
                    sources={item.sources}
                    timestamp={item.timestamp}
                    isHistorical
                  />
                  
                  {index < searchHistory.length - 1 && (
                    <div className="border-b border-white/10"></div>
                  )}
                </motion.div>
              ))}
            </motion.div>
          )}

          {/* Empty State */}
          {!currentAnswer && !isSearching && searchHistory.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.6 }}
              className="flex items-center justify-center h-full"
            >
              <div className="text-center max-w-md">
                <motion.div
                  animate={{ 
                    rotate: [0, 10, -10, 0],
                    scale: [1, 1.1, 1]
                  }}
                  transition={{ 
                    duration: 2, 
                    repeat: Infinity, 
                    repeatDelay: 3 
                  }}
                  className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center"
                >
                  <DocumentTextIcon className="w-10 h-10 text-white" />
                </motion.div>
                
                <h3 className="text-xl font-semibold text-white mb-2">
                  Ready to search
                </h3>
                <p className="text-dark-300">
                  Ask questions about your documents and get intelligent answers with source citations
                </p>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchInterface;