# 🚀 Deployment Guide

This guide covers different deployment options for the RAG Knowledge Base.

## 🐳 Docker Deployment (Recommended)

### Prerequisites
- Docker and Docker Compose installed

### Quick Deploy
```bash
# Clone the repository
git clone https://github.com/Adii-scripts/RAG_Knowledge_Checker.git
cd RAG_Knowledge_Checker

# Start with Docker Compose
docker-compose up -d
```

### Manual Docker Build
```bash
# Build backend
cd backend
docker build -t rag-backend .

# Build frontend
cd ../frontend
docker build -t rag-frontend .

# Run containers
docker run -d -p 8000:8000 --name rag-backend-container rag-backend
docker run -d -p 3000:3000 --name rag-frontend-container rag-frontend
```

## ☁️ Cloud Deployment

### Vercel (Frontend)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend
vercel --prod
```

### Railway/Render (Backend)
1. Connect your GitHub repository
2. Set environment variables:
   - `OPENAI_API_KEY` (optional)
   - `PORT=8000`
3. Deploy automatically on push

### AWS/GCP/Azure
- Use container services (ECS, Cloud Run, Container Instances)
- Set up load balancers for production traffic
- Configure environment variables in cloud console

## 🔧 Production Configuration

### Environment Variables
```bash
# Backend
OPENAI_API_KEY=your_key_here
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com
MAX_FILE_SIZE=20971520  # 20MB for production

# Frontend
REACT_APP_API_URL=https://your-backend-url.com
REACT_APP_ENVIRONMENT=production
```

### Performance Optimization
- Enable gzip compression
- Set up CDN for static assets
- Configure caching headers
- Use production builds (`npm run build`)

## 📊 Monitoring

### Health Checks
- Backend: `GET /api/health`
- Frontend: Check if app loads successfully

### Logging
- Backend logs to stdout (captured by container orchestration)
- Frontend errors logged to browser console
- Set up log aggregation (ELK stack, CloudWatch, etc.)

## 🔒 Security

### Production Checklist
- [ ] Set strong CORS origins
- [ ] Use HTTPS in production
- [ ] Validate file uploads
- [ ] Set rate limiting
- [ ] Monitor for suspicious activity
- [ ] Regular security updates

### API Security
```python
# Add to main.py for production
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy RAG Knowledge Base

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy Backend
        run: |
          # Your backend deployment commands
          
      - name: Deploy Frontend
        run: |
          # Your frontend deployment commands
```

## 📈 Scaling

### Horizontal Scaling
- Use load balancers
- Deploy multiple backend instances
- Implement session stickiness if needed

### Database Scaling
- Use managed vector databases (Pinecone, Weaviate)
- Implement database connection pooling
- Consider read replicas for high traffic

## 🛠️ Troubleshooting

### Common Issues
1. **CORS Errors**: Check CORS_ORIGINS configuration
2. **File Upload Fails**: Verify MAX_FILE_SIZE settings
3. **Slow Responses**: Check OpenAI API quotas
4. **Memory Issues**: Increase container memory limits

### Debug Commands
```bash
# Check container logs
docker logs rag-backend-container
docker logs rag-frontend-container

# Check service health
curl http://localhost:8000/api/health
curl http://localhost:3000
```

## 📞 Support

For deployment issues:
- Check the [Issues](https://github.com/Adii-scripts/RAG_Knowledge_Checker/issues) page
- Review logs for error messages
- Ensure all environment variables are set correctly