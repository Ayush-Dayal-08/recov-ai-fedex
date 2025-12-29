#!/usr/bin/env python3
"""
RECOV.AI - XGBoost Model Training Script
==========================================
This script trains a multi-output prediction model for debt recovery:
1. Recovery Probability (Classification: 0-1)
2. Days to Recovery (Regression: 10-60 days)
3. Recovery Percentage (Regression: 0.7-1.0)
"""

# =============================================================================
# 1. IMPORTS
# =============================================================================
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, 
    roc_auc_score, 
    classification_report,
    precision_recall_fscore_support,
    confusion_matrix,
    mean_absolute_error, 
    mean_squared_error,
    r2_score
)
from xgboost import XGBClassifier, XGBRegressor
import pickle
import json
from datetime import datetime
from pathlib import Path
import warnings
import sys
import os

warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION
# =============================================================================
class Config:
    """Configuration settings for model training."""
    
    # Paths
    DATA_PATH = Path("backend/data/training_data.csv")
    MODEL_OUTPUT_PATH = Path("backend/models/recovery_model.pkl")
    METADATA_OUTPUT_PATH = Path("backend/models/model_metadata.json")
    
    # Model parameters
    RANDOM_STATE = 42
    TEST_SIZE = 0.30
    
    # XGBoost Classifier parameters
    CLASSIFIER_PARAMS = {
        'n_estimators': 100,
        'max_depth': 5,
        'learning_rate': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42,
        'eval_metric': 'logloss',
        'use_label_encoder': False
    }
    
    # XGBoost Regressor parameters (Days)
    REGRESSOR_DAYS_PARAMS = {
        'n_estimators': 100,
        'max_depth': 4,
        'learning_rate': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42
    }
    
    # XGBoost Regressor parameters (Percentage)
    REGRESSOR_PCT_PARAMS = {
        'n_estimators': 80,
        'max_depth': 4,
        'learning_rate': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42
    }
    
    # Features
    SHIPPING_FEATURES = [
        'shipment_volume_30d',
        'shipment_volume_change_30d',
        'express_ratio',
        'destination_diversity'
    ]
    
    NUMERICAL_FEATURES = [
        'amount',
        'days_overdue',
        'payment_history_score'
    ]
    
    CATEGORICAL_FEATURES = [
        'industry',
        'region'
    ]
    
    BOOLEAN_FEATURES = [
        'email_opened',
        'dispute_flag'
    ]

