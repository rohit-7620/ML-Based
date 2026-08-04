# ML-Based Grading & Doubt Triage Pipeline

A comprehensive machine learning pipeline for Learning Management Systems (LMS) that provides:

1. **Automated Grade Prediction** - Predicts code submission quality using engineered features
2. **Intelligent Doubt Triage** - Classifies and routes student queries with confidence scoring
3. **Confidence-Based Routing** - Automated approval vs teacher review decisions

## 🎯 Objectives

- Build robust ML models for educational data
- Implement sound modeling practices with proper validation
- Handle class imbalance and prevent data leakage
- Provide confidence-based routing for automated decisions
- Deliver production-ready API endpoints

## 📊 Datasets

### Dataset 1: Student Grading Data (Tabular)
- **Features**: Attendance, quiz scores, assignments, participation, study hours, GPA
- **Target**: Grade classification (A, B, C, D)
- **Models**: Baseline Logistic Regression + LightGBM
- **Focus**: Feature engineering, cross-validation, overfitting prevention

### Dataset 2: University Query Data (Text)
- **Features**: Student queries, department, days to deadline
- **Target**: Priority classification (High, Medium, Low)
- **Models**: Text classification with TF-IDF + engineered features
- **Focus**: Confidence scoring, routing decisions

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Main Pipeline

```bash
# Execute the complete ML pipeline
python ml_pipeline.py
```

### 3. Start API Service

```bash
# Start Flask API server
python api_service.py
```

### 4. Test the API

```bash
# Run API tests
python test_api.py
```

## 🏗️ Architecture

### Core Components

1. **GradingPipeline Class**
   - Data exploration and leakage detection
   - Feature engineering for tabular data
   - Baseline vs advanced model comparison
   - Cross-validated training and evaluation

2. **DoubtTriagePipeline Class**
   - Text preprocessing and feature extraction
   - Confidence score calculation
   - Threshold optimization for routing
   - Multi-class text classification

3. **API Service (Flask)**
   - RESTful endpoints for predictions
   - Real-time model serving
   - Health monitoring and metrics

### Key Features

- **Data Leakage Detection**: Automated correlation analysis
- **Class Imbalance Handling**: Stratified sampling and evaluation
- **Cross-Validation**: Rigorous model validation with StratifiedKFold
- **Feature Engineering**: Domain-specific feature creation
- **Confidence Scoring**: Probabilistic predictions for routing
- **Threshold Optimization**: Data-driven confidence threshold selection

## 📡 API Endpoints

### Grade Prediction
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
  "model_used": "LightGBM",
  "auto_approve": true,
  "routing_decision": "auto_approve"
}
```

### Doubt Triage
```bash
POST /predict/triage
Content-Type: application/json

{
  "student_query": "I cannot download my hall ticket for tomorrow's exam",
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
  "priority_probabilities": {
    "High": 0.9156,
    "Medium": 0.0721,
    "Low": 0.0123
  }
}
```

## 🔍 Model Evaluation

### Grading Pipeline Metrics
- **Baseline Model**: Logistic Regression with cross-validation
- **Advanced Model**: LightGBM with early stopping
- **Evaluation**: Accuracy, F1-score, classification report
- **Validation**: 5-fold stratified cross-validation

### Triage Pipeline Metrics
- **Text Features**: TF-IDF vectorization (1000 features)
- **Engineered Features**: Urgency keywords, deadline proximity
- **Confidence Analysis**: Threshold optimization for routing
- **Performance**: Precision, recall, F1-score per class

## 🎛️ Configuration

### Confidence Thresholds
- **Grading Pipeline**: 0.70 (configurable)
- **Triage Pipeline**: Auto-optimized based on validation data

### Model Parameters
- **LightGBM**: Early stopping, 31 leaves, 0.05 learning rate
- **Text Classification**: TF-IDF max 1000 features, English stop words
- **Cross-Validation**: 5-fold stratified, balanced sampling

## 📈 Performance Monitoring

### Key Metrics Tracked
- Model accuracy and F1-scores
- Confidence score distributions
- Auto-approval vs review ratios
- Class-wise performance metrics
- Feature importance analysis

### Production Considerations
- Model drift detection
- A/B testing framework
- Performance degradation alerts
- Automated retraining triggers

## 🛡️ Data Safety & Ethics

### Data Leakage Prevention
- Temporal feature analysis
- Correlation matrix examination
- Feature dependency validation
- Cross-validation integrity checks

### Class Imbalance Mitigation
- Stratified sampling throughout pipeline
- Weighted metrics for evaluation
- Balanced validation sets
- Performance monitoring per class

### Bias Detection
- Feature importance analysis
- Subgroup performance evaluation
- Confidence score fairness assessment
- Regular model auditing

## 🔧 Development

### Project Structure
```
├── ml_pipeline.py          # Main ML pipeline implementation
├── api_service.py          # Flask API service
├── test_api.py            # API testing suite
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
└── Data/                 # Dataset directory
    ├── dataset 1/        # Grading data
    └── dataset 2/        # Query data
```

### Testing Strategy
- Unit tests for data processing
- Integration tests for API endpoints
- Model performance benchmarks
- Cross-validation robustness checks

## 📋 Usage Examples

### Batch Grade Prediction
```python
from ml_pipeline import GradingPipeline

# Initialize pipeline
pipeline = GradingPipeline()
pipeline.load_and_explore_data()

# Train models
pipeline.prepare_data()
pipeline.train_baseline_model(X_train, y_train)
pipeline.train_lgb_model(X_train, y_train, X_val, y_val)

# Evaluate
results = pipeline.evaluate_models(X_test, y_test)
```

### Confidence-Based Routing
```python
from ml_pipeline import DoubtTriagePipeline

# Initialize triage system
triage = DoubtTriagePipeline()
triage.load_and_explore_data()

# Optimize threshold
optimal_threshold = triage.confidence_analysis(X_test, y_test)

# Simulate routing
routing_results = triage.routing_simulation(X_test, y_test)
```

## 🚨 Monitoring & Alerts

### Model Health Checks
- Daily accuracy monitoring
- Confidence score distribution tracking
- Class balance drift detection
- Feature importance stability

### Performance Degradation
- Automated threshold for accuracy drops
- Confidence score distribution shifts
- Unusual prediction patterns
- Data quality anomalies

## 🔮 Future Enhancements

### Technical Improvements
- Deep learning models for text classification
- Ensemble methods for improved accuracy
- Real-time model updates
- Advanced feature engineering

### Business Features
- Multi-language support for queries
- Personalized confidence thresholds
- Integration with existing LMS systems
- Advanced analytics dashboard

## 📞 Support

For technical issues or questions:
1. Check the API health endpoint: `GET /health`
2. Review model performance: `GET /models/performance`
3. Validate input data format
4. Check server logs for detailed error messages


**Built by Rohit Salke**
