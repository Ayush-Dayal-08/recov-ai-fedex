from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Relative import
from .predictor import RecoveryPredictor

app = FastAPI()

# --- 1. ALLOW ALL CONNECTIONS (CORS) ---
# This fixes the "Blocked" errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Initialize AI
try:
    predictor = RecoveryPredictor()
    print("✅ AI Engine Loaded")
except Exception as e:
    print(f"❌ AI Engine Failed: {e}")
    predictor = None

# --- 2. DEFINE DATA STRUCTURE ---
# The frontend MUST send data matching this exactly
class AccountRequest(BaseModel):
    account_id: str
    company_name: str
    amount: float
    days_overdue: int
    payment_history_score: float
    shipment_volume_30d: int
    shipment_volume_change_30d: float
    industry: str
    region: str
    # Optional fields
    express_ratio: Optional[float] = 0.0
    destination_diversity: Optional[int] = 0
    email_opened: Optional[bool] = False
    dispute_flag: Optional[bool] = False

@app.get("/")
def home():
    return {"status": "Backend is Running", "url": "http://127.0.0.1:8000"}

@app.post("/predict")
def predict_recovery(data: AccountRequest):
    print(f"📩 Received Request for: {data.company_name}")
    
    if not predictor:
        return {"error": "AI Model not loaded"}
        
    account_data = data.dict()
    result = predictor.predict_recovery(account_data)
    return result

if __name__ == "__main__":
    # Force it to run on 127.0.0.1 port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)