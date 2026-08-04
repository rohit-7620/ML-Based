"""
Enhanced ML Pipeline with Model Persistence
==========================================

Runs the complete pipeline and saves trained models for production use
"""

from ml_pipeline import GradingPipeline, DoubtTriagePipeline
from model_persistence import save_all_models, load_all_models, ModelPersistence
import argparse


def train_and_save_models():
    """Train both pipelines and save models"""
    print("🚀 ML-Based Grading & Doubt Triage Pipeline (with Persistence)")
    print("=" * 70)
    
    # Initialize pipelines
    grading_pipeline = GradingPipeline()
    triage_pipeline = DoubtTriagePipeline()
    
    # === GRADING PIPELINE ===
    print("\n🎯 PART 1: GRADING PREDICTION PIPELINE")
    
    # Load and explore grading data
    grading_data = grading_pipeline.load_and_explore_data()
    
    # Data leakage detection
    grading_pipeline.detect_data_leakage()
    
    # Prepare data
    (X_train_scaled, X_val_scaled, X_test_scaled, 
     y_train, y_val, y_test, X_train, X_val, X_test) = grading_pipeline.prepare_data()
    
    # Train models
    baseline_model = grading_pipeline.train_baseline_model(X_train_scaled, y_train)
    advanced_model = grading_pipeline.train_advanced_model(X_train_scaled, y_train, X_val_scaled, y_val)
    
    # Evaluate models
    grading_results = grading_pipeline.evaluate_models(X_test_scaled, y_test)
    
    # === DOUBT TRIAGE PIPELINE ===
    print("\n🎯 PART 2: DOUBT TRIAGE PIPELINE")
    
    # Load and explore text data
    triage_data = triage_pipeline.load_and_explore_data()
    
    # Feature engineering
    triage_data = triage_pipeline.feature_engineering()
    
    # Prepare text data
    X_train_text, X_test_text, y_train_text, y_test_text = triage_pipeline.prepare_text_data()
    
    # Train classifier
    text_classifier = triage_pipeline.train_classifier(X_train_text, y_train_text)
    
    # Confidence analysis and threshold tuning
    optimal_threshold, threshold_metrics, confidence_scores = triage_pipeline.confidence_analysis(
        X_test_text, y_test_text
    )
    
    # Routing simulation
    routing_results = triage_pipeline.routing_simulation(X_test_text, y_test_text)
    
    # === SAVE MODELS ===
    performance_metrics = {
        'grading': {
            'baseline_accuracy': grading_results['baseline']['accuracy'],
            'baseline_f1': grading_results['baseline']['f1'],
            'advanced_accuracy': grading_results['advanced']['accuracy'],
            'advanced_f1': grading_results['advanced']['f1'],
            'test_samples': len(y_test)
        },
        'triage': {
            'accuracy': routing_results['auto_accuracy'] if routing_results['auto_accuracy'] else 1.0,
            'auto_approval_rate': routing_results['auto_samples'] / (routing_results['auto_samples'] + routing_results['review_samples']),
            'optimal_threshold': optimal_threshold,
            'test_samples': len(y_test_text)
        }
    }
    
    save_all_models(grading_pipeline, triage_pipeline, performance_metrics)
    
    # === SUMMARY REPORT ===
    print("\n" + "="*70)
    print("📊 PIPELINE SUMMARY REPORT")
    print("="*70)
    
    print("\n🎯 Grading Pipeline Results:")
    print(f"  Best Model: {'Advanced' if grading_results['advanced']['f1'] > grading_results['baseline']['f1'] else 'Baseline'}")
    print(f"  Best F1-Score: {max(grading_results['advanced']['f1'], grading_results['baseline']['f1']):.4f}")
    print(f"  Best Accuracy: {max(grading_results['advanced']['accuracy'], grading_results['baseline']['accuracy']):.4f}")
    
    print("\n🎯 Doubt Triage Results:")
    print(f"  Optimal Confidence Threshold: {optimal_threshold:.3f}")
    print(f"  Auto-approval Rate: {routing_results['auto_samples']}/{routing_results['auto_samples'] + routing_results['review_samples']} ({routing_results['auto_samples']/(routing_results['auto_samples'] + routing_results['review_samples'])*100:.1f}%)")
    if routing_results['auto_accuracy']:
        print(f"  Auto-approval Accuracy: {routing_results['auto_accuracy']:.4f}")
    
    print("\n✅ Pipeline completed successfully!")
    print("\nKey Achievements:")
    print("✓ Data leakage detection implemented")
    print("✓ Class imbalance analysis performed") 
    print("✓ Cross-validation for robust evaluation")
    print("✓ Feature engineering for both tabular and text data")
    print("✓ Confidence-based routing with threshold optimization")
    print("✓ Comprehensive model comparison and evaluation")
    print("✓ Models saved for production deployment")


