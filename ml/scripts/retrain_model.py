"""
RECOV.AI - Model Retraining Script (Fixed)
=========================================
Handles training data without outcome column
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from xgboost import XGBClassifier
import joblib
from pathlib import Path
import sys
import os

print("="*70)
print("  RECOV.AI - MODEL RETRAINING")
print("="*70)

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("\n📂 Loading training data...")

# Robust path handling
base_paths = [
    Path("backend/data/training_data.csv"),
    Path("data/training_data.csv"),
    Path("../backend/data/training_data.csv"),
]

data_path = None
for p in base_paths:
    if p.exists():
        data_path = p
        break

if not data_path:
    print("❌ ERROR: training_data.csv not found!")
    sys.exit(1)

df = pd.read_csv(data_path)
print(f"✅ Loaded {len(df)} records from {data_path}")
print(f"   Columns: {list(df.columns)}")

# ============================================================================
# 2. CREATE OUTCOME IF MISSING
# ============================================================================
if 'outcome' not in df.columns:
    print("\n⚠️  'outcome' column not found - generating based on rules...")
    
    # Rule-based outcome generation: 
    df['outcome'] = 0  # Default: no recovery
    
    # Condition for recovery (outcome=1):
    # Payment history > 0.6 AND (shipment_change > 0 OR days_overdue < 45)
    condition_high = (df['payment_history_score'] > 0.8)
    condition_medium = (
        (df['payment_history_score'] > 0.6) & 
        ((df['shipment_volume_change_30d'] > 0) | (df['days_overdue'] < 45))
    )
    
    df.loc[condition_high | condition_medium, 'outcome'] = 1
    
    recovery_count = df['outcome'].sum()
    recovery_pct = recovery_count / len(df) * 100
    
    print(f"   Generated outcomes:")
    print(f"     Recovery (1):    {recovery_count} ({recovery_pct:.1f}%)")
    print(f"     No Recovery (0): {len(df) - recovery_count} ({100-recovery_pct:.1f}%)")
else:
    print(f"\n✅ 'outcome' column found")

# ============================================================================
# 3. FEATURE ENGINEERING
# ============================================================================
print("\n🔧 Engineering features...")

# Create amount_log
df['amount_log'] = np.log1p(df['amount'])

# Fill missing optional columns
optional_cols = {
    'shipment_volume_30d': 0,
    'express_ratio': 0,
    'destination_diversity': 0,
    'contact_attempts': 0,
    'customer_tenure_months': 0
}

for col, default_val in optional_cols.items():
    if col not in df.columns:
        df[col] = default_val
    else:
        df[col] = df[col].fillna(default_val)

# Convert boolean columns
for col in ['email_opened', 'dispute_flag']:
    if col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].map({
                'TRUE': 1, 'FALSE': 0, 'True': 1, 'False': 0,
                '1': 1, '0': 0, True: 1, False: 0
            }).fillna(0).astype(int)
        else:
            df[col] = df[col].astype(int)
    else:
        df[col] = 0

# One-hot encode categoricals
if 'industry' in df.columns:
    industry_dummies = pd.get_dummies(df['industry'], prefix='industry')
    df = pd.concat([df, industry_dummies], axis=1)

if 'region' in df.columns:
    region_dummies = pd.get_dummies(df['region'], prefix='region')
    df = pd.concat([df, region_dummies], axis=1)

# ============================================================================
# 4. PREPARE FEATURES
# ============================================================================
print("\n📊 Preparing feature matrix...")

feature_cols = [
    'amount_log', 'days_overdue', 'payment_history_score',
    'shipment_volume_change_30d', 'shipment_volume_30d',
    'express_ratio', 'destination_diversity', 'contact_attempts',
    'customer_tenure_months', 'email_opened', 'dispute_flag',
]

# Add one-hot encoded
feature_cols.extend([col for col in df.columns if col.startswith('industry_')])
feature_cols.extend([col for col in df.columns if col.startswith('region_')])

available_features = [col for col in feature_cols if col in df.columns]
print(f"✅ Using {len(available_features)} features")

X = df[available_features]
y = df['outcome']

print(f"✅ Feature matrix:  {X.shape}")
print(f"✅ Target: {y.value_counts().to_dict()}")

# ============================================================================
# 5. TRAIN MODEL
# ============================================================================
print("\n🤖 Training XGBoost model...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = XGBClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='logloss',
    use_label_encoder=False
)

model.fit(X_train, y_train)
print("✅ Model trained")

# ============================================================================
# 6. EVALUATE
# ============================================================================
print("\n📈 Evaluating...")

y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)

print(f"✅ Accuracy:   {accuracy:.4f} ({accuracy*100:.1f}%)")
print(f"✅ ROC-AUC:    {roc_auc:.4f}")

# ============================================================================
# 7. SAVE MODEL
# ============================================================================
print("\n💾 Saving model...")

# Find correct models directory
if Path("backend").exists():
    model_dir = Path("backend/models")
else:
    model_dir = Path("models")

model_dir.mkdir(parents=True, exist_ok=True)
model_path = model_dir / "recovery_model.pkl"

model_package = {
    'models': {'classifier': model},
    'feature_names': available_features,
    'metadata': {
        'accuracy': float(accuracy),
        'roc_auc': float(roc_auc),
        'n_features': len(available_features),
    }
}

joblib.dump(model_package, model_path)

print(f"✅ Saved:  {model_path}")
file_size_kb = model_path.stat().st_size / 1024
print(f"   Size: {file_size_kb:.1f} KB")

# ============================================================================
# 8. TEST HERO ACCOUNT
# ============================================================================
print("\n🧪 Testing hero account...")

demo_paths = [Path("backend/data/demo_data.csv"), Path("../../backend/data/demo_data.csv"), Path("data/demo_data.csv")]
demo_path = None
for path in demo_paths:
    if path.exists():
        demo_path = path
        break

if demo_path:
    demo_df = pd.read_csv(demo_path)
    if 'ACC0001' in demo_df['account_id'].values:
        hero = demo_df[demo_df['account_id'] == 'ACC0001'].iloc[0]
        
        print(f"\n📋 Hero Account:")
        print(f"   {hero['company_name']}")
        print(f"   Payment History: {hero['payment_history_score']:.2f}")
        # SAFE CAST TO FLOAT to prevent crash
        print(f"   Shipment Change: {float(hero['shipment_volume_change_30d']):+.2f}")
        
        # Prepare features
        hero_data = {
            'amount_log': np.log1p(hero['amount']),
            'days_overdue': hero['days_overdue'],
            'payment_history_score': hero['payment_history_score'],
            'shipment_volume_change_30d': hero['shipment_volume_change_30d'],
        }
        
        # Fill defaults
        for col in optional_cols.keys():
            hero_data[col] = 0
        
        # Boolean
        for col in ['email_opened', 'dispute_flag']:
            val = str(hero.get(col, '')).upper()
            hero_data[col] = 1 if val == 'TRUE' else 0
        
        hero_df = pd.DataFrame([hero_data])
        
        # One-hot encode
        for feat in available_features:
            if feat.startswith('industry_'):
                industry_val = feat.replace('industry_', '')
                hero_df[feat] = 1 if hero.get('industry', '') == industry_val else 0
            elif feat.startswith('region_'):
                region_val = feat.replace('region_', '')
                hero_df[feat] = 1 if hero.get('region', '') == region_val else 0
            elif feat not in hero_df.columns:
                hero_df[feat] = 0
        
        hero_df = hero_df[available_features]
        
        # Predict
        prob = model.predict_proba(hero_df)[0][1]
        
        print(f"\n🎯 PREDICTION:")
        print(f"   Recovery Probability: {prob:.4f} ({prob*100:.1f}%)")
        
        if prob > 0.7:
            print(f"   ✅ HIGH - Correct! (good history + growth)")
        else:
            print(f"   ⚠️  Low probability despite good indicators")

print("\n" + "="*70)
print("  RETRAINING COMPLETE")
print("="*70)
print("\n✅ Restart backend server:")
print("   cd backend")
print("   python -m uvicorn main:app --reload\n")