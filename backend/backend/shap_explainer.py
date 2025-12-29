import shap
import numpy as np
import pandas as pd
import pickle
from pathlib import Path

class ExplainabilityEngine:
    """
    SHAP-based explainability for recovery predictions. 
    Provides feature importance and contribution scores for individual predictions.
    """
    
    def __init__(self, model_path: str = 'backend/models/recovery_model.pkl'):
        """Load model and create SHAP explainer"""
        self.model_path = Path(model_path)
        self.model = None
        self.explainer = None
        self.feature_names = None
        
        self._load_resources()
    
    def _load_resources(self):
        # robust path finding
        if not self.model_path.exists():
             # Try alternative paths
            alt_paths = [
                Path("models/recovery_model.pkl"),
                Path("../backend/models/recovery_model.pkl")
            ]
            for p in alt_paths:
                if p.exists():
                    self.model_path = p
                    break
        
        if not self.model_path.exists():
            print(f"⚠️ Warning: Model not found at {self.model_path}. Explainer disabled.")
            return

        with open(self.model_path, 'rb') as f:
            pkg = pickle.load(f)
            self.model = pkg['models']['classifier']
            self.feature_names = pkg['feature_names']
            
        # Create TreeExplainer (optimized for XGBoost)
        # We pass the model directly
        try:
            self.explainer = shap.TreeExplainer(self.model)
        except Exception as e:
            print(f"⚠️ SHAP Explainer init failed: {e}")

    def explain_prediction(self, account_features: pd.DataFrame) -> dict:
        """
        Explain a single account prediction.
        """
        if not self.explainer:
            return {}

        # Calculate SHAP values
        shap_values = self.explainer.shap_values(account_features)
        
        # Handle different SHAP output formats (binary classification sometimes returns list)
        if isinstance(shap_values, list):
            sv = shap_values[1][0] # Positive class
        elif len(shap_values.shape) > 1:
            sv = shap_values[0]
        else:
            sv = shap_values

        base_value = self.explainer.expected_value
        if isinstance(base_value, list):
            base_value = base_value[1]
            
        # Get top factors
        top_factors = self.get_top_factors(sv, self.feature_names)
        
        return {
            'top_factors': top_factors,
            'base_value': float(base_value),
            'prediction': float(base_value + sv.sum())
        }
    
    def get_top_factors(self, shap_values: np.ndarray, feature_names: list, top_n: int = 5) -> list:
        """Extract top N contributing factors."""
        # Pair values with names
        feature_importance = list(zip(feature_names, shap_values))
        
        # Sort by absolute impact (magnitude)
        feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
        
        factors = []
        for feature, impact in feature_importance[:top_n]:
            factors.append({
                'feature': self.format_feature_name(feature),
                'impact': float(impact),
                'direction': 'positive' if impact > 0 else 'negative',
                'raw_impact': float(impact)
            })
            
        return factors

    def format_feature_name(self, feature: str) -> str:
        """Convert technical feature names to human-readable"""
        display_map = {
            'shipment_volume_change_30d': 'Shipping Trend (30d)',
            'payment_history_score': 'Payment History',
            'days_overdue': 'Days Overdue',
            'amount_log': 'Invoice Amount',
            'express_ratio': 'Express Shipping Usage',
            'destination_diversity': 'Customer Base Diversity'
        }
        return display_map.get(feature, feature)

# Test function
if __name__ == "__main__":
    print("Testing SHAP Explainer...")
    try:
        explainer = ExplainabilityEngine()
        
        # Create dummy data (all zeros) just to test structure
        # In real use, we pass the dataframe from the predictor
        dummy_data = pd.DataFrame(np.zeros((1, 23)), columns=explainer.feature_names)
        
        explanation = explainer.explain_prediction(dummy_data)
        print("\n✅ SHAP Explanation Generated:")
        for f in explanation['top_factors']:
            print(f"  {f['direction'].upper()}: {f['feature']} (Impact: {f['impact']:.4f})")
            
    except Exception as e:
        print(f"❌ Test Failed: {e}")