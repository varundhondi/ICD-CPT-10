# Deployment Guide for Speech-to-Code AI App

## 🚀 Quick Deploy Options

### Option 1: Streamlit Cloud (Recommended - Free)

**Steps:**
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select your repository
5. Set main file path: `app.py`
6. Deploy!

**Requirements:**
- GitHub repository with your code
- `requirements.txt` file (already created)
- `.streamlit/config.toml` (already configured)

### Option 2: Heroku

**Steps:**
1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
3. Deploy:
   ```bash
   heroku create your-app-name
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Option 3: Railway

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `streamlit run app.py --server.port=$PORT`
5. Deploy!

### Option 4: Google Cloud Run

**Steps:**
1. Create `Dockerfile` (see below)
2. Build and push to Google Container Registry
3. Deploy to Cloud Run

### Option 5: AWS Elastic Beanstalk

**Steps:**
1. Create `Dockerfile` (see below)
2. Package as ZIP file
3. Upload to Elastic Beanstalk

## 📁 Required Files for Deployment

### 1. Dockerfile (for containerized deployment)
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. .dockerignore
```
venv/
__pycache__/
*.pyc
.env
.git/
.gitignore
README.md
*.md
```

### 3. runtime.txt (for Heroku)
```
python-3.10.0
```

## 🔧 Environment Variables

Set these in your deployment platform:

```bash
# For pyannote.audio (optional)
HUGGING_FACE_TOKEN=your_token_here

# For OpenAI Whisper (if using API)
OPENAI_API_KEY=your_key_here
```

## 📊 Performance Considerations

### Memory Requirements
- **Minimum**: 2GB RAM
- **Recommended**: 4GB+ RAM
- **GPU**: Optional but recommended for faster processing

### Storage Requirements
- **Minimum**: 1GB
- **Recommended**: 5GB+ for audio processing

## 🚨 Important Notes

### 1. File Size Limits
- Streamlit Cloud: 200MB per file
- Heroku: 500MB total
- Consider using cloud storage for large audio files

### 2. Processing Time
- Audio processing can take 30-60 seconds
- Consider implementing progress bars
- Add timeout handling

### 3. Security
- Don't commit sensitive data
- Use environment variables for API keys
- Implement rate limiting for production

## 🔍 Troubleshooting

### Common Issues:

1. **Memory Errors**
   - Reduce batch size in audio processing
   - Use smaller audio files
   - Implement streaming processing

2. **Timeout Errors**
   - Increase timeout limits
   - Implement async processing
   - Use background jobs

3. **Import Errors**
   - Check all dependencies in requirements.txt
   - Ensure Python version compatibility
   - Test locally before deploying

## 📈 Monitoring & Analytics

### Recommended Tools:
- **Streamlit Cloud**: Built-in analytics
- **Heroku**: Heroku Metrics
- **Google Cloud**: Cloud Monitoring
- **AWS**: CloudWatch

## 🎯 Production Checklist

- [ ] All dependencies in requirements.txt
- [ ] Environment variables configured
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Performance optimized
- [ ] Security measures in place
- [ ] Backup strategy defined
- [ ] Monitoring setup
- [ ] Documentation updated

## 🆘 Support

For deployment issues:
1. Check platform-specific documentation
2. Review error logs
3. Test locally first
4. Contact platform support

## 📞 Quick Deploy Commands

### Streamlit Cloud
```bash
# Just push to GitHub and deploy via web interface
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Heroku
```bash
heroku create your-app-name
git push heroku main
heroku open
```

### Railway
```bash
railway login
railway init
railway up
```

### Docker
```bash
docker build -t speech-to-code-ai .
docker run -p 8501:8501 speech-to-code-ai
``` 