# =============================================================================
# 2. FEATURE ENGINEERING FUNCTION
# =============================================================================
def engineer_features(df: pd.DataFrame, fit_encoders: bool = True, encoders: dict = None) -> tuple:
    """
    Transform raw dataframe into feature matrix for model training.
    """
    print("\n" + "="*60)
    print("FEATURE ENGINEERING")
    print("="*60)
    
    df_processed = df.copy()
    
    if encoders is None:
        encoders = {}
    
    # 2.1 Log Transform Amount
    df_processed['amount_log'] = np.log1p(df_processed['amount'])
    print("✓ Created: amount_log (log transform)")
    
    # 2.2 Days Overdue Categories
    bins_days = [0, 30, 60, 90, float('inf')]
    labels_days = ['0-30', '30-60', '60-90', '90+']
    df_processed['days_overdue_category'] = pd.cut(
        df_processed['days_overdue'], 
        bins=bins_days, 
        labels=labels_days,
        include_lowest=True
    )
    print("✓ Created: days_overdue_category (bins: 0-30, 30-60, 60-90, 90+)")
    
    # 2.3 Payment History Categories
    bins_payment = [0, 0.4, 0.6, 0.8, 1.0]
    labels_payment = ['poor', 'fair', 'good', 'excellent']
    df_processed['payment_history_category'] = pd.cut(
        df_processed['payment_history_score'],
        bins=bins_payment,
        labels=labels_payment,
        include_lowest=True
    )
    print("✓ Created: payment_history_category (poor, fair, good, excellent)")
    
    # 2.4 Keep Shipping Features As-Is
    for feature in Config.SHIPPING_FEATURES:
        if feature in df_processed.columns:
            print(f"✓ Kept: {feature} (shipping feature)")
    
    # 2.5 One-Hot Encode Categorical Features
    categorical_to_encode = Config.CATEGORICAL_FEATURES + ['days_overdue_category', 'payment_history_category']
    
    for col in categorical_to_encode:
        if col in df_processed.columns:
            if fit_encoders:
                dummies = pd.get_dummies(df_processed[col], prefix=col, drop_first=False)
                encoders[f'{col}_columns'] = dummies.columns.tolist()
            else:
                dummies = pd.get_dummies(df_processed[col], prefix=col, drop_first=False)
                for expected_col in encoders.get(f'{col}_columns', []):
                    if expected_col not in dummies.columns:
                        dummies[expected_col] = 0
                dummies = dummies[[c for c in encoders.get(f'{col}_columns', []) if c in dummies.columns]]
            
            df_processed = pd.concat([df_processed, dummies], axis=1)
            print(f"✓ One-hot encoded: {col} → {len(dummies.columns)} columns")
    
    # 2.6 Boolean to Integer
    for col in Config.BOOLEAN_FEATURES:
        if col in df_processed.columns:
            df_processed[col] = df_processed[col].astype(int)
            print(f"✓ Converted: {col} (bool → int)")
    
    # 2.7 Build Final Feature Matrix
    feature_columns = []
    feature_columns.extend(['amount_log', 'days_overdue', 'payment_history_score'])
    feature_columns.extend([f for f in Config.SHIPPING_FEATURES if f in df_processed.columns])
    feature_columns.extend([f for f in Config.BOOLEAN_FEATURES if f in df_processed.columns])
    
    for col in categorical_to_encode:
        encoded_cols = [c for c in df_processed.columns if c.startswith(f'{col}_')]
        feature_columns.extend(encoded_cols)
    
    feature_columns = list(dict.fromkeys(feature_columns))
    feature_columns = [c for c in feature_columns if c in df_processed.columns]
    
    X = df_processed[feature_columns].values
    print(f"\n📊 Final feature matrix shape: {X.shape}")
    
    return X, feature_columns, encoders

