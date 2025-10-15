# Python 3.13 Setup Guide

Since you're using Python 3.13, some packages may not have compatible wheels yet. Here's how to set up the RAG Knowledge Base:

## Option 1: Install Core Dependencies Only

```bash
cd backend
source venv/bin/activate

# Install minimal requirements
pip install -r requirements-minimal.txt

# Try to install the problematic packages individually
pip install --only-binary=all numpy || pip install numpy
pip install --only-binary=all pandas || pip install pandas

# Try ChromaDB (may fail on Python 3.13)
pip install chromadb || echo "ChromaDB failed - will use simple vector service"

# Try sentence-transformers (optional)
pip install sentence-transformers || echo "sentence-transformers failed - using OpenAI embeddings only"
```

## Option 2: Use the Installation Script

```bash
cd backend
source venv/bin/activate
chmod +x install_deps.sh
./install_deps.sh
```

## Option 3: Use Python 3.11 (Recommended)

If you have issues with Python 3.13, consider using Python 3.11:

```bash
# Install Python 3.11 using pyenv or your system package manager
pyenv install 3.11.6
pyenv local 3.11.6

# Or use conda
conda create -n rag-kb python=3.11
conda activate rag-kb

# Then install normally
pip install -r requirements.txt
```

## Fallback Mode

The system is designed to work even if some packages fail:

- **ChromaDB fails**: Uses simple in-memory vector storage with JSON persistence
- **sentence-transformers fails**: Uses OpenAI embeddings only
- **numpy/pandas fail**: Some features may be limited but core functionality works

## Testing the Setup

```bash
# Test if the basic setup works
python -c "
import fastapi
import openai
import tiktoken
print('✅ Core dependencies working')
"

# Test vector service
python -c "
from services.vector_service import VectorService
print('✅ Vector service can be imported')
"

# Start the server
uvicorn main:app --reload
```

## Environment Variables

Make sure to set your OpenAI API key in `.env`:

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Common Issues

1. **setuptools error**: `pip install --upgrade setuptools wheel`
2. **Build tools missing**: Install Xcode command line tools on macOS
3. **ChromaDB fails**: The system will automatically fall back to simple storage
4. **Memory issues**: Reduce chunk size in `.env`: `CHUNK_SIZE=250`

The system is designed to be resilient and will work even with missing optional dependencies!