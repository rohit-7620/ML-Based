# 🚀 Deployment Guide - ML-Based LMS Intelligence Platform

## Quick Start

### Option 1: Run the Web Application (Recommended)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train and save models (if not already done)
python run_pipeline_with_persistence.py

# 3. Start the web application
python web_app.py

# 4. Open your browser
# Navigate to: http://localhost:5000
```

### Option 2: Run API Service Only

```bash
# Start the enhanced API service
python api_service_enhanced.py

# Access at: http://localhost:5000
# Use tools like Postman or the test script
```

---

## 📁 Project Structure

```
kpmg/
├── Data/
│   ├── dataset 1/          # Grading data
│   └── dataset 2/          # Query/triage data
├── models/                 # Saved trained models (auto-created)
│   ├── grading/
│   │   ├── baseline_model.pkl
│   │   ├── advanced_model.pkl
│   │   ├── scaler.pkl
│   │   ├── label_encoder.pkl
│   │   └── metadata.json
│   └── triage/
│       ├── classifier.pkl
│       ├── vectorizer.pkl
│       ├── label_encoder.pkl
│       ├── department_encoder.pkl
│       └── metadata.json
├── static/                 # Web assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── templates/              # HTML templates
│   └── index.html
├── ml_pipeline.py          # Core ML pipeline
├── model_persistence.py    # Model saving/loading
├── web_app.py             # Web application (Flask)
├── api_service_enhanced.py # API service
├── run_pipeline_with_persistence.py  # Training script
└── requirements.txt        # Dependencies
```

---

## 🎯 Features

### 1. Grade Prediction
- **Input:** 7 academic performance metrics
- **Output:** Predicted grade (A, B, C, D) with confidence score
- **Features:**
  - Baseline (Logistic Regression) + Advanced (GradientBoosting) models
  - Automatic model selection based on confidence
  - Engineered features: engagement score, consistency, trend
  - Confidence-based routing (auto-approve vs teacher review)

### 2. Doubt Triage
- **Input:** Student query text, department, deadline
- **Output:** Priority classification (High, Medium, Low) with routing
- **Features:**
  - Text classification with TF-IDF vectorization
  - Engineered features: urgency detection, technical keywords
  - Confidence-based routing
  - Multi-class probability distribution

### 3. Batch Processing
- **Input:** CSV file with multiple students
- **Output:** Bulk grade predictions
- **Features:**
  - Process multiple students simultaneously
  - Export results for further analysis

### 4. Model Information
- View model metadata, performance metrics
- Training timestamps, feature lists
- Performance statistics

---

## 🖥️ Web Interface Guide

### Homepage (http://localhost:5000)

#### Tab 1: Grade Prediction
1. Enter student metrics (attendance, scores, GPA, etc.)
2. Use "Quick Fill" buttons for example data
3. Click "Predict Grade"
4. View:
   - Predicted grade with confidence
   - Model used (Baseline/Advanced)
   - Routing decision
   - Engineered features

#### Tab 2: Doubt Triage
1. Enter student query text
2. Select department
3. Enter days to deadline
4. Click "Analyze & Triage"
5. View:
   - Priority classification
   - Confidence score
   - Routing decision
   - Feature analysis
   - Priority probabilities

#### Tab 3: Batch Processing
1. Paste CSV data (format provided)
2. Click "Process Batch"
3. View results for all students

#### Tab 4: Model Info
- View comprehensive model information
- Performance metrics
- Training timestamps

---

## 🔧 API Endpoints

### 1. Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "timestamp": "2026-08-04T..."
}
```

### 2. Grade Prediction
```bash
POST /predict/grade
Content-Type: application/json

{
  "attendance_percentage": 85.0,
  "quiz_average": 78.5,
  "assignment_average": 82.0,
  "midterm_score": 76.0,
  "participation_score": 8.5,
  "study_hours_per_week": 15.0,
  "previous_gpa": 3.2
}
```

**Response:**
```json
{
  "predicted_grade": "B",
  "confidence_score": 0.8234,
  "model_used": "Baseline",
  "auto_approve": true,
  "routing_decision": "auto_approve",
  "engineered_features": {...},
  "timestamp": "..."
}
```

### 3. Doubt Triage
```bash
POST /predict/triage
Content-Type: application/json

{
  "student_query": "I cannot download my hall ticket",
  "department": "IT Support",
  "days_to_deadline": 2
}
```

**Response:**
```json
{
  "predicted_priority": "High",
  "confidence_score": 0.9156,
  "auto_approve": true,
  "routing_decision": "auto_route",
  "priority_probabilities": {...},
  "feature_analysis": {...},
  "timestamp": "..."
}
```

