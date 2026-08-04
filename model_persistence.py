"""
Model Persistence Module
========================

Provides functionality to save and load trained models with metadata
"""

import pickle
import joblib
import json
import os
from datetime import datetime
from pathlib import Path


class ModelPersistence:
    """Handle saving and loading of trained ML models"""
    
    def __init__(self, base_path="models"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
    def save_grading_model(self, pipeline, metadata=None):
        """
        Save grading pipeline models and artifacts
        
        Args:
            pipeline: GradingPipeline instance
            metadata: Optional dict with additional metadata
        """
        model_dir = self.base_path / "grading"
        model_dir.mkdir(exist_ok=True)
        
        # Save models
        joblib.dump(pipeline.baseline_model, model_dir / "baseline_model.pkl")
        joblib.dump(pipeline.advanced_model, model_dir / "advanced_model.pkl")
        joblib.dump(pipeline.scaler, model_dir / "scaler.pkl")
        joblib.dump(pipeline.label_encoder, model_dir / "label_encoder.pkl")
        
        # Save metadata
        model_metadata = {
            "saved_at": datetime.now().isoformat(),
            "feature_names": pipeline.feature_names,
            "confidence_threshold": pipeline.confidence_threshold,
            "classes": pipeline.label_encoder.classes_.tolist(),
            "model_types": {
                "baseline": type(pipeline.baseline_model).__name__,
                "advanced": type(pipeline.advanced_model).__name__
            }
        }
        
        if metadata:
            model_metadata.update(metadata)
            
        with open(model_dir / "metadata.json", "w") as f:
            json.dump(model_metadata, f, indent=2)
            
        print(f"✅ Grading models saved to {model_dir}")
        return model_dir
        
    def load_grading_model(self, pipeline):
        """
        Load grading pipeline models and artifacts
        
        Args:
            pipeline: GradingPipeline instance to load into
            
        Returns:
            Updated pipeline with loaded models
        """
        model_dir = self.base_path / "grading"
        
        if not model_dir.exists():
            raise FileNotFoundError(f"Model directory not found: {model_dir}")
            
        # Load models
        pipeline.baseline_model = joblib.load(model_dir / "baseline_model.pkl")
        pipeline.advanced_model = joblib.load(model_dir / "advanced_model.pkl")
        pipeline.scaler = joblib.load(model_dir / "scaler.pkl")
        pipeline.label_encoder = joblib.load(model_dir / "label_encoder.pkl")
        
        # Load metadata
        with open(model_dir / "metadata.json", "r") as f:
            metadata = json.load(f)
            
        pipeline.feature_names = metadata["feature_names"]
        pipeline.confidence_threshold = metadata["confidence_threshold"]
        
        print(f"✅ Grading models loaded from {model_dir}")
        print(f"   Saved at: {metadata['saved_at']}")
        print(f"   Models: {metadata['model_types']}")
        
        return pipeline, metadata
        
    def save_triage_model(self, pipeline, metadata=None):
        """
        Save triage pipeline models and artifacts
        
        Args:
            pipeline: DoubtTriagePipeline instance
            metadata: Optional dict with additional metadata
        """
        model_dir = self.base_path / "triage"
        model_dir.mkdir(exist_ok=True)
        
        # Save models
        joblib.dump(pipeline.classifier, model_dir / "classifier.pkl")
        joblib.dump(pipeline.vectorizer, model_dir / "vectorizer.pkl")
        joblib.dump(pipeline.label_encoder, model_dir / "label_encoder.pkl")
        joblib.dump(pipeline.department_encoder, model_dir / "department_encoder.pkl")
        
        # Save metadata
        model_metadata = {
            "saved_at": datetime.now().isoformat(),
            "confidence_threshold": pipeline.confidence_threshold,
            "classes": pipeline.label_encoder.classes_.tolist(),
            "departments": pipeline.department_encoder.classes_.tolist(),
            "classifier_type": type(pipeline.classifier).__name__,
            "vectorizer_params": {
                "max_features": pipeline.vectorizer.max_features,
                "stop_words": pipeline.vectorizer.stop_words
            }
        }
        
        if metadata:
            model_metadata.update(metadata)
            
        with open(model_dir / "metadata.json", "w") as f:
            json.dump(model_metadata, f, indent=2)
            
        print(f"✅ Triage models saved to {model_dir}")
        return model_dir
        
    def load_triage_model(self, pipeline):
        """
        Load triage pipeline models and artifacts
        
        Args:
            pipeline: DoubtTriagePipeline instance to load into
            
        Returns:
            Updated pipeline with loaded models
        """
        model_dir = self.base_path / "triage"
        
        if not model_dir.exists():
            raise FileNotFoundError(f"Model directory not found: {model_dir}")
            
        # Load models
        pipeline.classifier = joblib.load(model_dir / "classifier.pkl")
        pipeline.vectorizer = joblib.load(model_dir / "vectorizer.pkl")
        pipeline.label_encoder = joblib.load(model_dir / "label_encoder.pkl")
        pipeline.department_encoder = joblib.load(model_dir / "department_encoder.pkl")
        
        # Load metadata
        with open(model_dir / "metadata.json", "r") as f:
            metadata = json.load(f)
            
        pipeline.confidence_threshold = metadata["confidence_threshold"]
        
        print(f"✅ Triage models loaded from {model_dir}")
        print(f"   Saved at: {metadata['saved_at']}")
        print(f"   Classifier: {metadata['classifier_type']}")
        
        return pipeline, metadata
        
    def model_exists(self, model_type):
        """
        Check if saved model exists
        
        Args:
            model_type: 'grading' or 'triage'
            
        Returns:
            bool: True if model exists
        """
        model_dir = self.base_path / model_type
        metadata_file = model_dir / "metadata.json"
        
        return metadata_file.exists()
        
    def get_model_info(self, model_type):
        """
        Get information about saved model
        
        Args:
            model_type: 'grading' or 'triage'
            
        Returns:
            dict: Model metadata
        """
        model_dir = self.base_path / model_type
        metadata_file = model_dir / "metadata.json"
        
        if not metadata_file.exists():
            return None
            
        with open(metadata_file, "r") as f:
            return json.load(f)


def save_all_models(grading_pipeline, triage_pipeline, performance_metrics=None):
    """
    Convenience function to save both pipelines
    
    Args:
        grading_pipeline: Trained GradingPipeline
        triage_pipeline: Trained DoubtTriagePipeline
        performance_metrics: Optional dict with performance metrics
    """
    persistence = ModelPersistence()
    
    print("\n=== SAVING MODELS ===")
    
    # Save grading models
    grading_metadata = {}
    if performance_metrics and 'grading' in performance_metrics:
        grading_metadata['performance'] = performance_metrics['grading']
    persistence.save_grading_model(grading_pipeline, grading_metadata)
    
    # Save triage models
    triage_metadata = {}
    if performance_metrics and 'triage' in performance_metrics:
        triage_metadata['performance'] = performance_metrics['triage']
    persistence.save_triage_model(triage_pipeline, triage_metadata)
    
    print("✅ All models saved successfully!")


def load_all_models(grading_pipeline=None, triage_pipeline=None):
    """
    Convenience function to load both pipelines
    
    Args:
        grading_pipeline: GradingPipeline instance (or None to create new)
        triage_pipeline: DoubtTriagePipeline instance (or None to create new)
        
    Returns:
        tuple: (grading_pipeline, triage_pipeline, metadata)
    """
    from ml_pipeline import GradingPipeline, DoubtTriagePipeline
    
    persistence = ModelPersistence()
    
    print("\n=== LOADING MODELS ===")
    
    # Initialize pipelines if needed
    if grading_pipeline is None:
        grading_pipeline = GradingPipeline()
    if triage_pipeline is None:
        triage_pipeline = DoubtTriagePipeline()
    
    # Load models
    grading_pipeline, grading_metadata = persistence.load_grading_model(grading_pipeline)
    triage_pipeline, triage_metadata = persistence.load_triage_model(triage_pipeline)
    
    metadata = {
        'grading': grading_metadata,
        'triage': triage_metadata
    }
    
    print("✅ All models loaded successfully!")
    
    return grading_pipeline, triage_pipeline, metadata
