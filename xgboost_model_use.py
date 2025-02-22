import pandas as pd
import xgboost as xgb
from get_Data import get_financial_data
import joblib
import warnings
warnings.filterwarnings('ignore')

# Load Model
loaded_model = xgb.XGBClassifier()
loaded_model.load_model('new_xgboost_model.json')
label_encoder = joblib.load("label_encoder.pkl")  # Load trained label encoder

# Get Financial Data
ticker = "AAPL"
data = get_financial_data(ticker)
input_df = pd.DataFrame.from_dict(data, orient="index").T
print("Raw Input Data:\n", input_df)

# Predict
pred_encoded = loaded_model.predict(input_df)

# Decode Predicted Labels
pred_label = label_encoder.inverse_transform(pred_encoded)

print("Predicted Class:", pred_label[0])
