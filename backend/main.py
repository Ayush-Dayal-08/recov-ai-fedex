from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import json
from typing import List, Dict
import sys
import os

# Robust import logic for sibling modules
try:
    from backend.predictor import RecoveryPredictor
    from backend.models import AccountData, PredictionResponse
except ImportError:
    # If running from inside backend/ folder
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from predictor import RecoveryPredictor
    from models import AccountData, PredictionResponse

app = FastAPI(title="RECOV.AI API", version="1.0.0")

# --- 1. CORS SETUP ---
# Allows React (localhost:5173) to talk to this Python backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. GLOBAL STATE ---
# In-memory database to store the last analysis results
stored_predictions: Dict[str, dict] = {}

# Initialize the Brain
try:
    predictor = RecoveryPredictor()
    print("✅ RECOV.AI Brain Initialized")
except Exception as e:
    print(f"❌ Failed to initialize predictor: {e}")
    predictor = None

# --- 3. ENDPOINTS ---

@app.get("/")
def home():
    return {"message": "RECOV.AI API is Running", "status": "active"}

@app.post("/analyze", response_model=List[PredictionResponse])
async def analyze_file(file: UploadFile = File(...)):
    """
    Receives a CSV file, parses it, runs ML predictions, 
    and returns the results.
    """
    if not predictor:
        raise HTTPException(status_code=500, detail="ML Model not active")
    
    # 1. Read the uploaded file
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")
    
    # 2. Validate essential columns exist
    required_cols = ['account_id', 'amount', 'days_overdue']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")
    
    # 3. Generate Predictions
    results = []
    stored_predictions.clear() # Clear old cache
    
    print(f"Processing {len(df)} accounts...")
    
    for _, row in df.iterrows():
        # Convert row to dict
        account_data = row.to_dict()
        
        # Run Prediction
        prediction = predictor.predict_recovery(account_data)
        
        # Add to results list
        results.append(prediction)
        
        # Store in memory for Detail View
        acc_id = str(account_data.get('account_id', 'unknown'))
        stored_predictions[acc_id] = prediction
        
    print(f"✅ Analyzed {len(results)} accounts successfully")
    return results

@app.get("/account/{account_id}", response_model=PredictionResponse)
def get_account_detail(account_id: str):
    """
    Fetch the detailed prediction for a specific account.
    """
    if account_id not in stored_predictions:
        raise HTTPException(status_code=404, detail="Account not found. Upload a file first.")
    
    return stored_predictions[account_id]