def load_and_test_models():
    """Load saved models and test predictions"""
    print("🔄 Loading Saved Models for Testing")
    print("=" * 70)
    
    # Check if models exist
    persistence = ModelPersistence()
    
    if not persistence.model_exists('grading'):
        print("❌ No saved grading models found. Run with --train first.")
        return
        
    if not persistence.model_exists('triage'):
        print("❌ No saved triage models found. Run with --train first.")
        return
    
    # Load models
    grading_pipeline, triage_pipeline, metadata = load_all_models()
    
    print("\n" + "="*70)
    print("📊 MODEL INFORMATION")
    print("="*70)
    
    print("\n🎯 Grading Model:")
    print(f"  Saved: {metadata['grading']['saved_at']}")
    print(f"  Features: {len(metadata['grading']['feature_names'])}")
    print(f"  Classes: {metadata['grading']['classes']}")
    print(f"  Models: {metadata['grading']['model_types']}")
    if 'performance' in metadata['grading']:
        perf = metadata['grading']['performance']
        print(f"  Performance: Accuracy={perf['baseline_accuracy']:.4f}, F1={perf['baseline_f1']:.4f}")
    
    print("\n🎯 Triage Model:")
    print(f"  Saved: {metadata['triage']['saved_at']}")
    print(f"  Classifier: {metadata['triage']['classifier_type']}")
    print(f"  Classes: {metadata['triage']['classes']}")
    print(f"  Threshold: {metadata['triage']['confidence_threshold']:.3f}")
    if 'performance' in metadata['triage']:
        perf = metadata['triage']['performance']
        print(f"  Performance: Accuracy={perf['accuracy']:.4f}, Auto-rate={perf['auto_approval_rate']:.2%}")
    
    # Test predictions
    print("\n" + "="*70)
    print("🧪 TESTING PREDICTIONS")
    print("="*70)
    
    # Test grading prediction
    print("\n📝 Test Grade Prediction:")
    import pandas as pd
    import numpy as np
    
    test_student = pd.DataFrame([{
        'attendance_percentage': 85.0,
        'quiz_average': 78.5,
        'assignment_average': 82.0,
        'midterm_score': 76.0,
        'participation_score': 8.5,
        'study_hours_per_week': 15.0,
        'previous_gpa': 3.2
    }])
    
    # Feature engineering
    test_student['engagement_score'] = (
        test_student['attendance_percentage'] * 0.4 + 
        test_student['participation_score'] * 10 * 0.6
    )
    test_student['academic_consistency'] = (
        test_student['quiz_average'] + test_student['assignment_average']
    ) / 2
    test_student['performance_trend'] = (
        test_student['midterm_score'] - test_student['academic_consistency']
    )
    
    # Predict
    features = test_student[grading_pipeline.feature_names]
    features_scaled = grading_pipeline.scaler.transform(features)
    
    baseline_pred = grading_pipeline.baseline_model.predict(features_scaled)[0]
    baseline_proba = grading_pipeline.baseline_model.predict_proba(features_scaled)[0]
    
    grade = grading_pipeline.label_encoder.inverse_transform([baseline_pred])[0]
    confidence = np.max(baseline_proba)
    
    print(f"  Student Features: Attendance={test_student['attendance_percentage'].iloc[0]:.1f}%, Quiz={test_student['quiz_average'].iloc[0]:.1f}")
    print(f"  Predicted Grade: {grade}")
    print(f"  Confidence: {confidence:.4f}")
    print(f"  Decision: {'Auto-approve' if confidence >= 0.7 else 'Teacher review'}")
    
    print("\n✅ Models loaded and tested successfully!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='ML Pipeline with Model Persistence')
    parser.add_argument('--train', action='store_true', help='Train and save models')
    parser.add_argument('--load', action='store_true', help='Load and test saved models')
    parser.add_argument('--all', action='store_true', help='Train, save, then load and test')
    
    args = parser.parse_args()
    
    if args.all:
        train_and_save_models()
        print("\n" + "="*70 + "\n")
        load_and_test_models()
    elif args.train:
        train_and_save_models()
    elif args.load:
        load_and_test_models()
    else:
        # Default: train and save
        print("No arguments provided. Running with --all (train + load test)")
        print("Use --train to only train, --load to only load and test")
        print("="*70 + "\n")
        train_and_save_models()
        print("\n" + "="*70 + "\n")
        load_and_test_models()


if __name__ == "__main__":
    main()
