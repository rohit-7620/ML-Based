# 🔧 Deployment Troubleshooting Guide

## Common Deployment Errors & Solutions

### ❌ Error 1: "No module named 'distutils'"

**Full Error:**
```
ModuleNotFoundError: No module named 'distutils'
hint: `distutils` was removed from the standard library in Python 3.12
```

**Cause:** Python 3.12 removed `distutils`, old numpy versions (<1.24) depend on it

**✅ Solution:**
1. Updated Python version to 3.11 (in `runtime.txt`)
2. Updated numpy to >=1.24.0 (Python 3.12 compatible)
3. Updated all dependencies to latest stable versions

**Files Changed:**
- `runtime.txt`: `python-3.11.7`
- `requirements.txt`: numpy>=1.24.0
- `Dockerfile`: Python 3.11-slim

---

### ❌ Error 2: "Bundle size exceeds 500 MB"

**Full Error:**
```
Total bundle size (6968.59 MB) exceeds the maximum function size (500 MB)
```

**Cause:** TensorFlow (~2.5GB) and PyTorch (~4GB) dependencies

**✅ Solution:**
1. Removed TensorFlow (not needed - models use scikit-learn)
2. Removed PyTorch (not needed - models use scikit-learn)
3. Removed development dependencies (matplotlib, jupyter, pytest)
4. Added `.slugignore`, `.vercelignore`, `.dockerignore`

**Bundle Size:** Reduced from 7GB → 261MB ✅

---

### ❌ Error 3: "Multiple Flask entrypoints found"

**Full Error:**
```
No Flask entrypoint found in default locations, but found potential entrypoints:
api_service.py (variable: app)
api_service_enhanced.py (variable: app)
web_app.py (variable: app)
```

**Cause:** Multiple Flask apps in the repository

**✅ Solution:**
1. Moved legacy API files to `backup_apis/`
2. Created clear entry points: `wsgi.py` and `app.py`
3. Both import from `web_app.py` (single source of truth)
4. Updated `Procfile` to use `wsgi:application`

---

### ❌ Error 4: "Port already in use"

**Error:**
```
OSError: [Errno 98] Address already in use
```

**✅ Solution:**
Updated `web_app.py` to read PORT from environment:
```python
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

---

### ❌ Error 5: "Models not loading"

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/grading/...'
```

**✅ Solution:**
1. Ensure models are committed to git
2. Check `.gitignore` doesn't exclude `.pkl` files
3. Verify model paths are relative, not absolute
4. Run training before deployment if needed:
```bash
python run_pipeline_with_persistence.py --train
```

---

## Platform-Specific Issues

### Vercel

**Issue:** Function timeout
**Solution:** Add to `vercel.json`:
```json
{
  "functions": {
    "wsgi.py": {
      "maxDuration": 60
    }
  }
}
```

**Issue:** Cold start takes too long
**Solution:** Use Vercel Pro for faster cold starts, or switch to Railway/Render

---

### Heroku

**Issue:** Slug size too large
**Solution:** Use `.slugignore` to exclude:
- Documentation files
- Test files
- Development notebooks
- Backup folders

**Issue:** Memory limit exceeded
**Solution:** Upgrade dyno type:
```bash
heroku ps:scale web=1:standard-1x
```

---

### Railway

**Issue:** Build timeout
**Solution:** Railway has generous limits (8GB RAM), should work fine

**Issue:** Environment variables not set
**Solution:**
```bash
railway variables set FLASK_ENV=production
railway variables set PORT=8080
```

---

### AWS Lambda

**Issue:** Deployment package too large
**Solution:** Use Lambda Layers for dependencies:
```bash
mkdir python
pip install -r requirements.txt -t python/
zip -r layer.zip python/
aws lambda publish-layer-version --layer-name ml-deps --zip-file fileb://layer.zip
```

---

### Google Cloud Run

**Issue:** Container build fails
**Solution:** Use provided `Dockerfile` and build:
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/ml-lms
gcloud run deploy --image gcr.io/PROJECT-ID/ml-lms --platform managed
```

---

## Pre-Deployment Checklist

- [ ] Python version: 3.11+ (check `runtime.txt`)
- [ ] Dependencies optimized (no TensorFlow/PyTorch)
- [ ] Bundle size < 500 MB (check with `du -sh .`)
- [ ] Single Flask entrypoint (`wsgi.py`)
- [ ] Environment variables configured
- [ ] Models trained and saved
- [ ] `.gitignore` configured properly
- [ ] Platform-specific ignore files added
- [ ] Gunicorn in requirements.txt
- [ ] Port reads from environment variable

---

## Testing Before Deployment

### 1. Test locally with production setup:
```bash
# Install production requirements
pip install -r requirements.txt

# Test with gunicorn (production server)
gunicorn wsgi:application --bind 0.0.0.0:5000

# Visit http://localhost:5000
```

### 2. Check bundle size:
```bash
# Total size
du -sh .

# Dependencies size
pip install -r requirements.txt --target ./temp
du -sh temp
rm -rf temp
```

### 3. Verify entry points:
```bash
# Should all work
python app.py
python web_app.py
gunicorn wsgi:application --bind 0.0.0.0:5000
```

### 4. Test API endpoints:
```bash
# Health check
curl http://localhost:5000/health

# Grade prediction
curl -X POST http://localhost:5000/predict/grade \
  -H "Content-Type: application/json" \
  -d '{"attendance_percentage": 85, "quiz_average": 78.5, ...}'
```

---

## Quick Fixes

### If deployment fails:

1. **Check logs first:**
```bash
# Heroku
heroku logs --tail

# Vercel
vercel logs

# Railway
railway logs
```

2. **Verify requirements:**
```bash
pip install -r requirements.txt
# Should complete without errors
```

3. **Test entry point:**
```bash
python -c "from wsgi import application; print('OK')"
```

4. **Check file sizes:**
```bash
find . -type f -size +10M
# Should return nothing (or only data files)
```

5. **Verify Python version:**
```bash
python --version
# Should be 3.11+
```

---

## Platform Recommendations

| Platform | Best For | Size Limit | Cost |
|----------|----------|------------|------|
| **Railway** | Full apps | 2 GB | $5/mo |
| **Render** | Full apps | 2 GB | Free tier |
| **Heroku** | Traditional apps | 500 MB | Free tier |
| **Vercel** | Serverless | 500 MB | Free tier |
| **Google Cloud Run** | Containers | 10 GB | Pay per use |
| **AWS Lambda** | Serverless | 250 MB | Pay per use |

**Recommendation:** Start with **Railway** or **Render** (easiest, most forgiving)

---

## Still Having Issues?

1. Check platform-specific documentation
2. Verify all environment variables are set
3. Test locally first with production configuration
4. Check platform status page for outages
5. Review deployment logs carefully
6. Try a different platform (Railway is most reliable)

---

## Success Indicators

✅ Build completes without errors
✅ Health endpoint returns 200 OK
✅ Models load successfully
✅ API endpoints respond correctly
✅ No memory/timeout errors
✅ Cold start < 10 seconds

---

**Your deployment should now work! 🚀**

**Current Configuration:**
- Python: 3.11.7
- Bundle Size: ~261 MB
- Entry Point: wsgi:application
- Dependencies: Optimized (no deep learning frameworks)
- Platform: Compatible with all major platforms