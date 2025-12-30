from pydantic import BaseModel
from typing import List, Optional, Union

# --- 1. INPUT MODEL ---
class AccountData(BaseModel):
    account_id: str
    company_name: str = "Unknown"
    amount: float
    days_overdue: int
    payment_history_score: float
    shipment_volume_30d: float
    shipment_volume_change_30d: float
    express_ratio: float
    destination_diversity: int
    industry: str = "Other"
    region: str = "Other"
    email_opened: bool = False
    dispute_flag: bool = False
    
    class Config:
        extra = "ignore" 

# --- 2. OUTPUT MODELS ---

class DCARecommendation(BaseModel):
    name: str
    specialization: str
    # FIX 1: Add a default value so it doesn't crash if predictor omits it
    reasoning: str = "Recommended based on account profile"

class TopFactor(BaseModel):
    feature: str
    # FIX 2: Accept float (numbers) because that is what SHAP returns
    impact: float     
    direction: str

class PredictionResponse(BaseModel):
    account_id: str
    company_name: str
    recovery_probability: float
    recovery_percentage: float
    expected_days: int
    recovery_velocity_score: float
    risk_level: str
    recommended_dca: DCARecommendation
    top_factors: List[TopFactor]
    prediction_timestamp: str