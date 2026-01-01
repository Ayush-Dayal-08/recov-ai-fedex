"""
RECOV.AI - FastAPI Backend
===========================
Main API server for debt recovery predictions.  
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import io
import uvicorn

# Import predictor
try:
    from backend.predictor import RecoveryPredictor
except:  
    from predictor import RecoveryPredictor

# Initialize FastAPI app
app = FastAPI(
    title="RECOV.AI API",
    description="AI-powered debt recovery prediction system",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Engine
try:
    predictor = RecoveryPredictor()
    print("✅ AI Engine Loaded Successfully")
except Exception as e:  
    print(f"❌ AI Engine Failed to Load:  {e}")
    predictor = None

# In-memory storage for accounts
accounts_db = {}

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AccountRequest(BaseModel):
    """Single account prediction request"""
    account_id: str
    company_name:  str
    amount:  float
    days_overdue: int
    payment_history_score: float
    shipment_volume_change_30d: float
    
    # Optional fields with defaults
    shipment_volume_30d: Optional[int] = 0
    express_ratio: Optional[float] = 0.0
    destination_diversity: Optional[int] = 0
    industry:  Optional[str] = "Other"
    region: Optional[str] = "Other"
    email_opened: Optional[bool] = False
    dispute_flag: Optional[bool] = False

# ============================================================================
# HELPER FUNCTION
# ============================================================================

def to_dict(obj):
    """Convert result to dict, handling both dict and Pydantic models"""
    if isinstance(obj, dict):
        return obj
    elif hasattr(obj, 'dict'):
        return obj.dict()
    elif hasattr(obj, 'model_dump'):  # Pydantic v2
        return obj.model_dump()
    else: 
        return dict(obj)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def home():
    """Health check endpoint"""
    return {
        "status":  "RECOV.AI Backend Running",
        "project":  "FedEx SMART Hackathon 2026",
        "endpoints": {
            "health": "GET /",
            "single_prediction": "POST /predict",
            "batch_analysis": "POST /analyze",
            "get_account": "GET /account/{account_id}"
        },
        "ai_engine":  "Loaded" if predictor else "Error"
    }

@app.post("/predict")
def predict_single(data: AccountRequest):
    """
    Predict recovery for a single account.  
    
    **Day 3 Requirement:** Single account prediction endpoint
    """
    if not predictor: 
        raise HTTPException(status_code=500, detail="AI Engine not loaded")
    
    try:
        # Convert to dict
        account_data = data.dict()
        
        # Store in memory
        accounts_db[account_data['account_id']] = account_data
        
        # Get prediction
        result = predictor.predict_recovery(account_data)
        
        # Ensure it's a dict
        result_dict = to_dict(result)
        
        # Add original data back
        result_dict['amount'] = float(account_data.get('amount', 0))
        result_dict['days_overdue'] = int(account_data.get('days_overdue', 0))

        return result_dict
        
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Prediction failed:  {str(e)}")

@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    """
    Analyze multiple accounts from CSV file. 
    
    **Day 3 Requirement:** CSV upload and batch processing
    """
    if not predictor:
        raise HTTPException(status_code=500, detail="AI Engine not loaded")
    
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Validate required columns
        required_cols = ['account_id', 'company_name', 'amount', 'days_overdue', 
                         'payment_history_score', 'shipment_volume_change_30d']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_cols}"
            )
        
        # Process each account
        predictions = []
        for idx, row in df.iterrows():
            account_dict = row.to_dict()
            
            # Store in memory
            accounts_db[account_dict['account_id']] = account_dict
            
            # Get prediction and convert to dict
            result = predictor.predict_recovery(account_dict)
            result_dict = to_dict(result)
            
            # ✅ NEW: Include original account data in response
            # Using safe casting to ensure frontend doesn't break
            result_dict['amount'] = float(account_dict.get('amount', 0) or 0)
            result_dict['days_overdue'] = int(account_dict.get('days_overdue', 0) or 0)
            
            predictions.append(result_dict)
        
        return {
            "total_accounts": len(predictions),
            "predictions": predictions,
            "summary": {
                "high_probability": sum(1 for p in predictions if p['recovery_probability'] > 0.7),
                "medium_probability": sum(1 for p in predictions if 0.4 < p['recovery_probability'] <= 0.7),
                "low_probability": sum(1 for p in predictions if p['recovery_probability'] <= 0.4),
            }
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/account/{account_id}")
def get_account(account_id: str):
    """
    Get prediction for a specific account by ID.
    
    **Day 3 Requirement:** Retrieve single account detail
    """
    if not predictor: 
        raise HTTPException(status_code=500, detail="AI Engine not loaded")
    
    # Check if account exists in memory
    if account_id not in accounts_db:
        raise HTTPException(
            status_code=404, 
            detail=f"Account {account_id} not found. Upload CSV first via /analyze"
        )
    
    try: 
        account_data = accounts_db[account_id]
        result = predictor.predict_recovery(account_data)
        
        # Convert to dict and enrich with original data
        result_dict = to_dict(result)
        result_dict['amount'] = float(account_data.get('amount', 0))
        result_dict['days_overdue'] = int(account_data.get('days_overdue', 0))
        
        return result_dict
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/accounts/list")
def list_accounts():
    """List all accounts in memory"""
    return {
        "total_accounts": len(accounts_db),
        "account_ids": list(accounts_db.keys())
    }

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":  
    print("🚀 Starting RECOV.AI Backend Server...")
    print("📍 Server will run at:  http://127.0.0.1:8000")
    print("📖 API Docs: http://127.0.0.1:8000/docs")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)