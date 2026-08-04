"""
Web Application for ML Pipeline Deployment
==========================================

Flask web application that serves the ML models through a beautiful web interface
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
from model_persistence import load_all_models, ModelPersistence
from ml_pipeline import GradingPipeline, DoubtTriagePipeline
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# Global model containers
grading_model = None
triage_model = None
models_loaded = False
model_metadata = {}

def initialize_models():
    """Load models from disk"""
    global grading_model, triage_model, models_loaded, model_metadata
    
    try:
        persistence = ModelPersistence()
        
        # Check if models exist
        if not persistence.model_exists('grading') or not persistence.model_exists('triage'):
            print("⚠️  No saved models found. Training new models...")
            from run_pipeline_with_persistence import train_and_save_models
            train_and_save_models()
        
        # Load models
        print("Loading pre-trained models...")
        grading_model, triage_model, model_metadata = load_all_models()
        models_loaded = True
        
        print("✅ Models loaded successfully from disk")
        
    except Exception as e:
        print(f"❌ Error loading models: {str(e)}")
        print("Attempting to train new models...")
        try:
            from run_pipeline_with_persistence import train_and_save_models
            train_and_save_models()
            grading_model, triage_model, model_metadata = load_all_models()
            models_loaded = True
        except Exception as e2:
            print(f"❌ Failed to train models: {str(e2)}")
            models_loaded = False

# Initialize models on startup
with app.app_context():
    initialize_models()

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/documentation')
def documentation():
    """Serve the documentation page"""
    return render_template('documentation.html')

@app.route('/about')
def about():
    """Serve the about page"""
    return render_template('about.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if models_loaded else 'initializing',
        'models_loaded': models_loaded,
        'timestamp': datetime.now().isoformat(),
        'model_info': {
            'grading': model_metadata.get('grading', {}).get('saved_at'),
            'triage': model_metadata.get('triage', {}).get('saved_at')
        } if models_loaded else None
    })

@app.route('/predict/grade', methods=['POST'])
def predict_grade():
    """
    Predict student grade based on academic features
    """
    try:
        if not models_loaded:
            return jsonify({'error': 'Models not loaded. Please wait for initialization.'}), 503
        
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
        confidence_threshold = grading_model.confidence_threshold
        auto_approve = final_confidence >= confidence_threshold
        
        return jsonify({
            'predicted_grade': str(final_grade),
            'confidence_score': float(final_confidence),
            'model_used': str(model_used),
            'auto_approve': bool(auto_approve),
            'routing_decision': 'auto_approve' if auto_approve else 'teacher_review',
            'model_predictions': {
                'baseline': {
                    'grade': str(baseline_grade),
                    'confidence': float(baseline_confidence),
                    'probabilities': {
                        str(grade): float(prob) for grade, prob in 
                        zip(grading_model.label_encoder.classes_, baseline_proba)
                    }
                },
                'advanced': {
                    'grade': str(advanced_grade),
                    'confidence': float(advanced_confidence),
                    'probabilities': {
                        str(grade): float(prob) for grade, prob in 
                        zip(grading_model.label_encoder.classes_, advanced_proba)
                    }
                }
            },
            'engineered_features': {
                'engagement_score': float(features['engagement_score'].iloc[0]),
                'academic_consistency': float(features['academic_consistency'].iloc[0]),
                'performance_trend': float(features['performance_trend'].iloc[0])
            },
            'confidence_threshold': float(confidence_threshold),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500

@app.route('/predict/triage', methods=['POST'])
def predict_triage():
    """
    Triage student doubt/query based on text content and context
    """
    try:
        if not models_loaded:
            return jsonify({'error': 'Models not loaded. Please wait for initialization.'}), 503
        
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
            print(f"⚠️  Unknown department: {data['department']}, using default encoding")
            
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
            'predicted_priority': str(predicted_priority),
            'confidence_score': float(confidence_score),
            'auto_approve': bool(auto_approve),
            'routing_decision': 'auto_route' if auto_approve else 'human_review',
            'priority_probabilities': priority_probs,
            'feature_analysis': {
                'query_length': int(query_data['query_word_count'].iloc[0]),
                'has_urgent_keywords': bool(int(query_data['has_urgent_words'].iloc[0])),
                'has_technical_keywords': bool(int(query_data['has_technical_words'].iloc[0])),
                'urgency_from_deadline': int(query_data['urgency_score'].iloc[0]),
                'department': str(data['department']),
                'department_encoded': int(dept_encoded)
            },
            'confidence_threshold': float(triage_model.confidence_threshold),
            'model_info': {
                'classifier': model_metadata.get('triage', {}).get('classifier_type'),
                'trained_at': model_metadata.get('triage', {}).get('saved_at')
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500

@app.route('/models/info', methods=['GET'])
def get_model_info():
    """Get comprehensive model information"""
    try:
        if not models_loaded:
            return jsonify({'error': 'Models not loaded'}), 503
        
        return jsonify({
            'grading_pipeline': {
                'saved_at': model_metadata['grading']['saved_at'],
                'baseline_model': model_metadata['grading']['model_types']['baseline'],
                'advanced_model': model_metadata['grading']['model_types']['advanced'],
                'features': model_metadata['grading']['feature_names'],
                'classes': model_metadata['grading']['classes'],
                'confidence_threshold': model_metadata['grading']['confidence_threshold'],
                'performance': model_metadata['grading'].get('performance', {})
            },
            'triage_pipeline': {
                'saved_at': model_metadata['triage']['saved_at'],
                'classifier': model_metadata['triage']['classifier_type'],
                'classes': model_metadata['triage']['classes'],
                'departments': model_metadata['triage']['departments'],
                'confidence_threshold': model_metadata['triage']['confidence_threshold'],
                'vectorizer_params': model_metadata['triage']['vectorizer_params'],
                'performance': model_metadata['triage'].get('performance', {})
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch/grade', methods=['POST'])
def batch_grade_prediction():
    """
    Batch grade prediction for multiple students
    """
    try:
        if not models_loaded:
            return jsonify({'error': 'Models not loaded'}), 503
        
        data = request.get_json()
        
        if 'students' not in data or not isinstance(data['students'], list):
            return jsonify({'error': 'Expected "students" array in request'}), 400
        
        results = []
        for idx, student_data in enumerate(data['students']):
            try:
                # Process each student
                features = pd.DataFrame([student_data])
                
                # Feature engineering
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
                
                # Predict
                feature_vector = features[grading_model.feature_names]
                feature_scaled = grading_model.scaler.transform(feature_vector)
                
                baseline_pred = grading_model.baseline_model.predict(feature_scaled)[0]
                baseline_proba = grading_model.baseline_model.predict_proba(feature_scaled)[0]
                
                grade = grading_model.label_encoder.inverse_transform([baseline_pred])[0]
                confidence = np.max(baseline_proba)
                
                results.append({
                    'student_index': int(idx),
                    'predicted_grade': str(grade),
                    'confidence': float(confidence),
                    'auto_approve': bool(confidence >= grading_model.confidence_threshold)
                })
                
            except Exception as e:
                results.append({
                    'student_index': int(idx),
                    'error': str(e)
                })
        
        return jsonify({
            'batch_results': results,
            'total_students': len(data['students']),
            'successful_predictions': sum(1 for r in results if 'predicted_grade' in r),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    
    print("=" * 70)
    print("🚀 ML-Based LMS Intelligence Platform - Web Application")
    print("=" * 70)
    print("\n🌐 Starting web server...")
    
    # Get port from environment (for deployment platforms) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"📍 Access the application at: http://localhost:{port}")
    print("\nAvailable Endpoints:")
    print("  🏠 GET  /                  - Web Interface")
    print("  💚 GET  /health            - Health Check")
    print("  📊 POST /predict/grade     - Grade Prediction")
    print("  💬 POST /predict/triage    - Doubt Triage")
    print("  📦 POST /batch/grade       - Batch Processing")
    print("  ℹ️  GET  /models/info      - Model Information")
    print("\n" + "=" * 70)
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
