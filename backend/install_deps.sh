#!/bin/bash

echo "🔧 Installing dependencies for Python 3.13 compatibility..."

# Upgrade pip and install build tools first
pip install --upgrade pip setuptools wheel

# Install core dependencies first
echo "📦 Installing core FastAPI dependencies..."
pip install fastapi uvicorn[standard] python-multipart

# Install OpenAI dependencies
echo "🤖 Installing OpenAI dependencies..."
pip install openai tiktoken

# Install document processing
echo "📄 Installing document processing libraries..."
pip install PyPDF2 python-docx

# Install utilities
echo "⚙️ Installing utilities..."
pip install python-dotenv pydantic pydantic-settings aiofiles httpx loguru

# Install data processing with compatibility flags
echo "📊 Installing data processing libraries..."
pip install --only-binary=all numpy pandas || pip install numpy pandas

# Try to install ChromaDB
echo "🗄️ Installing ChromaDB..."
pip install chromadb || echo "⚠️ ChromaDB installation failed - you may need to install it manually"

# Try to install sentence-transformers
echo "🧠 Installing sentence-transformers..."
pip install sentence-transformers || echo "⚠️ sentence-transformers installation failed - you may need to install it manually"

# Optional: Install LangChain if needed
echo "🔗 Installing LangChain (optional)..."
pip install langchain langchain-openai || echo "⚠️ LangChain installation failed - skipping (optional)"

echo "✅ Installation complete!"
echo "⚠️ If any packages failed to install, you can try installing them individually with:"
echo "   pip install --no-deps <package-name>"
echo "   or use conda instead of pip for better compatibility"