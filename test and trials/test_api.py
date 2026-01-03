"""
RECOV.AI - API Testing Script
==============================
Tests all Day 3 endpoints. 
"""

import requests
import json
import os

# Configuration
API_URL = "http://127.0.0.1:8000"
DEMO_CSV = "backend/data/demo_data.csv"

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_health_check():
    """Test 1: Health check endpoint"""
    print_section("TEST 1: Health Check (GET /)")
    
    try:
        response = requests.get(f"{API_URL}/")
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Response:\n{json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e: 
        print(f"❌ Error: {e}")
        return False

def test_single_prediction():
    """Test 2: Single account prediction"""
    print_section("TEST 2: Single Prediction (POST /predict)")
    
    # Test account data
    test_account = {
        "account_id": "TEST001",
        "company_name": "Test Company Inc",
        "amount": 150000,
        "days_overdue":  45,
        "payment_history_score": 0.75,
        "shipment_volume_change_30d": 0.25,
        "industry":  "Technology",
        "region":  "South",
        "email_opened":  True,
        "dispute_flag":  False
    }
    
    try:
        response = requests. post(f"{API_URL}/predict", json=test_account)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📊 Prediction Results:")
            print(f"   Account ID: {result['account_id']}")
            print(f"   Company: {result['company_name']}")
            print(f"   Recovery Probability: {result['recovery_probability']:.1%}")
            print(f"   Expected Days: {result['expected_days']}")
            print(f"   Risk Level: {result['risk_level']}")
            print(f"   Recommended DCA: {result['recommended_dca']['name']}")
            
            if result['top_factors']:
                print(f"\n   Top Factors:")
                for factor in result['top_factors'][:3]:
                    print(f"     • {factor['feature']}: {factor['impact']:.3f} ({factor['direction']})")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_csv_upload():
    """Test 3: CSV file upload and batch analysis"""
    print_section("TEST 3: CSV Upload (POST /analyze)")
    
    # Check if demo CSV exists
    if not os. path.exists(DEMO_CSV):
        print(f"❌ Demo CSV not found:  {DEMO_CSV}")
        print(f"   Please ensure demo_data.csv exists in backend/data/")
        return False
    
    try:
        with open(DEMO_CSV, 'rb') as f:
            files = {'file': ('demo_data.csv', f, 'text/csv')}
            response = requests.post(f"{API_URL}/analyze", files=files)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📊 Analysis Summary:")
            print(f"   Total Accounts: {result['total_accounts']}")
            print(f"   High Probability (>70%): {result['summary']['high_probability']}")
            print(f"   Medium Probability (40-70%): {result['summary']['medium_probability']}")
            print(f"   Low Probability (<40%): {result['summary']['low_probability']}")
            
            # Show first prediction
            if result['predictions']: 
                first = result['predictions'][0]
                print(f"\n   First Account Preview:")
                print(f"     ID: {first['account_id']}")
                print(f"     Company: {first['company_name']}")
                print(f"     Probability: {first['recovery_probability']:.1%}")
                print(f"     DCA: {first['recommended_dca']['name']}")
            
            return True
        else: 
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_account():
    """Test 4: Get specific account"""
    print_section("TEST 4: Get Account (GET /account/{id})")
    
    # First, upload CSV to populate database
    print("📤 Uploading CSV first to populate database...")
    
    if not os.path.exists(DEMO_CSV):
        print(f"❌ Demo CSV not found:  {DEMO_CSV}")
        return False
    
    try: 
        # Upload CSV
        with open(DEMO_CSV, 'rb') as f:
            files = {'file': ('demo_data.csv', f, 'text/csv')}
            upload_response = requests.post(f"{API_URL}/analyze", files=files)
        
        if upload_response.status_code != 200:
            print(f"❌ CSV upload failed: {upload_response. text}")
            return False
        
        # Get first account ID from upload response
        upload_result = upload_response.json()
        if not upload_result['predictions']:
            print("❌ No accounts found in CSV")
            return False
        
        account_id = upload_result['predictions'][0]['account_id']
        print(f"✅ CSV uploaded.  Testing GET for account:  {account_id}")
        
        # Now test GET endpoint
        response = requests.get(f"{API_URL}/account/{account_id}")
        print(f"\n✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📊 Account Details:")
            print(f"   Account ID: {result['account_id']}")
            print(f"   Company: {result['company_name']}")
            print(f"   Recovery Probability: {result['recovery_probability']:.1%}")
            print(f"   Expected Days: {result['expected_days']}")
            print(f"   Recommended DCA: {result['recommended_dca']['name']}")
            
            return True
        else: 
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error:  {e}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("\n" + "🚀"*35)
    print("  RECOV.AI - API TEST SUITE")
    print("🚀"*35)
    
    results = {
        "Health Check": test_health_check(),
        "Single Prediction": test_single_prediction(),
        "CSV Upload": test_csv_upload(),
        "Get Account": test_get_account()
    }
    
    # Summary
    print_section("TEST SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*70}")
    print(f"  Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!  Day 3 requirements complete!")
        return True
    else:
        print(f"⚠️ {total - passed} test(s) failed. Check server logs.")
        return False

if __name__ == "__main__":
    # Check if server is running
    try:
        requests.get(f"{API_URL}/", timeout=2)
    except:
        print("\n❌ ERROR: Backend server not running!")
        print("   Please start the server first:")
        print("   1. cd backend")
        print("   2. uvicorn main:app --reload")
        print("   3. Then run this test again\n")
        exit(1)
    
    # Run tests
    success = run_all_tests()
    exit(0 if success else 1)