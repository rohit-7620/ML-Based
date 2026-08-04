"""
Comprehensive Test Suite for Enhanced API
========================================

Tests all endpoints including batch processing and model persistence
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_health():
    """Test health endpoint"""
    print_section("Testing Health Endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200 and result.get('models_loaded', False)
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_model_info():
    """Test model info endpoint"""
    print_section("Testing Model Info Endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/models/info")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n📊 Grading Model Info:")
            print(f"  Saved: {result['grading_pipeline']['saved_at']}")
            print(f"  Models: {result['grading_pipeline']['baseline_model']} + {result['grading_pipeline']['advanced_model']}")
            print(f"  Features: {len(result['grading_pipeline']['features'])}")
            print(f"  Classes: {result['grading_pipeline']['classes']}")
            
            print("\n📊 Triage Model Info:")
            print(f"  Saved: {result['triage_pipeline']['saved_at']}")
            print(f"  Classifier: {result['triage_pipeline']['classifier']}")
            print(f"  Classes: {result['triage_pipeline']['classes']}")
            print(f"  Departments: {len(result['triage_pipeline']['departments'])}")
            
            if 'performance' in result['grading_pipeline']:
                perf = result['grading_pipeline']['performance']
                print(f"\n  Grading Performance: Acc={perf.get('baseline_accuracy', 'N/A'):.4f}")
            
            if 'performance' in result['triage_pipeline']:
                perf = result['triage_pipeline']['performance']
                print(f"  Triage Performance: Acc={perf.get('accuracy', 'N/A'):.4f}")
            
            return True
        else:
            print(f"  ❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Model info test failed: {e}")
        return False

def test_grade_prediction():
    """Test grade prediction endpoint"""
    print_section("Testing Grade Prediction")
    
    test_cases = [
        {
            "name": "High Performer (Expected: A)",
            "data": {
                "attendance_percentage": 95.0,
                "quiz_average": 88.5,
                "assignment_average": 92.0,
                "midterm_score": 87.0,
                "participation_score": 9.2,
                "study_hours_per_week": 20.0,
                "previous_gpa": 3.8
            }
        },
        {
            "name": "Average Student (Expected: B/C)",
            "data": {
                "attendance_percentage": 78.0,
                "quiz_average": 72.5,
                "assignment_average": 75.0,
                "midterm_score": 74.0,
                "participation_score": 6.5,
                "study_hours_per_week": 12.0,
                "previous_gpa": 3.0
            }
        },
        {
            "name": "Struggling Student (Expected: C/D)",
            "data": {
                "attendance_percentage": 65.0,
                "quiz_average": 58.5,
                "assignment_average": 62.0,
                "midterm_score": 55.0,
                "participation_score": 4.2,
                "study_hours_per_week": 8.0,
                "previous_gpa": 2.3
            }
        }
    ]
    
    success_count = 0
    try:
        for case in test_cases:
            print(f"\n📊 {case['name']}:")
            response = requests.post(
                f"{API_BASE_URL}/predict/grade", 
                json=case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ Predicted Grade: {result['predicted_grade']}")
                print(f"  ✓ Confidence: {result['confidence_score']:.4f}")
                print(f"  ✓ Model Used: {result['model_used']}")
                print(f"  ✓ Routing: {result['routing_decision']}")
                
                # Show engineered features
                eng_feat = result.get('engineered_features', {})
                print(f"  ✓ Engineered Features:")
                print(f"      Engagement: {eng_feat.get('engagement_score', 0):.2f}")
                print(f"      Consistency: {eng_feat.get('academic_consistency', 0):.2f}")
                print(f"      Trend: {eng_feat.get('performance_trend', 0):.2f}")
                
                success_count += 1
            else:
                print(f"  ❌ Error: {response.status_code} - {response.text}")
        
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"❌ Grade prediction test failed: {e}")
        return False

def test_batch_grade_prediction():
    """Test batch grade prediction endpoint"""
    print_section("Testing Batch Grade Prediction")
    
    batch_data = {
        "students": [
            {
                "attendance_percentage": 95.0,
                "quiz_average": 88.5,
                "assignment_average": 92.0,
                "midterm_score": 87.0,
                "participation_score": 9.2,
                "study_hours_per_week": 20.0,
                "previous_gpa": 3.8
            },
            {
                "attendance_percentage": 78.0,
                "quiz_average": 72.5,
                "assignment_average": 75.0,
                "midterm_score": 74.0,
                "participation_score": 6.5,
                "study_hours_per_week": 12.0,
                "previous_gpa": 3.0
            },
            {
                "attendance_percentage": 65.0,
                "quiz_average": 58.5,
                "assignment_average": 62.0,
                "midterm_score": 55.0,
                "participation_score": 4.2,
                "study_hours_per_week": 8.0,
                "previous_gpa": 2.3
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/batch/grade", 
            json=batch_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Total Students: {result['total_students']}")
            print(f"✓ Successful Predictions: {result['successful_predictions']}")
            
            print("\n📊 Batch Results:")
            for student_result in result['batch_results']:
                if 'predicted_grade' in student_result:
                    print(f"  Student {student_result['student_index']}: "
                          f"Grade={student_result['predicted_grade']}, "
                          f"Confidence={student_result['confidence']:.4f}, "
                          f"Auto-approve={student_result['auto_approve']}")
                else:
                    print(f"  Student {student_result['student_index']}: ERROR - {student_result.get('error')}")
            
            return result['successful_predictions'] == result['total_students']
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Batch prediction test failed: {e}")
        return False

def test_triage_prediction():
    """Test doubt triage endpoint"""
    print_section("Testing Doubt Triage")
    
    test_cases = [
        {
            "name": "Urgent Exam Issue (Expected: High)",
            "data": {
                "student_query": "I cannot download my hall ticket for tomorrow's exam. Please help urgently!",
                "department": "IT Support",
                "days_to_deadline": 1
            }
        },
        {
            "name": "General Inquiry (Expected: Low)",
            "data": {
                "student_query": "What are the university working hours?",
                "department": "Administration",
                "days_to_deadline": 15
            }
        },
        {
            "name": "Financial Issue (Expected: High)",
            "data": {
                "student_query": "I have not received my scholarship amount yet",
                "department": "Finance Office",
                "days_to_deadline": 8
            }
        },
        {
            "name": "Technical Problem (Expected: Medium)",
            "data": {
                "student_query": "LMS portal is not allowing me to upload my assignment",
                "department": "IT Support",
                "days_to_deadline": 3
            }
        }
    ]
    
    success_count = 0
    try:
        for case in test_cases:
            print(f"\n📋 {case['name']}:")
            response = requests.post(
                f"{API_BASE_URL}/predict/triage", 
                json=case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ Query: '{case['data']['student_query'][:50]}...'")
                print(f"  ✓ Predicted Priority: {result['predicted_priority']}")
                print(f"  ✓ Confidence: {result['confidence_score']:.4f}")
                print(f"  ✓ Routing: {result['routing_decision']}")
                
                # Show feature analysis
                feat = result.get('feature_analysis', {})
                print(f"  ✓ Feature Analysis:")
                print(f"      Query Length: {feat.get('query_length', 0)} words")
                print(f"      Urgent Keywords: {feat.get('has_urgent_keywords', False)}")
                print(f"      Technical Keywords: {feat.get('has_technical_keywords', False)}")
                print(f"      Urgency Score: {feat.get('urgency_from_deadline', 0)}/3")
                
                # Show probabilities
                probs = result.get('priority_probabilities', {})
                print(f"  ✓ Probabilities: {', '.join([f'{k}={v:.3f}' for k, v in probs.items()])}")
                
                success_count += 1
            else:
                print(f"  ❌ Error: {response.status_code} - {response.text}")
        
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"❌ Triage prediction test failed: {e}")
        return False

def test_error_handling():
    """Test API error handling"""
    print_section("Testing Error Handling")
    
    success = True
    
    # Test missing field in grade prediction
    print("\n🧪 Test: Missing field in grade prediction")
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict/grade", 
            json={"attendance_percentage": 85.0},  # Missing other fields
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 400:
            print("  ✓ Correctly returned 400 for missing fields")
        else:
            print(f"  ❌ Expected 400, got {response.status_code}")
            success = False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        success = False
    
    # Test invalid department in triage
    print("\n🧪 Test: Unknown department in triage (should handle gracefully)")
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict/triage", 
            json={
                "student_query": "Test query",
                "department": "Unknown Department XYZ",
                "days_to_deadline": 5
            },
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ Handled unknown department gracefully: {result['predicted_priority']}")
        else:
            print(f"  ⚠️  Got status {response.status_code}, but should handle gracefully")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        success = False
    
    return success

def main():
    """Run all API tests"""
    print("🚀 Starting Enhanced ML Pipeline API Tests")
    print("=" * 70)
    
    # Wait for API to be ready
    print("⏳ Waiting for API to be ready...")
    time.sleep(2)
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Model Info", test_model_info),
        ("Grade Prediction", test_grade_prediction),
        ("Batch Grade Prediction", test_batch_grade_prediction),
        ("Doubt Triage", test_triage_prediction),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n  Overall: {passed}/{len(tests)} tests passed")
    print("="*70)
    
    if passed == len(tests):
        print("🎉 All tests passed! Enhanced API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API service.")

if __name__ == "__main__":
    main()
