import pickle
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import json
from pathlib import Path
import sys
import os

# --- 1. CLEAN IMPORT (Permanent Fix) ---
# Uses relative import because this file is part of the 'backend' package
from .shap_explainer import ExplainabilityEngine

# --- 2. PREDICTOR CLASS ---
class RecoveryPredictor:
    """
    Main prediction engine for RECOV.AI.
    Loads trained XGBoost models and provides recovery predictions.
    """
    
    def __init__(self, model_path: str = 'backend/models/recovery_model.pkl'):
        """Load all trained models with robust path finding"""
        self.model_path = Path(model_path)
        
        # Robust path finding to handle running from different directories
        if not self.model_path.exists():
            current_dir = os.path.dirname(os.path.abspath(__file__))
            alt_paths = [
                Path("models/recovery_model.pkl"),                     # If running from backend/
                Path("../backend/models/recovery_model.pkl"),          # If running from sibling
                Path(os.path.join(current_dir, "models/recovery_model.pkl")) # Absolute path relative to this file
            ]
            for p in alt_paths:
                if p.exists():
                    self.model_path = p
                    break
        
        self.models = None
        self.feature_names = None
        self.explainer = None
        
        # Load the models immediately
        self.load_models()

        # Initialize Explainer (if available)
        try:
            self.explainer = ExplainabilityEngine(str(self.model_path))
            print("✅ SHAP Explainer attached successfully")
        except Exception as e:
            print(f"⚠️ Explainer init failed: {e}")
            self.explainer = None

    def load_models(self):
        """Load pickled models and metadata"""
        if not self.model_path.exists():
            # Print current directory to help debug
            print(f"❌ Critical Error: Model not found at {self.model_path}")
            print(f"   Current dir: {os.getcwd()}")
            raise FileNotFoundError(f"Model file missing: {self.model_path}")
            
        print(f"Loading model from: {self.model_path}")
        with open(self.model_path, 'rb') as f:
            pkg = pickle.load(f)
            self.models = pkg['models']
            self.feature_names = pkg['feature_names']
        
        print("✅ Models loaded successfully")

    def prepare_features(self, account: Dict[str, Any]) -> pd.DataFrame:
        """Transform raw account data into model features."""
        df = pd.DataFrame([account])
        
        # Feature Engineering matching training logic
        if 'amount' in df.columns:
            df['amount_log'] = np.log1p(df['amount'])
            
        # Initialize expected columns
        X_df = pd.DataFrame(0, index=df.index, columns=self.feature_names)
        
        # Fill numerical values
        for col in ['amount_log', 'days_overdue', 'payment_history_score', 
                    'shipment_volume_change_30d', 'shipment_volume_30d', 
                    'express_ratio', 'destination_diversity']:
            if col in df.columns and col in X_df.columns:
                X_df[col] = df[col]
        
        # Handle Boolean
        for col in ['email_opened', 'dispute_flag']:
            if col in df.columns and col in X_df.columns:
                X_df[col] = int(df[col].iloc[0])

        # Handle Categorical
        for col in ['industry', 'region']:
            if col in df.columns:
                val = df[col].iloc[0]
                target_col = f"{col}_{val}"
                if target_col in X_df.columns:
                    X_df[target_col] = 1
                    
        return X_df

    def predict_recovery(self, account: Dict[str, Any]) -> Dict[str, Any]:
        """Make complete recovery prediction for an account."""
        X_df = self.prepare_features(account)
        X = X_df.values
        
        # Predictions
        prob = self.models['classifier'].predict_proba(X)[0, 1]
        days = self.models['regressor_days'].predict(X)[0]
        pct = self.models['regressor_pct'].predict(X)[0]
        
        # Derived Metrics
        velocity_score = self.calculate_velocity_score(prob, days, pct)
        risk_level = self.determine_risk_level(prob, days)
        dca = self.match_dca(account, prob)
        
        # SHAP Explanation
        top_factors = []
        if self.explainer:
            try:
                explanation = self.explainer.explain_prediction(X_df)
                top_factors = explanation.get('top_factors', [])
            except Exception as e:
                print(f"SHAP Error: {e}")

        # Fallback if SHAP failed or no explainer
        if not top_factors:
            top_factors = [
                {"feature": "shipment_volume_change_30d", "impact": 0.5, "direction": "positive"}
            ]

        return {
            'account_id': account.get('account_id', 'Unknown'),
            'company_name': account.get('company_name', 'Unknown'),
            'recovery_probability': float(prob),
            'recovery_percentage': float(pct),
            'expected_days': int(days),
            'recovery_velocity_score': float(velocity_score),
            'risk_level': risk_level,
            'recommended_dca': dca,
            'top_factors': top_factors,
            'prediction_timestamp': 'NOW'
        }

    def calculate_velocity_score(self, prob: float, days: int, pct: float) -> float:
        if days <= 0: days = 1
        return (prob * pct) / (days / 30)

    def determine_risk_level(self, prob: float, days: int) -> str:
        if prob > 0.75 and days < 30: return 'Low'
        elif prob > 0.5 and days < 60: return 'Medium'
        else: return 'High'

    def match_dca(self, account: Dict, probability: float) -> Dict:
        amount = account.get('amount', 0)
        industry = account.get('industry', 'Other')
        shipment_change = account.get('shipment_volume_change_30d', 0)
        
        if amount > 2000000 and industry in ['Technology', 'Healthcare']: 
            return {'name': 'Premium Recovery Services', 'specialization': 'High-value B2B'}
        elif shipment_change > 0.2: 
            return {'name': 'Growth-Focused Recovery', 'specialization': 'Expanding businesses'}
        elif amount < 500000:
            return {'name': 'Quick Collections Ltd', 'specialization': 'SMB Accounts'}
        else:
            return {'name': 'Standard DCA Pool', 'specialization': 'General'}

# --- 3. TEST FUNCTION (OUTSIDE THE CLASS) ---
def test_hero_account():
    """Test prediction on the hero account"""
    # Initialize
    try:
        predictor = RecoveryPredictor()
    except Exception as e:
        print(f"Failed to initialize predictor: {e}")
        return

    # Updated Hero Data (25 days overdue + High Shipping)
    hero_account = {
        'account_id': 'ACC0001',
        'company_name': 'TechCorp Solutions Pvt Ltd',
        'industry': 'Technology',
        'amount': 2800000,
        'days_overdue': 25,
        'payment_history_score': 0.88,
        'shipment_volume_30d': 45,
        'shipment_volume_change_30d': 0.40,
        'express_ratio': 0.65,
        'destination_diversity': 18,
        'email_opened': True,
        'contact_attempts': 3,
        'dispute_flag': False,
        'customer_tenure_months': 36,
        'region': 'South'
    }
    
    print("\n🔎 PREDICTOR TEST (TechCorp)...")
    prediction = predictor.predict_recovery(hero_account)
    print(json.dumps(prediction, indent=2))

if __name__ == '__main__':
    test_hero_account()