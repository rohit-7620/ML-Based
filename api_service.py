"""
Flask API Service for ML-Based Grading & Doubt Triage Pipeline
============================================================

Provides REST endpoints for:
1. Grade prediction with confidence scoring
2. Doubt triage classification and routing
3. Model performance metrics
"""

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import pickle
import joblib
from datetime import datetime
import os
from ml_pipeline import GradingPipeline, DoubtTriagePipeline

app = Flask(__name__)

# Global model containers
grading_model = None
triage_model = None
models_loaded = False

def load_models():
    """Load trained models (in production, load from saved files)"""
    global grading_model, triage_model, models_loaded
    
    try:
        # Initialize and train models (in production, load pre-trained models)
        print("Initializing ML models...")
        
        grading_model = GradingPipeline()
        triage_model = DoubtTriagePipeline()
        
        # Quick training for demo (in production, load saved models)
        grading_data = grading_model.load_and_explore_data()
        (X_train_scaled, X_val_scaled, X_test_scaled, 
         y_train, y_val, y_test, X_train, X_val, X_test) = grading_model.prepare_data()
        
        grading_model.train_baseline_model(X_train_scaled, y_train)
        grading_model.train_advanced_model(X_train_scaled, y_train, X_val_scaled, y_val)
        
        triage_data = triage_model.load_and_explore_data()
        triage_data = triage_model.feature_engineering()
        X_train_text, X_test_text, y_train_text, y_test_text = triage_model.prepare_text_data()
        triage_model.train_classifier(X_train_text, y_train_text)
        triage_model.confidence_analysis(X_test_text, y_test_text)
        
        models_loaded = True
        print("✅ Models loaded successfully")
        
    except Exception as e:
        print(f"❌ Error loading models: {str(e)}")
        models_loaded = False

@app.before_first_request
def initialize():
    """Initialize models before first request"""
    load_models()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': models_loaded,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict/grade', methods=['POST'])
