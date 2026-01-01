from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from backend.models import AccountData, PredictionResponse
from backend.predictor import RecoveryPredictor
import pandas as pd
import io

# ==========================================
# SETUP & CONFIGURATION
# ==========================================
app = FastAPI(title="Recov.AI FedEx Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = RecoveryPredictor()
accounts_db = {} # In-memory storage

@app.get("/")
def home():
    return {"status": "Backend is Running", "accounts_analyzed": len(accounts_db)}

# 1. SINGLE PREDICTION
@app.post("/predict", response_model=PredictionResponse)
def predict_single(account: AccountData):
    try:
        data = account.dict()
        result = predictor.predict_recovery(data)
        acc_id = data.get("account_id", "SINGLE_SCAN")
        accounts_db[acc_id] = result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. BATCH CSV UPLOAD
@app.post("/analyze")
async def analyze_batch(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        results = []
        
        for _, row in df.iterrows():
            account_data = row.to_dict()
            try:
                # Ensure minimal required fields exist
                if 'amount' not in account_data: account_data['amount'] = 0
                
                prediction = predictor.predict_recovery(account_data)
                
                acc_id = str(account_data.get('account_id', f"ROW_{_}"))
                accounts_db[acc_id] = prediction
                results.append(prediction)
            except Exception as e:
                print(f"Skipping row {_}: {e}")
                continue
                
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. GET DETAILS
@app.get("/account/{account_id}")
def get_account(account_id: str):
    if account_id in accounts_db:
        return accounts_db[account_id]
    raise HTTPException(status_code=404, detail="Account not found")