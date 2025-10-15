#!/bin/bash

# RAG Knowledge Base Setup Script
echo "🚀 Setting up RAG Knowledge Base..."

# Check if required tools are installed
check_requirements() {
    echo "📋 Checking requirements..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3.9+ is required but not installed."
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 18+ is required but not installed."
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo "❌ npm is required but not installed."
        exit 1
    fi
    
    echo "✅ All requirements satisfied"
}

# Setup backend
setup_backend() {
    echo "🔧 Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create necessary directories
    mkdir -p uploads logs chroma_db
    
    echo "✅ Backend setup complete"
    cd ..
}

# Setup frontend
setup_frontend() {
    echo "🎨 Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    npm install
    
    echo "✅ Frontend setup complete"
    cd ..
}

# Setup environment
setup_environment() {
    echo "⚙️ Setting up environment..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "📝 Created .env file from template"
        echo "⚠️  Please edit .env and add your OpenAI API key"
    else
        echo "✅ .env file already exists"
    fi
}

# Main setup function
main() {
    check_requirements
    setup_environment
    setup_backend
    setup_frontend
    
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file and add your OpenAI API key"
    echo "2. Start the backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
    echo "3. Start the frontend: cd frontend && npm start"
    echo "4. Open http://localhost:3000 in your browser"
    echo ""
    echo "Or use Docker: docker-compose up --build"
}

# Run main function
main