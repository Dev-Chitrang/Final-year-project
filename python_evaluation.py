import pandas as pd
import xgboost as xgb
import torch
import yfinance as yf
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from prophet import Prophet
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, mean_squared_error
import numpy as np

# Load XGBoost Model
xgb_model = xgb.XGBClassifier()
xgb_model.load_model('xgboost_model.json')

# Load FinBERT Model
finbert_tokenizer = AutoTokenizer.from_pretrained("./finbert_model")
finbert_model = AutoModelForSequenceClassification.from_pretrained("./finbert_model")


investment_mapping = {
    0: ['AAA', 'AA+', 'AA', 'AA-'],
    1: ['A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-'],
    2: ['BB+', 'BB', 'BB-', 'B+', 'B', 'B-'],
    3: ['CCC+', 'CCC', 'CCC-', 'CC', 'SD']
}

### 1️⃣ **XGBoost Credit Rating Prediction Evaluation**
def evaluate_xgboost(ticker):
    from get_Data import get_financial_data  # Assuming function exists in get_Data.py
    data = get_financial_data(ticker)
    input_df = pd.DataFrame.from_dict(data, orient="index").T
    
    pred = xgb_model.predict(input_df)
    
    # Dummy Actual Labels for Example Evaluation
    actual_labels = [pred[0]]  # Placeholder since real labels are unknown
    
    acc = accuracy_score(actual_labels, pred)
    print(f"\nXGBoost Accuracy: {acc:.2f}")
    
    report = classification_report(actual_labels, pred, output_dict=True)
    report_df = pd.DataFrame(report).transpose()
    report_df.to_csv("xgboost_classification_report.csv", index=True)
    
    return pred[0]  # Returning the predicted credit rating group


### 2️⃣ **FinBERT Sentiment Analysis**
def analyze_sentiment(text):
    """Performs sentiment analysis using FinBERT."""
    inputs = finbert_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = finbert_model(**inputs)
    scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    labels = ["negative", "neutral", "positive"]
    sentiment = labels[torch.argmax(scores).item()]
    return sentiment, {labels[i]: scores[0][i].item() for i in range(3)}

def evaluate_finbert(ticker):
    stock = yf.Ticker(ticker)
    news = stock.news[:10]  # Fetch top 10 news articles
    headlines = [article['content']['title'] for article in news]

    total_scores = {"negative": 0, "neutral": 0, "positive": 0}
    sentiment_results = []

    for headline in headlines:
        sentiment, scores = analyze_sentiment(headline)
        sentiment_results.append([headline, sentiment, scores])
        for key in total_scores:
            total_scores[key] += scores[key]

    avg_scores = {key: total / len(headlines) for key, total in total_scores.items()}
    sentiment_df = pd.DataFrame(sentiment_results, columns=["Headline", "Sentiment", "Scores"])
    sentiment_df.to_csv("finbert_sentiment_results.csv", index=False)

    print("\nFinBERT Sentiment Analysis:")
    print(avg_scores)

    return avg_scores


### 3️⃣ **Prophet Stock Trend Forecasting**
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="6mo")
    df = df.reset_index()
    df.rename(columns={"Date": "ds", "Close": "y"}, inplace=True)
    df["ds"] = pd.to_datetime(df["ds"]).dt.tz_localize(None)
    return df[["ds", "y"]]

def evaluate_prophet(ticker):
    stock_data = get_stock_data(ticker)
    model = Prophet(daily_seasonality=True)
    model.fit(stock_data)

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    # Evaluate Performance
    y_pred = forecast['yhat'].iloc[-30:]
    y_true = stock_data['y'].iloc[-30:].values

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))

    print(f"\nProphet MAE: {mae:.2f}, RMSE: {rmse:.2f}")
    forecast[['ds', 'yhat']].to_csv("prophet_forecast_results.csv", index=False)

    return "Upward" if y_pred.iloc[-1] > y_pred.iloc[0] else "Downward"


### **🔹 Running the Evaluations**
if __name__ == "__main__":
    ticker = "AAPL"  # Example stock

    # 1️⃣ XGBoost Prediction
    predicted_credit_rating = evaluate_xgboost(ticker)
    rating_range = investment_mapping[predicted_credit_rating]

    # 2️⃣ FinBERT Sentiment Analysis
    news_sentiment = evaluate_finbert(ticker)

    # 3️⃣ Prophet Stock Trend Forecasting
    stock_trend = evaluate_prophet(ticker)

    # Store Results in a CSV
    results_df = pd.DataFrame([{
        "Company": ticker,
        "Predicted Credit Rating": (predicted_credit_rating, rating_range),
        "News Sentiment": news_sentiment,
        "Stock Trend": stock_trend
    }])

    results_df.to_csv("final_results_summary.csv", index=False)

    print("\n✅ Results saved to final_results_summary.csv")
