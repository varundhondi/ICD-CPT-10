# 🚀 Quick Deployment Guide

## Fastest Deployment Options

### Option 1: Streamlit Cloud (Recommended - 5 minutes)

**Prerequisites:**
- GitHub account
- Your code pushed to GitHub

**Steps:**
1. **Push to GitHub** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy!"

**✅ Done!** Your app will be live in 2-3 minutes.

---

### Option 2: Railway (Alternative - 10 minutes)

**Prerequisites:**
- GitHub account
- Railway account (free)

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Railway will auto-detect it's a Python app
7. Click "Deploy"

**✅ Done!** Your app will be live in 5-10 minutes.

---

### Option 3: Docker (Local/Cloud - 15 minutes)

**Prerequisites:**
- Docker installed

**Steps:**
1. **Build the image**:
   ```bash
   docker build -t speech-to-code-ai .
   ```

2. **Run locally**:
   ```bash
   docker run -p 8501:8501 speech-to-code-ai
   ```

3. **Deploy to cloud** (choose one):
   - **Google Cloud Run**: `gcloud run deploy`
   - **AWS ECS**: Use AWS CLI
   - **Azure Container Instances**: Use Azure CLI

---

### Option 4: Heroku (15 minutes)

**Prerequisites:**
- Heroku account
- Heroku CLI installed

**Steps:**
1. **Login to Heroku**:
   ```bash
   heroku login
   ```

2. **Deploy**:
   ```bash
   heroku create your-app-name
   git push heroku main
   heroku open
   ```

---

## 🎯 Recommended: Streamlit Cloud

**Why Streamlit Cloud?**
- ✅ **Free** for public apps
- ✅ **No configuration** needed
- ✅ **Automatic HTTPS**
- ✅ **Built-in analytics**
- ✅ **Easy updates** (just push to GitHub)
- ✅ **Perfect for Streamlit apps**

**Limitations:**
- ❌ 200MB file size limit
- ❌ Public repository required (for free tier)
- ❌ No custom domain (free tier)

---

## 🔧 Environment Variables

If you need to set environment variables (like Hugging Face token):

### Streamlit Cloud:
1. Go to your app settings
2. Add secrets in the format:
   ```
   HUGGING_FACE_TOKEN = "your_token_here"
   ```

### Railway:
1. Go to your project
2. Click "Variables"
3. Add key-value pairs

### Heroku:
```bash
heroku config:set HUGGING_FACE_TOKEN=your_token_here
```

---

## 📊 Performance Tips

### For Production:
1. **Use smaller audio files** (under 50MB)
2. **Implement progress bars** for long operations
3. **Add error handling** for timeouts
4. **Consider caching** for repeated operations

### Memory Optimization:
- The app uses ~2-4GB RAM during processing
- Most cloud platforms support this
- Consider upgrading if you get memory errors

---

## 🚨 Troubleshooting

### Common Issues:

1. **"Module not found" errors**:
   - Check `requirements.txt` has all dependencies
   - Ensure Python 3.10+ is used

2. **Memory errors**:
   - Use smaller audio files
   - Upgrade to higher memory tier

3. **Timeout errors**:
   - Audio processing can take 30-60 seconds
   - Consider implementing background jobs

4. **File size errors**:
   - Streamlit Cloud: 200MB limit
   - Use cloud storage for large files

---

## 📞 Quick Commands

### Check if ready to deploy:
```bash
# Windows
deploy.bat

# Linux/Mac
./deploy.sh
```

### Manual deployment:
```bash
# Streamlit Cloud (just push to GitHub)
git add .
git commit -m "Ready for deployment"
git push origin main

# Then go to share.streamlit.io
```

---

## 🎉 Success!

Once deployed, your app will be available at:
- **Streamlit Cloud**: `https://your-app-name.streamlit.app`
- **Railway**: `https://your-app-name.railway.app`
- **Heroku**: `https://your-app-name.herokuapp.com`

**Share your app URL and start processing medical conversations!** 🏥✨ 