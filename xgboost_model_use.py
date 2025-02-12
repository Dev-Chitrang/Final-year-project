import pandas as pd
import xgboost as xgb
from get_Data import get_financial_data


loaded_model = xgb.XGBClassifier()
loaded_model.load_model('xgboost_model.json')

ticker = "AAPL"
data = get_financial_data(ticker)
input_df = pd.DataFrame.from_dict(data, orient="index").T
print(input_df)

pred = loaded_model.predict(input_df)
print(pred)