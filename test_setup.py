#!/usr/bin/env python3
"""
Quick test script to verify RAG Knowledge Base setup
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import openai
        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False
    
    try:
        import tiktoken
        print("✅ tiktoken imported successfully")
    except ImportError as e:
        print(f"❌ tiktoken import failed: {e}")
        return False
    
    try:
        from core.config import settings
        print("✅ Configuration loaded successfully")
        print(f"   - OpenAI API key: {'✅ Set' if settings.openai_api_key.startswith('sk-') else '❌ Not set'}")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False
    
    try:
        from services.vector_service import VectorService
        print("✅ Vector service imported successfully")
    except ImportError as e:
        print(f"❌ Vector service import failed: {e}")
        return False
    
    return True

def test_vector_service():
    """Test vector service initialization"""
    print("\n🔧 Testing vector service...")
    
    try:
        from services.vector_service import VectorService
        vector_service = VectorService()
        print("✅ Vector service created")
        
        # Check which service will be used
        if hasattr(vector_service, 'use_chromadb') and vector_service.use_chromadb:
            print("✅ Will use ChromaDB")
        else:
            print("✅ Will use simple vector service (fallback)")
        
        return True
    except Exception as e:
        print(f"❌ Vector service test failed: {e}")
        return False

def main():
    print("🚀 RAG Knowledge Base Setup Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install missing dependencies.")
        return False
    
    # Test vector service
    if not test_vector_service():
        print("\n❌ Vector service test failed.")
        return False
    
    print("\n🎉 All tests passed! Your setup looks good.")
    print("\nNext steps:")
    print("1. Start backend: cd backend && uvicorn main:app --reload")
    print("2. Start frontend: cd frontend && npm start")
    print("3. Open http://localhost:3000 in your browser")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)