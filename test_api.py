"""
API Testing Script for ML Pipeline
=================================

Tests both grading and triage prediction endpoints with sample data
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_grade_prediction():
    """Test grade prediction endpoint"""
    print("\n🎯 Testing grade prediction...")
    
    # Sample student data
    test_cases = [
        {
            "name": "High Performer",
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
            "name": "Average Student",
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
            "name": "Struggling Student",
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
    
    try:
        for case in test_cases:
            print(f"\n📊 Testing {case['name']}:")
            response = requests.post(
                f"{API_BASE_URL}/predict/grade", 
                json=case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Predicted Grade: {result['predicted_grade']}")
                print(f"  Confidence: {result['confidence_score']:.4f}")
                print(f"  Model Used: {result['model_used']}")
                print(f"  Routing: {result['routing_decision']}")
            else:
                print(f"  ❌ Error: {response.status_code} - {response.text}")
                
        return True
        
    except Exception as e:
        print(f"❌ Grade prediction test failed: {e}")
        return False

def test_triage_prediction():
    """Test doubt triage endpoint"""
    print("\n🎯 Testing doubt triage...")
    
    # Sample doubt queries
    test_cases = [
        {
            "name": "Urgent Exam Issue",
            "data": {
                "student_query": "I cannot download my hall ticket for tomorrow's exam. Please help urgently!",
                "department": "IT Support",
                "days_to_deadline": 1
            }
        },
        {
            "name": "General Inquiry",
            "data": {
                "student_query": "What are the university working hours?",
                "department": "Administration",
                "days_to_deadline": 15
            }
        },
        {
            "name": "Financial Issue",
            "data": {
                "student_query": "I have not received my scholarship amount yet",
                "department": "Finance Office",
                "days_to_deadline": 8
            }
        },
        {
            "name": "Technical Problem",
            "data": {
                "student_query": "LMS portal is not allowing me to upload my assignment",
                "department": "IT Support",
                "days_to_deadline": 3
            }
        }
    ]
    
    try:
        for case in test_cases:
            print(f"\n📋 Testing {case['name']}:")
            response = requests.post(
                f"{API_BASE_URL}/predict/triage", 
                json=case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Query: '{case['data']['student_query'][:50]}...'")
                print(f"  Predicted Priority: {result['predicted_priority']}")
                print(f"  Confidence: {result['confidence_score']:.4f}")
                print(f"  Routing: {result['routing_decision']}")
                print(f"  Features: {result['feature_analysis']}")
            else:
                print(f"  ❌ Error: {response.status_code} - {response.text}")
                
        return True
        
    except Exception as e:
        print(f"❌ Triage prediction test failed: {e}")
        return False

def test_model_performance():
    """Test model performance endpoint"""
    print("\n📈 Testing model performance endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/models/performance")
        
        if response.status_code == 200:
            result = response.json()
            print("Model Performance Info:")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Starting ML Pipeline API Tests")
    print("=" * 50)
    
    # Wait a moment for API to be ready
    print("⏳ Waiting for API to be ready...")
    time.sleep(2)
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Grade Prediction", test_grade_prediction),
        ("Doubt Triage", test_triage_prediction),
        ("Model Performance", test_model_performance)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API service.")

if __name__ == "__main__":
    main()