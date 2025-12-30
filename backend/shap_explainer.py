import pandas as pd
import numpy as np
import shap
import pickle

class ExplainabilityEngine:
    """
    SHAP-based explanation engine for XGBoost models.
    """
    def __init__(self, model_path: str):
        self.model = None
        self.explainer = None
        self.feature_names = None
        self._load_model(model_path)

    def _load_model(self, model_path):
        try:
            with open(model_path, 'rb') as f:
                pkg = pickle.load(f)
                # handle different pickle structures
                if isinstance(pkg, dict):
                    self.model = pkg.get('models', {}).get('classifier') or pkg.get('model')
                    self.feature_names = pkg.get('feature_names', [])
                else:
                    self.model = pkg
            
            if self.model:
                # Initialize TreeExplainer for XGBoost/Tree models
                try:
                    self.explainer = shap.TreeExplainer(self.model)
                except Exception as e:
                    print(f"⚠️ Could not initialize TreeExplainer: {e}")
                    self.explainer = None
        except Exception as e:
            print(f"⚠️ SHAP Engine Load Error: {e}")

    def explain_prediction(self, X_df: pd.DataFrame):
        """
        Generate SHAP values for a single prediction and return top factors.
        """
        if not self.explainer or X_df.empty:
            return {'top_factors': []}

        try:
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(X_df)
            
            # Handle different SHAP output shapes (binary vs multiclass)
            if isinstance(shap_values, list):
                # Binary classification usually returns list [class0, class1]
                vals = shap_values[1][0] 
            elif len(shap_values.shape) > 1:
                vals = shap_values[0]
            else:
                vals = shap_values

            # Map values to features
            feature_importance = []
            for name, val in zip(X_df.columns, vals):
                feature_importance.append({
                    "feature": name,
                    "impact": float(val),
                    "direction": "positive" if val > 0 else "negative"
                })

            # Sort by absolute impact magnitude
            feature_importance.sort(key=lambda x: abs(x['impact']), reverse=True)
            
            return {
                'top_factors': feature_importance[:3], # Return top 3
                'base_value': float(self.explainer.expected_value[-1] if isinstance(self.explainer.expected_value, list) else self.explainer.expected_value)
            }
        except Exception as e:
            print(f"⚠️ SHAP Calculation Error: {e}")
            return {'top_factors': []}