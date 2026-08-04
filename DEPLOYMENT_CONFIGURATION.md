# Deployment Configuration Guide

This guide provides configuration files and instructions for deploying the ML-Based LMS Intelligence Platform to various cloud platforms.

## 📁 Deployment Files Created

### Core Entry Points
- `app.py` - Main entry point (many platforms look for this)
- `wsgi.py` - WSGI application entry point
- `web_app.py` - Original Flask application (can be used directly)

### Platform Configuration
- `Procfile` - Process configuration for Heroku, Railway, etc.
- `runtime.txt` - Python version specification
- `requirements.txt` - Updated with gunicorn for production

## 🚀 Platform-Specific Deployment

### 1. Heroku Deployment

```bash
# Install Heroku CLI and login
heroku login

# Create new app
heroku create your-ml-lms-platform

# Set environment variables (optional)
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Open app
heroku open
```

**Heroku will automatically:**
- Detect Python app
- Use `Procfile` for process configuration
- Install dependencies from `requirements.txt`
- Use `runtime.txt` for Python version
- Run: `gunicorn wsgi:application --bind 0.0.0.0:$PORT`

### 2. Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
railway init

# Deploy
railway up
```

**Railway Configuration:**
- Entry point: `wsgi:application`
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn wsgi:application --bind 0.0.0.0:$PORT`

### 3. Render Deployment

**Web Service Configuration:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn wsgi:application --bind 0.0.0.0:$PORT`
- **Environment:** `Python 3`

### 4. Google Cloud Run

```bash
# Build and deploy
gcloud run deploy ml-lms-platform \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

### 5. AWS Elastic Beanstalk

**Create `application.py`:**
```python
from wsgi import application

if __name__ == "__main__":
    application.run()
```

### 6. Azure App Service

**Startup Command:** `gunicorn --bind=0.0.0.0 --timeout 600 wsgi:application`

### 7. Vercel Deployment

Create `vercel.json`:
```json
{
  "builds": [
    {
      "src": "wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "wsgi.py"
    }
  ]
}
```

### 8. Digital Ocean App Platform

**App Spec Configuration:**
```yaml
name: ml-lms-platform
services:
- name: web
  source_dir: /
  github:
    repo: your-username/ML-Based-Grading-Doubt-Triage-Pipeline
    branch: main
  run_command: gunicorn wsgi:application --bind 0.0.0.0:$PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8080
```

## 🔧 Environment Variables

Set these environment variables on your deployment platform:

```bash
# Production settings
FLASK_ENV=production
PORT=8080  # or platform default

# Optional: Model configuration
CONFIDENCE_THRESHOLD_GRADING=0.7
CONFIDENCE_THRESHOLD_TRIAGE=0.5

# Optional: Security
SECRET_KEY=your-secret-key-here
```

## 🐛 Common Deployment Issues & Solutions

### Issue 1: "No Flask entrypoint found"
**Solution:** Use one of these entry points:
- `app.py` (most common)
- `wsgi.py` (WSGI standard)
- `web_app.py` (original)

### Issue 2: "Port already in use"
**Solution:** The app now reads PORT from environment variables

### Issue 3: "Module not found"
**Solution:** Ensure all dependencies are in `requirements.txt`

### Issue 4: "Models not loading"
**Solution:** Models are included in the repository. If issues persist, check file paths.

### Issue 5: "Static files not serving"
**Solution:** Flask handles static files automatically. For production, consider CDN.

## 📋 Pre-Deployment Checklist

- [ ] All dependencies listed in `requirements.txt`
- [ ] Environment variables configured
- [ ] Models are trained and saved
- [ ] Static files are accessible
- [ ] Database connections (if any) configured
- [ ] CORS settings appropriate for your domain
- [ ] Secret keys set for production
- [ ] Debug mode disabled in production

## 🎯 Recommended Entry Points by Platform

| Platform | Primary Entry | Alternative |
|----------|---------------|-------------|
| Heroku | `wsgi.py` | `app.py` |
| Railway | `app.py` | `wsgi.py` |
| Render | `wsgi.py` | `app.py` |
| Vercel | `wsgi.py` | `app.py` |
| Google Cloud Run | `app.py` | `wsgi.py` |
| AWS Elastic Beanstalk | `application.py` | `wsgi.py` |
| Azure App Service | `wsgi.py` | `app.py` |

## 🔍 Testing Deployment

After deployment, test these endpoints:
- `GET /` - Web interface
- `GET /health` - API health check
- `GET /models/info` - Model information
- `POST /predict/grade` - Grade prediction
- `POST /predict/triage` - Triage prediction

## 🚨 Production Recommendations

1. **Use gunicorn** instead of Flask development server
2. **Set FLASK_ENV=production** to disable debug mode
3. **Use environment variables** for configuration
4. **Monitor application** with logging and metrics
5. **Set up backup** for trained models
6. **Configure SSL/HTTPS** for production use
7. **Set up domain** and DNS properly
8. **Monitor resource usage** and scale as needed

## 📞 Deployment Support

If you encounter issues:
1. Check platform-specific logs
2. Verify all files are committed to git
3. Ensure requirements.txt includes all dependencies
4. Test locally first with `gunicorn wsgi:application`
5. Check environment variables are set correctly

---

**The platform is now deployment-ready with multiple entry points and comprehensive configuration!**