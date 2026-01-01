"""
RECOV. AI - SHAP Explainability Engine
=====================================
Provides SHAP-based explanations for XGBoost model predictions. 
Falls back gracefully if SHAP is unavailable.
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path

# Try to import SHAP (optional dependency)
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError: 
    SHAP_AVAILABLE = False
    print("⚠️ SHAP not installed. Using fallback explanations.")


class ExplainabilityEngine:
    """
    SHAP-based explanation engine for XGBoost models.
    Provides interpretable feature importance for predictions.
    """
    
    def __init__(self, model_path: str):
        """
        Initialize explainer and load model.
        
        Args:
            model_path:  Path to pickled model file
        """
        self.model = None
        self.explainer = None
        self.feature_names = None
        self. shap_available = SHAP_AVAILABLE
        
        # Load model
        self._load_model(model_path)
        
        # Initialize SHAP explainer if available
        if self.shap_available and self.model:
            self._initialize_explainer()

    def _load_model(self, model_path:  str):
        """
        Load pickled model and extract feature names.
        
        Handles multiple pickle structures:
        - {'models': {... }, 'feature_names': [...]}
        - {'model': ..., 'features': [...]}
        - Direct model object
        """
        try: 
            # Convert to Path object for better handling
            model_file = Path(model_path)
            
            # Find model file (handle different working directories)
            if not model_file.exists():
                alt_paths = [
                    Path("models/recovery_model.pkl"),
                    Path("backend/models/recovery_model.pkl"),
                    Path("../backend/models/recovery_model.pkl"),
                    Path(__file__).parent / "models" / "recovery_model.pkl"
                ]
                for p in alt_paths:
                    if p.exists():
                        model_file = p
                        break
            
            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found:  {model_path}")
            
            # Load pickle
            with open(model_file, 'rb') as f:
                pkg = pickle.load(f)
            
            # Extract model and features based on structure
            if isinstance(pkg, dict):
                # Structure 1: {'models': {'classifier':  ...}, 'feature_names':  [...]}
                if 'models' in pkg: 
                    self.model = pkg['models'].get('classifier')
                    self.feature_names = pkg. get('feature_names', [])
                # Structure 2: {'model': .. ., 'features': [...]}
                elif 'model' in pkg:
                    self.model = pkg['model']
                    self.feature_names = pkg.get('features', pkg.get('feature_names', []))
                # Structure 3: Direct dict with classifier key
                else:
                    self.model = pkg. get('classifier', pkg)
                    self.feature_names = pkg.get('feature_names', [])
            else:
                # Direct model object
                self.model = pkg
                # Try to extract feature names from model
                try:
                    self.feature_names = self.model.get_booster().feature_names
                except: 
                    self.feature_names = []
            
            if not self.model:
                raise ValueError("Could not extract model from pickle file")
            
            print(f"✅ Model loaded for SHAP:  {type(self.model).__name__}")
            if self.feature_names:
                print(f"   Features: {len(self.feature_names)} columns")
            
        except Exception as e:
            print(f"❌ SHAP Engine Model Load Error: {e}")
            self.model = None
            self.feature_names = []

    def _initialize_explainer(self):
        """
        Initialize SHAP TreeExplainer for the model.
        Handles errors gracefully.
        """
        if not self.shap_available:
            print("⚠️ SHAP not available - using fallback")
            return
        
        try:
            # Initialize TreeExplainer (optimized for tree-based models)
            self.explainer = shap.TreeExplainer(self.model)
            print("✅ SHAP TreeExplainer initialized")
            
        except Exception as e:
            print(f"⚠️ Could not initialize SHAP TreeExplainer: {e}")
            self.explainer = None

    def explain_prediction(self, X_df: pd.DataFrame) -> dict:
        """
        Generate SHAP values for a prediction and return top factors.
        
        Args:
            X_df: DataFrame with single row of features (already prepared)
        
        Returns: 
            dict: {
                'top_factors': [
                    {'feature': str, 'impact':  float, 'direction': str},
                    ...
                ],
                'base_value': float (optional)
            }
        """
        # Validation
        if X_df is None or X_df.empty:
            print("⚠️ Empty DataFrame provided to SHAP explainer")
            return {'top_factors': []}
        
        if not self.explainer:
            print("⚠️ SHAP explainer not initialized - using fallback")
            return self._fallback_explanation(X_df)
        
        try:
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(X_df)
            
            # Handle different SHAP output formats
            # Binary classification: list [class0_values, class1_values]
            # Multiclass: list of arrays
            # Regression: single array
            if isinstance(shap_values, list):
                # For binary classification, use positive class (index 1)
                if len(shap_values) == 2:
                    vals = shap_values[1]
                else: 
                    vals = shap_values[0]
            else:
                vals = shap_values
            
            # Extract values for single prediction
            if len(vals. shape) > 1:
                vals = vals[0]  # First row
            
            # Map SHAP values to feature names
            feature_importance = []
            feature_names = X_df.columns.tolist()
            
            for i, (name, val) in enumerate(zip(feature_names, vals)):
                # Skip features with zero impact
                if abs(val) < 1e-10:
                    continue
                
                # Get actual feature value
                feature_value = X_df. iloc[0, i]
                
                feature_importance.append({
                    "feature": self._clean_feature_name(name),
                    "impact": float(val),
                    "direction": "positive" if val > 0 else "negative",
                    "feature_value": float(feature_value) if isinstance(feature_value, (int, float)) else str(feature_value)
                })
            
            # Sort by absolute impact magnitude
            feature_importance. sort(key=lambda x: abs(x['impact']), reverse=True)
            
            # Get base value (expected model output)
            try:
                if isinstance(self.explainer.expected_value, (list, np.ndarray)):
                    base_value = float(self.explainer.expected_value[-1])
                else:
                    base_value = float(self.explainer.expected_value)
            except:
                base_value = 0.5  # Default for binary classification
            
            return {
                'top_factors': feature_importance[:5],  # Top 5 factors
                'base_value': base_value
            }
            
        except Exception as e:
            print(f"⚠️ SHAP Calculation Error:  {e}")
            # Fallback to feature importances
            return self._fallback_explanation(X_df)

    def _fallback_explanation(self, X_df: pd.DataFrame) -> dict:
        """
        Fallback explanation using model feature importances.
        Used when SHAP is unavailable or fails.
        """
        try:
            # Get feature importances from model
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
            elif hasattr(self.model, 'get_score'):
                # XGBoost-specific method
                importance_dict = self.model.get_score(importance_type='weight')
                importances = [importance_dict.get(f, 0) for f in X_df.columns]
            else:
                # Ultimate fallback:  use non-zero features
                importances = np.abs(X_df.iloc[0]. values)
            
            # Create feature importance list
            feature_importance = []
            for i, (name, imp) in enumerate(zip(X_df.columns, importances)):
                if abs(imp) < 1e-10:
                    continue
                
                feature_value = X_df.iloc[0, i]
                
                feature_importance.append({
                    "feature": self._clean_feature_name(name),
                    "impact": float(imp),
                    "direction": "positive" if feature_value > 0 else "neutral",
                    "feature_value":  float(feature_value) if isinstance(feature_value, (int, float)) else str(feature_value)
                })
            
            # Sort by importance
            feature_importance.sort(key=lambda x: abs(x['impact']), reverse=True)
            
            return {
                'top_factors': feature_importance[:5],
                'base_value':  0.5,
                'method': 'feature_importance_fallback'
            }
            
        except Exception as e: 
            print(f"⚠️ Fallback explanation also failed: {e}")
            # Ultimate fallback: return empty
            return {'top_factors': []}

    def _clean_feature_name(self, name: str) -> str:
        """
        Convert technical feature names to human-readable format.
        
        Examples:
            'amount_log' -> 'Invoice Amount'
            'shipment_volume_change_30d' -> 'Shipment Volume Change (30d)'
            'industry_Technology' -> 'Industry:  Technology'
        """
        # Feature name mappings
        name_map = {
            'amount_log': 'Invoice Amount (log)',
            'amount':  'Invoice Amount',
            'days_overdue': 'Days Overdue',
            'payment_history_score': 'Payment History Score',
            'shipment_volume_change_30d': 'Shipment Volume Change (30d)',
            'shipment_volume_30d': 'Shipment Volume (30d)',
            'express_ratio': 'Express Shipment Ratio',
            'destination_diversity': 'Shipping Destination Diversity',
            'email_opened': 'Email Engagement',
            'dispute_flag': 'Dispute History'
        }
        
        # Check direct mapping
        if name in name_map: 
            return name_map[name]
        
        # Handle one-hot encoded features (e.g., 'industry_Technology')
        if '_' in name:
            parts = name.split('_', 1)
            if len(parts) == 2:
                category, value = parts
                if category in ['industry', 'region']:
                    return f"{category. title()}: {value}"
        
        # Default:  title case with underscores replaced
        return name.replace('_', ' ').title()

    def get_summary(self) -> dict:
        """
        Get summary of explainer status.
        
        Returns:
            dict: Status information
        """
        return {
            'shap_available': self.shap_available,
            'explainer_initialized': self.explainer is not None,
            'model_loaded':  self.model is not None,
            'feature_count': len(self.feature_names) if self.feature_names else 0,
            'model_type': type(self.model).__name__ if self.model else None
        }


# ============================================================================
# STANDALONE TESTING
# ============================================================================

if __name__ == "__main__": 
    """Test SHAP explainer"""
    print("🧪 Testing SHAP Explainer...")
    
    # Test with sample data
    test_data = pd.DataFrame([{
        'amount_log': 12.5,
        'days_overdue': 45,
        'payment_history_score':  0.75,
        'shipment_volume_change_30d': 0.3,
        'email_opened': 1,
        'dispute_flag':  0
    }])
    
    try:
        engine = ExplainabilityEngine('models/recovery_model.pkl')
        print(f"\n✅ Engine Status: {engine.get_summary()}")
        
        explanation = engine.explain_prediction(test_data)
        print(f"\n📊 Explanation:")
        print(f"   Top Factors: {len(explanation['top_factors'])}")
        for factor in explanation['top_factors'][:3]:
            print(f"     • {factor['feature']}: {factor['impact']:.4f} ({factor['direction']})")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")