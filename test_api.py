import requests
import json
import os

# Define file path and API URL
file_path = "backend/data/demo_data.csv"
url = "http://127.0.0.1:8000/analyze"

# Check if file exists first
if not os.path.exists(file_path):
    print(f"❌ Error: File not found at {file_path}")
    print("Please make sure you generated demo_data.csv in Day 1.")
    exit()

try:
    # Open the file and send it to the API
    with open(file_path, "rb") as f:
        print(f"🚀 Sending {file_path} to RECOV.AI API...")
        files = {"file": f}
        response = requests.post(url, files=files)
    
    # Check response
    if response.status_code == 200:
        print("✅ SUCCESS! API returned predictions.")
        predictions = response.json()
        
        # Show the first prediction to prove it works
        print("\n--- Example Prediction (First Account) ---")
        print(json.dumps(predictions[0], indent=2))
        
        print(f"\n✅ Total Accounts Analyzed: {len(predictions)}")
    else:
        print(f"❌ API Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"❌ Connection Error: {e}")
    print("Make sure the server is running (uvicorn backend.main:app --reload)")