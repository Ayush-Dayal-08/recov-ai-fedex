import pandas as pd
import numpy as np
import joblib
import os
import traceback
from backend.models import PredictionResponse, TopFactor, DCARecommendation

class RecoveryPredictor:
    def __init__(self):
        self.model = None
        self.REQUIRED_FEATURES = ['days_overdue', 'payment_history_score', 'shipment_volume_change_30d', 'amount_log']
        
        self.model_path = os.path.join("backend", "models", "recovery_model.pkl")
        
        try:
            if not os.path.exists(self.model_path):
                print(f"❌ CRITICAL: Model file missing at {self.model_path}")
                return

            # 1. LOAD THE ARTIFACT
            artifact = joblib.load(self.model_path)
            print(f"📂 Loaded Artifact Type: {type(artifact)}")

            # 2. PERMANENT FIX: FIND THE MODEL
            # We don't guess keys. We inspect every object to see if it's a model.
            if hasattr(artifact, "predict") or hasattr(artifact, "predict_proba"):
                self.model = artifact
                print("✅ Artifact IS the model.")
            elif isinstance(artifact, dict):
                print(f"📦 Inspecting Dictionary Keys: {list(artifact.keys())}")
                for key, value in artifact.items():
                    if hasattr(value, "predict") or hasattr(value, "predict_proba"):
                        self.model = value
                        print(f"✅ FOUND Model inside key: '{key}'")
                        break
            
            # If still not found (edge case), try first value
            if self.model is None and isinstance(artifact, dict) and len(artifact) > 0:
                print("⚠️ Model methods not detected. Forcing first value as model.")
                self.model = list(artifact.values())[0]

            # 3. SYNC FEATURES (Prevents Column Mismatch)
            if self.model and hasattr(self.model, "feature_names_in_"):
                self.REQUIRED_FEATURES = list(self.model.feature_names_in_)
                print(f"ℹ️ Model Features Synced: {self.REQUIRED_FEATURES}")

        except Exception as e:
            print(f"❌ MODEL LOAD ERROR: {e}")
            traceback.print_exc()

    def predict_recovery(self, data: dict) -> PredictionResponse:
        print(f"🔍 Analyzing: {data.get('account_id', 'Unknown')}")
        
        try:
            # 1. SAFE DATA CONVERSION (Prevents NaN crashes)
            # Convert everything to standard python types first
            amount = float(data.get('amount', 0) or 0)
            overdue = int(data.get('days_overdue', 0) or 0)
            history = float(data.get('payment_history_score', 0) or 0)
            vol_change = float(data.get('shipment_volume_change_30d', 0) or 0)

            # 2. CREATE DATAFRAME
            df = pd.DataFrame([{
                'days_overdue': overdue,
                'payment_history_score': history,
                'shipment_volume_change_30d': vol_change,
                'amount': amount,
                'amount_log': np.log1p(amount)
            }])

            # 3. PREDICT (Using Real Model)
            if self.model:
                # Prepare inputs exactly as model wants
                model_input = pd.DataFrame()
                for feature in self.REQUIRED_FEATURES:
                    if feature in df.columns:
                        model_input[feature] = df[feature]
                    else:
                        model_input[feature] = 0.0 # Missing features get 0
                
                # EXECUTE
                prob = float(self.model.predict_proba(model_input)[0][1])
            else:
                raise ValueError("Model failed to load.")

        except Exception as e:
            print(f"⚠️ CALCULATION ERROR: {e}")
            traceback.print_exc()
            # Fallback only if the math breaks, so app stays alive
            prob = float(data.get('payment_history_score', 0.5))

        # 4. FORMAT RESPONSE
        risk_score = 1.0 - prob
        expected_amt = float(data.get('amount', 0)) * prob
        
        if prob > 0.7:
            risk_level = "Low Risk"
            days = 45
        elif prob > 0.4:
            risk_level = "Medium Risk"
            days = 60
        else:
            risk_level = "High Risk"
            days = 90

        # Factors
        factors = []
        ovr = float(data.get('days_overdue', 0))
        if ovr > 60:
            factors.append(TopFactor(feature="days_overdue", impact="Increases Risk", value=ovr))
        else:
            factors.append(TopFactor(feature="days_overdue", impact="Increases Recovery", value=ovr))

        # DCA
        if prob > 0.8:
            dca = DCARecommendation(agency_name="In-House", strategy="Email", estimated_commission="0%")
        else:
            dca = DCARecommendation(agency_name="External", strategy="Call", estimated_commission="15%")

        print(f"✅ Prediction: {prob:.4f}")
        
        return PredictionResponse(
            account_id=str(data.get('account_id', 'UNKNOWN')),
            risk_score=round(risk_score, 2),
            recovery_probability=round(prob, 4),
            risk_level=risk_level,
            expected_recovery_amount=round(expected_amt, 2),
            days_to_pay_prediction=days,
            top_factors=factors,
            dca_recommendation=dca
        )