### 4. Batch Processing
```bash
POST /batch/grade
Content-Type: application/json

{
  "students": [
    {"attendance_percentage": 95, ...},
    {"attendance_percentage": 78, ...}
  ]
}
```

### 5. Model Info
```bash
GET /models/info
```

---

## 🧪 Testing

### Test the Web Application
```bash
# Start the web app
python web_app.py

# Open browser and test each feature
# http://localhost:5000
```

### Test the API
```bash
# In another terminal, run the test suite
python test_enhanced_api.py
```

---

## 📊 Model Training

### Initial Training
```bash
# Train both pipelines and save models
python run_pipeline_with_persistence.py --train
```

### Load and Test Saved Models
```bash
# Load models and run predictions
python run_pipeline_with_persistence.py --load
```

### Full Pipeline (Train + Test)
```bash
# Run complete pipeline
python run_pipeline_with_persistence.py --all
```

---

## 🔄 Model Retraining

Models can be retrained via:

### Option 1: Command Line
```bash
python run_pipeline_with_persistence.py --train
```

### Option 2: API Endpoint
```bash
POST /models/retrain
```

### Option 3: Programmatically
```python
from run_pipeline_with_persistence import train_and_save_models
train_and_save_models()
```

---

## 🐛 Troubleshooting

### Issue: Models not loading
**Solution:**
```bash
# Retrain models
python run_pipeline_with_persistence.py --train

# Restart web app
python web_app.py
```

### Issue: API returns 503
**Cause:** Models not initialized
**Solution:** Wait for models to load (check terminal logs) or retrain

### Issue: Port 5000 already in use
**Solution:**
```python
# Edit web_app.py, change last line:
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Issue: Missing dependencies
**Solution:**
```bash
pip install -r requirements.txt
```

---

## 🚀 Production Deployment

### 1. Using Gunicorn (Linux/Mac)
```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### 2. Using Waitress (Windows)
```bash
# Install waitress
pip install waitress

# Run server
waitress-serve --port=5000 web_app:app
```

### 3. Using Docker
```dockerfile
# Dockerfile
FROM python:3.9

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt
RUN python run_pipeline_with_persistence.py --train

EXPOSE 5000
CMD ["python", "web_app.py"]
```

```bash
# Build and run
docker build -t ml-lms-platform .
docker run -p 5000:5000 ml-lms-platform
```

### 4. Environment Variables
```bash
# For production, set:
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here

# Then run
python web_app.py
```

---

## 📈 Performance Monitoring

### Metrics to Track
1. **Prediction Latency:** Response time for predictions
2. **Model Accuracy:** Track accuracy over time
3. **Auto-approval Rate:** Percentage of auto-approved predictions
4. **API Uptime:** Service availability

### Logging
Add logging to track usage:
```python
import logging
logging.basicConfig(filename='app.log', level=logging.INFO)
```

---

## 🔐 Security Considerations

### For Production:
1. **Enable HTTPS:** Use SSL certificates
2. **Add Authentication:** Implement API keys or OAuth
3. **Rate Limiting:** Prevent API abuse
4. **Input Validation:** Already implemented
5. **CORS Configuration:** Adjust CORS settings as needed

### Example: Add API Key Authentication
```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != 'your-secret-key':
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/predict/grade', methods=['POST'])
@require_api_key
def predict_grade():
    # ... existing code
```

---

## 📚 Additional Resources

### Documentation
- Flask: https://flask.palletsprojects.com/
- scikit-learn: https://scikit-learn.org/
- Pandas: https://pandas.pydata.org/

### Support
- Check logs in terminal for error messages
- Review code comments for implementation details
- Test with example data first

---

## ✅ Deployment Checklist

- [ ] Install all dependencies (`pip install -r requirements.txt`)
- [ ] Train models (`python run_pipeline_with_persistence.py --train`)
- [ ] Verify models exist in `models/` directory
- [ ] Test locally (`python web_app.py`)
- [ ] Access web interface (http://localhost:5000)
- [ ] Test all features (grade, triage, batch)
- [ ] Run test suite (`python test_enhanced_api.py`)
- [ ] Configure production settings (if deploying)
- [ ] Set up monitoring and logging
- [ ] Enable security features (HTTPS, auth)

---

## 🎉 Success!

Your ML-Based LMS Intelligence Platform is now ready for use!

**Access the application at:** http://localhost:5000

**Need help?** Check the logs, review error messages, or retrain models if needed.

---

**Built with ❤️ for KPMG | 2026**