def predict_grade():
    """
    Predict student grade based on academic features
    
    Expected input:
    {
        "attendance_percentage": 85.0,
        "quiz_average": 78.5,
        "assignment_average": 82.0,
        "midterm_score": 76.0,
        "participation_score": 8.5,
        "study_hours_per_week": 15.0,
        "previous_gpa": 3.2
    }
    """
    try:
        if not models_loaded:
            return jsonify({'error': 'Models not loaded'}), 500
        
        data = request.get_json()
        
        # Validate input
        required_features = [
            'attendance_percentage', 'quiz_average', 'assignment_average',
            'midterm_score', 'participation_score', 'study_hours_per_week', 'previous_gpa'
        ]
        
        for feature in required_features:
            if feature not in data:
                return jsonify({'error': f'Missing required feature: {feature}'}), 400
        
        # Create feature vector
        features = pd.DataFrame([data])
        
        # Feature engineering (same as training)
        features['engagement_score'] = (
            features['attendance_percentage'] * 0.4 + 
            features['participation_score'] * 10 * 0.6
        )
        features['academic_consistency'] = (
            features['quiz_average'] + features['assignment_average']
        ) / 2
        features['performance_trend'] = (
            features['midterm_score'] - features['academic_consistency']
        )
        
        # Scale features
        feature_vector = features[grading_model.feature_names]
        feature_scaled = grading_model.scaler.transform(feature_vector)
        
        # Get predictions from both models
        baseline_proba = grading_model.baseline_model.predict_proba(feature_scaled)[0]
        baseline_pred = grading_model.baseline_model.predict(feature_scaled)[0]
        
        advanced_proba = grading_model.advanced_model.predict_proba(feature_scaled)[0]
        advanced_pred = grading_model.advanced_model.predict(feature_scaled)[0]
        
        # Convert predictions to grade labels
        baseline_grade = grading_model.label_encoder.inverse_transform([baseline_pred])[0]
        advanced_grade = grading_model.label_encoder.inverse_transform([advanced_pred])[0]
        
        # Calculate confidence scores
        baseline_confidence = np.max(baseline_proba)
        advanced_confidence = np.max(advanced_proba)
        
        # Choose best model prediction (based on confidence)
        if advanced_confidence > baseline_confidence:
            final_grade = advanced_grade
            final_confidence = advanced_confidence
            model_used = "GradientBoosting"
        else:
            final_grade = baseline_grade
            final_confidence = baseline_confidence
            model_used = "Baseline"
        
        # Routing decision
        confidence_threshold = 0.7
        auto_approve = final_confidence >= confidence_threshold
        
        return jsonify({
            'predicted_grade': final_grade,
            'confidence_score': float(final_confidence),
            'model_used': model_used,
            'auto_approve': auto_approve,
            'routing_decision': 'auto_approve' if auto_approve else 'teacher_review',
            'model_predictions': {
                'baseline': {
                    'grade': baseline_grade,
                    'confidence': float(baseline_confidence),
                    'probabilities': baseline_proba.tolist()
                },
                'advanced': {
                    'grade': advanced_grade,
                    'confidence': float(advanced_confidence),
                    'probabilities': advanced_proba.tolist()
                }
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict/triage', methods=['POST'])
def predict_triage():
    """
    Triage student doubt/query based on text content and context
    
    Expected input:
    {
        "student_query": "I cannot download my hall ticket for tomorrow's exam",
        "department": "IT Support",
        "days_to_deadline": 2
    }
    """
    try:
        if not models_loaded:
            return jsonify({'error': 'Models not loaded'}), 500
        
        data = request.get_json()
        
        # Validate input
        required_fields = ['student_query', 'department', 'days_to_deadline']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create feature vector
        query_data = pd.DataFrame([{
            'Student_Query': data['student_query'],
            'Department': data['department'],
            'Days_To_Deadline': data['days_to_deadline']
        }])
        
        # Feature engineering (same as training)
        query_data['query_word_count'] = query_data['Student_Query'].str.split().str.len()
        query_data['has_urgent_words'] = query_data['Student_Query'].str.contains(
            'urgent|emergency|tomorrow|today|asap|immediately', case=False
        ).astype(int)
        query_data['has_technical_words'] = query_data['Student_Query'].str.contains(
            'portal|password|login|download|upload|system|error', case=False
        ).astype(int)
        
        # Deadline urgency feature
        query_data['urgency_score'] = pd.cut(
            query_data['Days_To_Deadline'], 
            bins=[0, 3, 7, 30, float('inf')], 
            labels=[3, 2, 1, 0]
        ).astype(int)
        
        # Department encoding
        try:
            dept_encoded = triage_model.department_encoder.transform([data['department']])[0]
        except ValueError:
            # Handle unseen department
            dept_encoded = 0
        query_data['department_encoded'] = dept_encoded
        
        # Vectorize text
        text_features = triage_model.vectorizer.transform(query_data['Student_Query'])
        
        # Combine features
        engineered_features = query_data[['query_word_count', 'has_urgent_words', 
                                        'has_technical_words', 'urgency_score', 'department_encoded']]
        
        from scipy.sparse import hstack
        combined_features = hstack([text_features, engineered_features.values])
        
        # Get prediction
        prediction_proba = triage_model.classifier.predict_proba(combined_features)[0]
        prediction = triage_model.classifier.predict(combined_features)[0]
        
        # Convert to label
        predicted_priority = triage_model.label_encoder.inverse_transform([prediction])[0]
        
        # Calculate confidence
        confidence_score = np.max(prediction_proba)
        
        # Routing decision
        auto_approve = confidence_score >= triage_model.confidence_threshold
        
        # Priority probabilities
        priority_probs = {
            label: float(prob) for label, prob in 
            zip(triage_model.label_encoder.classes_, prediction_proba)
        }
        
        return jsonify({
            'predicted_priority': predicted_priority,
            'confidence_score': float(confidence_score),
            'auto_approve': auto_approve,
            'routing_decision': 'auto_route' if auto_approve else 'human_review',
            'priority_probabilities': priority_probs,
            'feature_analysis': {
                'query_length': int(query_data['query_word_count'].iloc[0]),
                'has_urgent_keywords': bool(query_data['has_urgent_words'].iloc[0]),
                'has_technical_keywords': bool(query_data['has_technical_words'].iloc[0]),
                'urgency_from_deadline': int(query_data['urgency_score'].iloc[0]),
                'department_encoded': int(dept_encoded)
            },
            'confidence_threshold': triage_model.confidence_threshold,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/models/performance', methods=['GET'])
def get_model_performance():
    """Get model performance metrics"""
    try:
        if not models_loaded:
            return jsonify({'error': 'Models not loaded'}), 500
        
        # In production, these metrics would be stored from training
        return jsonify({
            'grading_pipeline': {
                'baseline_model': 'LogisticRegression',
                'advanced_model': 'GradientBoosting',
                'features_count': len(grading_model.feature_names),
                'confidence_threshold': 0.7
            },
            'triage_pipeline': {
                'model_type': type(triage_model.classifier).__name__,
                'text_features': triage_model.vectorizer.max_features,
                'confidence_threshold': triage_model.confidence_threshold,
                'priority_classes': triage_model.label_encoder.classes_.tolist()
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/models/retrain', methods=['POST'])
def retrain_models():
    """Trigger model retraining (for production use)"""
    try:
        # In production, this would trigger retraining pipeline
        load_models()  # For demo, just reload
        
        return jsonify({
            'status': 'success',
            'message': 'Models retrained successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting ML Pipeline API Service...")
    print("Endpoints available:")
    print("  GET  /health - Health check")
    print("  POST /predict/grade - Grade prediction")
    print("  POST /predict/triage - Doubt triage")
    print("  GET  /models/performance - Model metrics")
    print("  POST /models/retrain - Retrain models")
    
    app.run(debug=True, host='0.0.0.0', port=5000)