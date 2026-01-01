import pandas as pd
import numpy as np
import pickle
import json
import os
from pathlib import Path
from xgboost import XGBClassifier, XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

# --- CONFIG ---
# Automatically find the project root based on where this file is
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = BASE_DIR / "backend" / "data" / "training_data.csv"
MODEL_PATH = BASE_DIR / "backend" / "models" / "recovery_model.pkl"
METADATA_PATH = BASE_DIR / "backend" / "models" / "model_metadata.json"

def load_and_prep_data():
    print(f"✅ Loading data from: {DATA_PATH}")
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"❌ Data file not found at {DATA_PATH}")
        
    df = pd.read_csv(DATA_PATH)
    
    # --- 1. AUTO-FIX: Generate 'outcome' if missing ---
    if 'outcome' not in df.columns:
        print("⚠️ 'outcome' column missing. Generating synthetic labels based on logic...")
        # Rule: If payment history is good (>0.6) AND not too overdue (<70 days), they likely pay (1)
        df['outcome'] = np.where(
            (df['payment_history_score'] > 0.60) & (df['days_overdue'] < 70), 
            1, 
            0
        )
        print("✅ Synthetic 'outcome' labels generated.")

    # --- 2. AUTO-FIX: Generate Regression Targets ---
    print("🔄 Generating synthetic regression targets...")
    np.random.seed(42)
    
    # Recovery Percentage: High for outcome 1, Low for outcome 0
    df['recovery_percentage'] = np.where(
        df['outcome'] == 1,
        np.random.uniform(0.7, 1.0, size=len(df)),
        np.random.uniform(0.0, 0.4, size=len(df))
    )
    
    # Days to Pay: Low for outcome 1, High for outcome 0
    random_lag = np.random.randint(5, 30, size=len(df))
    df['days_to_pay'] = np.where(
        df['outcome'] == 1,
        df['days_overdue'] + random_lag,
        180 # Cap for non-payment
    )
    
    # --- 3. Feature Engineering ---
    if 'amount' in df.columns:
        df['amount_log'] = np.log1p(df['amount'])
    
    df.fillna(0, inplace=True)
    return df

def train():
    df = load_and_prep_data()
    
    # Define Features (Updated to match your new Day 1 Schema)
    features = [
        'amount_log', 'days_overdue', 'payment_history_score', 
        'shipment_volume_change_30d', 'shipment_volume_30d', 
        'express_ratio', 'destination_diversity', 
        'contact_attempts', 'customer_tenure_months'
    ]
    
    # Verify columns exist
    available_features = [f for f in features if f in df.columns]
    print(f"features used: {available_features}")
    
    X = df[available_features]
    y_class = df['outcome']
    y_days = df['days_to_pay']
    y_pct = df['recovery_percentage']
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y_class, test_size=0.2, random_state=42)
    _, _, y_days_train, y_days_test = train_test_split(X, y_days, test_size=0.2, random_state=42)
    _, _, y_pct_train, y_pct_test = train_test_split(X, y_pct, test_size=0.2, random_state=42)
    
    # --- 1. Train Classifier (Risk Level) ---
    print("\n🤖 Training XGBoost Classifier...")
    clf = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, use_label_encoder=False, eval_metric='logloss')
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_pred)
    
    print(f"   🏆 Classifier Accuracy: {acc:.4f}")
    print(f"   🏆 ROC-AUC Score: {roc:.4f}")

    # --- 2. Train Regressors (Days & %) ---
    print("\n🤖 Training XGBoost Regressors...")
    reg_days = XGBRegressor(n_estimators=100, max_depth=5)
    reg_days.fit(X_train, y_days_train)
    
    reg_pct = XGBRegressor(n_estimators=100, max_depth=5)
    reg_pct.fit(X_train, y_pct_train)
    
    print("   ✅ Regressors Trained")

    # --- 3. Save Everything ---
    model_pkg = {
        'models': {
            'classifier': clf,
            'regressor_days': reg_days,
            'regressor_pct': reg_pct
        },
        'feature_names': available_features
    }
    
    # Create directory if it doesn't exist
    os.makedirs(MODEL_PATH.parent, exist_ok=True)
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model_pkg, f)
        
    print(f"\n💾 Model saved to {MODEL_PATH}")
    
    # Save Metadata
    meta = {
        'accuracy': float(acc),
        'roc_auc': float(roc),
        'features': available_features
    }
    with open(METADATA_PATH, 'w') as f:
        json.dump(meta, f, indent=2)

if __name__ == "__main__":
    train()