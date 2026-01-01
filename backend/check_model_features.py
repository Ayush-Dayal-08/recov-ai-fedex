import joblib

# Load model
artifact = joblib.load('backend/models/recovery_model.pkl')

print("📦 Model Structure:")
if 'feature_names' in artifact: 
    features = artifact['feature_names']
    print(f"\n✅ Feature Names ({len(features)} total):")
    for i, f in enumerate(features, 1):
        print(f"  {i: 2d}. {f}")
else:
    print("❌ No feature_names in artifact")

if 'models' in artifact and 'classifier' in artifact['models']:
    model = artifact['models']['classifier']
    if hasattr(model, 'feature_names_in_'):
        print(f"\n✅ Model expects {len(model.feature_names_in_)} features:")
        for i, f in enumerate(model.feature_names_in_, 1):
            print(f"  {i:2d}. {f}")