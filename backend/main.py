from flask import Flask, request, jsonify
from flask_cors import CORS
import xgboost as xgb
import pandas as pd
import numpy as np

# 1. Initialize the App
app = Flask(__name__)
CORS(app)  # This allows your frontend (website) to talk to this backend

# 2. Load the AI Brain
print("🤖 Loading RECOV.AI Model...")
model = xgb.XGBClassifier()
try:
    model.load_model('recov_ai_model.json')
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")

# 3. Define the Prediction Route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get data from the website
        data = request.json
        print(f"📥 Received data: {data}")

        # Create a DataFrame (must match the training columns exactly)
        # Note: We only need the features the AI was trained on
        input_data = pd.DataFrame([{
            'amount': float(data.get('amount', 0)),
            'days_overdue': int(data.get('days_overdue', 0)),
            'payment_history_score': float(data.get('payment_history_score', 0.5)),
            'shipment_volume_change_30d': float(data.get('shipment_volume_change_30d', 0.0)),
            'email_opened': int(data.get('email_opened', 0)),
            'dispute_flag': int(data.get('dispute_flag', 0)),
            
            # These columns weren't used in the final math model, but we add them to prevent errors
            # if the model expects them (depending on how we finalized the training columns).
            # For XGBoost, column order matters!
        }])

        # Make the Prediction
        prediction = model.predict(input_data)[0]
        probability = model.predict_proba(input_data)[0][1]

        # Return the result
        result = {
            'prediction': int(prediction), # 1 = Will Pay, 0 = Risk
            'risk_score': float(1 - probability), # Higher score = Higher risk
            'message': "High Likelihood of Payment" if prediction == 1 else "High Risk of Default"
        }
        
        print(f"📤 Sending result: {result}")
        return jsonify(result)

    except Exception as e:
        print(f"❌ API Error: {e}")
        return jsonify({'error': str(e)}), 500

# 4. Start the Server
if __name__ == '__main__':
    print("🚀 RECOV.AI Server starting on port 5000...")
    app.run(debug=True, port=5000)