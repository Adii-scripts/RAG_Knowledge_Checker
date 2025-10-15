# 🧠 RAG Knowledge Base Search Engine

A production-ready **Retrieval-Augmented Generation (RAG)** system that allows users to upload documents and ask intelligent questions about their content using natural language.

![RAG Knowledge Base](https://img.shields.io/badge/RAG-Knowledge%20Base-blue?style=for-the-badge)
![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-4.9-3178C6?style=for-the-badge&logo=typescript)

## ✨ Features

### 🚀 **Core Functionality**
- **Document Upload**: Drag & drop PDF, TXT, DOCX files
- **Intelligent Querying**: Ask natural language questions about uploaded content
- **Streaming Responses**: Real-time, token-by-token AI responses
- **Source Citations**: References to specific documents and excerpts
- **Document Management**: View, organize, and delete uploaded files

### 🎨 **Modern UI/UX**
- **Dark Theme**: Professional glassmorphism design
- **Smooth Animations**: Framer Motion powered interactions
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live streaming interface like ChatGPT
- **Progress Indicators**: Visual feedback for uploads and processing

### 🧠 **Advanced AI Features**
- **Multi-Modal Search**: Fuzzy matching, synonym expansion, entity recognition
- **Intent Understanding**: Detects question types and user intent
- **Context Awareness**: Understands document types and provides relevant guidance
- **Conversation Memory**: Tracks context across queries
- **Smart Fallbacks**: Helpful guidance when content isn't found

## 🏗️ Architecture

### **Frontend (React + TypeScript)**
```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── DocumentUpload.tsx
│   │   ├── SearchInterface.tsx
│   │   ├── SearchResults.tsx
│   │   ├── Sidebar.tsx
│   │   └── Header.tsx
│   ├── services/           # API communication
│   │   └── api.ts
│   ├── types/              # TypeScript definitions
│   └── App.tsx
├── package.json
└── tailwind.config.js
```

### **Backend (FastAPI + Python)**
```
backend/
├── services/               # Core business logic
│   ├── document_service.py    # Document processing
│   ├── vector_service.py      # Vector storage (ChromaDB)
│   ├── rag_service.py         # RAG orchestration
│   ├── llm_service.py         # LLM integration
│   └── embedding_service.py   # Text embeddings
├── models/                 # Data models
│   └── schemas.py
├── core/                   # Configuration
│   ├── config.py
│   └── logging.py
├── utils/                  # Utilities
│   └── document_processor.py
├── main.py                 # FastAPI application
└── requirements.txt
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.11+
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/Adii-scripts/RAG_Knowledge_Checker.git
cd RAG_Knowledge_Checker
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key (optional - works in demo mode without it)

# Start the backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs

## 🎯 Usage

### **Upload Documents**
1. Drag and drop files into the upload area
2. Supported formats: PDF, TXT, DOCX
3. Watch real-time processing progress

### **Ask Questions**
- "What are the main challenges mentioned?"
- "What skills are described in the resume?"
- "Summarize the key findings"
- "What methodologies are discussed?"

### **Advanced Queries**
- "Compare technical skills with work experience"
- "How many years of experience are mentioned?"
- "What programming languages and frameworks are used?"

## 🛠️ Configuration

### **Environment Variables**
```bash
# Backend (.env)
OPENAI_API_KEY=your_openai_api_key_here  # Optional - works in demo mode
CHROMA_PERSIST_DIRECTORY=./chroma_db
MAX_FILE_SIZE=10485760  # 10MB
CHUNK_SIZE=500
TOP_K_RESULTS=5
```

### **Demo Mode**
The system works perfectly without OpenAI API keys:
- ✅ Document upload and processing
- ✅ Intelligent demo responses
- ✅ Full UI functionality
- ✅ Source citations with realistic examples

## 🔧 Technical Details

### **Key Technologies**
- **Frontend**: React 18, TypeScript, Tailwind CSS, Framer Motion
- **Backend**: FastAPI, Python 3.13, ChromaDB, Pydantic
- **AI/ML**: OpenAI GPT (with demo fallback), Text embeddings
- **Storage**: ChromaDB vector database, In-memory caching

### **Advanced Features**
- **Semantic Search**: Multi-modal search with fuzzy matching
- **NLP Processing**: Intent detection, entity recognition
- **Document Processing**: Smart chunking, multi-format support
- **Streaming**: Server-Sent Events for real-time responses
- **Error Handling**: Graceful fallbacks and user guidance

## 📊 Performance

- **Upload Speed**: Handles files up to 10MB
- **Query Response**: < 2 seconds average
- **Concurrent Users**: Supports multiple simultaneous users
- **Memory Efficient**: Optimized chunking and caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT and embedding models
- **ChromaDB** for vector storage
- **FastAPI** for the excellent Python web framework
- **React** and **Tailwind CSS** for the modern frontend

## 📞 Support

If you have any questions or need help:
- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/Adii-scripts/RAG_Knowledge_Checker/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Adii-scripts/RAG_Knowledge_Checker/discussions)

---

**Built with ❤️ by [Aditya](https://github.com/Adii-scripts)**

⭐ **Star this repo if you found it helpful!**