def generate_synthetic_targets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate synthetic regression targets based on outcome.
    """
    print("\n" + "="*60)
    print("GENERATING SYNTHETIC REGRESSION TARGETS")
    print("="*60)
    
    np.random.seed(Config.RANDOM_STATE)
    df_copy = df.copy()
    
    # Days to recover
    df_copy['days_to_recover'] = np.where(
        df_copy['outcome'] == 1,
        np.random.randint(15, 46, size=len(df_copy)),  # 15-45 days for paid
        np.random.randint(60, 121, size=len(df_copy))   # 60-120 days for not paid
    )
    
    # Recovery percentage
    df_copy['recovery_percentage'] = np.where(
        df_copy['outcome'] == 1,
        np.random.uniform(0.85, 1.0, size=len(df_copy)),
        np.random.uniform(0.0, 0.5, size=len(df_copy))
    )
    
    print(f"✓ Created: days_to_recover and recovery_percentage")
    return df_copy

# =============================================================================
# 3. MODEL TRAINING
# =============================================================================
def train_models(X_train, X_test, y_train_class, y_test_class, 
                 y_train_days, y_test_days, y_train_pct, y_test_pct):
    """
    Train all three models: classifier and two regressors.
    """
    print("\n" + "="*60)
    print("MODEL TRAINING")
    print("="*60)
    
    models = {}
    metrics = {}
    
    # 3.1 PRIMARY MODEL: Recovery Probability
    print("\n📊 Training PRIMARY MODEL: Recovery Probability Classifier...")
    classifier = XGBClassifier(**Config.CLASSIFIER_PARAMS)
    classifier.fit(X_train, y_train_class)
    
    y_pred_class = classifier.predict(X_test)
    y_pred_proba = classifier.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test_class, y_pred_class)
    roc_auc = roc_auc_score(y_test_class, y_pred_proba)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test_class, y_pred_class, average='binary')
    
    print(f"✓ Accuracy:  {accuracy:.4f}")
    
    models['classifier'] = classifier
    metrics['classifier'] = {'accuracy': float(accuracy), 'roc_auc': float(roc_auc), 'f1_score': float(f1)}
    
    # 3.2 SECONDARY MODEL: Days to Recovery
    print("\n📊 Training SECONDARY MODEL: Days to Recovery Regressor...")
    regressor_days = XGBRegressor(**Config.REGRESSOR_DAYS_PARAMS)
    regressor_days.fit(X_train, y_train_days)
    y_pred_days = regressor_days.predict(X_test)
    mae_days = mean_absolute_error(y_test_days, y_pred_days)
    
    print(f"✓ MAE:  {mae_days:.2f} days")
    models['regressor_days'] = regressor_days
    metrics['regressor_days'] = {'mae': float(mae_days)}
    
    # 3.3 TERTIARY MODEL: Recovery Percentage
    print("\n📊 Training TERTIARY MODEL: Recovery Percentage Regressor...")
    regressor_pct = XGBRegressor(**Config.REGRESSOR_PCT_PARAMS)
    regressor_pct.fit(X_train, y_train_pct)
    y_pred_pct = regressor_pct.predict(X_test)
    mae_pct = mean_absolute_error(y_test_pct, y_pred_pct)
    
    print(f"✓ MAE:  {mae_pct:.4f} ({mae_pct*100:.2f}%)")
    models['regressor_pct'] = regressor_pct
    metrics['regressor_pct'] = {'mae': float(mae_pct)}
    
    return models, metrics

# =============================================================================
# 4. SAVE & ANALYZE
# =============================================================================
def save_model(models, feature_names, encoders, metrics):
    print("\n" + "="*60)
    print("SAVING MODEL")
    print("="*60)
    
    Config.MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    model_package = {
        'models': models,
        'feature_names': feature_names,
        'encoders': encoders,
        'version': '1.0.0',
        'trained_at': datetime.now().isoformat()
    }
    
    with open(Config.MODEL_OUTPUT_PATH, 'wb') as f:
        pickle.dump(model_package, f)
    
    print(f"✅ Model saved to: {Config.MODEL_OUTPUT_PATH}")
    
    # Save Metadata
    metadata = {
        'training_date': datetime.now().isoformat(),
        'performance': metrics
    }
    with open(Config.METADATA_OUTPUT_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Metadata saved to: {Config.METADATA_OUTPUT_PATH}")

def main():
    print("="*70)
    print("       RECOV.AI - MODEL TRAINING PIPELINE")
    print("="*70)
    
    # Load Data
    if not Config.DATA_PATH.exists():
        # Fallback paths
        possible_paths = [Path("../../backend/data/training_data.csv"), Path("../backend/data/training_data.csv")]
        for p in possible_paths:
            if p.exists():
                Config.DATA_PATH = p
                break
    
    try:
        df = pd.read_csv(Config.DATA_PATH)
        print(f"✅ Loaded data from: {Config.DATA_PATH}")
    except:
        print(f"❌ ERROR: Could not find training_data.csv")
        return

    # Generate Targets
    df = generate_synthetic_targets(df)
    
    # Feature Engineering
    X, feature_names, encoders = engineer_features(df, fit_encoders=True)
    
    y_class = df['outcome'].values
    y_days = df['days_to_recover'].values
    y_pct = df['recovery_percentage'].values
    
    # Split
    X_train, X_test, y_train_class, y_test_class = train_test_split(X, y_class, test_size=Config.TEST_SIZE, stratify=y_class, random_state=Config.RANDOM_STATE)
    
    # Indices for regression (aligning with split)
    # Note: Simplification for script - using same split
    _, _, y_train_days, y_test_days = train_test_split(X, y_days, test_size=Config.TEST_SIZE, stratify=y_class, random_state=Config.RANDOM_STATE)
    _, _, y_train_pct, y_test_pct = train_test_split(X, y_pct, test_size=Config.TEST_SIZE, stratify=y_class, random_state=Config.RANDOM_STATE)
    
    # Train
    models, metrics = train_models(X_train, X_test, y_train_class, y_test_class, y_train_days, y_test_days, y_train_pct, y_test_pct)
    
    # Save
    save_model(models, feature_names, encoders, metrics)
    
    print("\n✅ TARGET ACHIEVED: Pipeline Complete!")

if __name__ == "__main__":
    main()