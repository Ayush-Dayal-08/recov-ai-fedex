from pydantic import BaseModel
from typing import List, Optional

# 1. INPUT MODEL (Matches your CSV columns)
class AccountData(BaseModel):
    account_id: str
    company_name: str
    amount: float
    days_overdue: int
    payment_history_score: float
    shipment_volume_change_30d: float
    # Optional fields (Good to have, but not strictly required for prediction if model doesn't use them)
    industry: Optional[str] = None
    region: Optional[str] = None
    shipment_volume_30d: Optional[float] = 0.0
    express_ratio: Optional[float] = 0.0
    destination_diversity: Optional[int] = 0
    contact_attempts: Optional[int] = 0
    customer_tenure_months: Optional[int] = 0
    email_opened: Optional[int] = 0
    dispute_flag: Optional[int] = 0

# 2. OUTPUT MODELS
class TopFactor(BaseModel):
    feature: str
    impact: str  # "Increases Risk" or "Increases Recovery"
    value: float

class DCARecommendation(BaseModel):
    agency_name: str
    strategy: str
    estimated_commission: str

class PredictionResponse(BaseModel):
    account_id: str
    risk_score: float
    recovery_probability: float
    risk_level: str  # "Low", "Medium", "High"
    expected_recovery_amount: float
    days_to_pay_prediction: int
    top_factors: List[TopFactor]
    dca_recommendation: DCARecommendation