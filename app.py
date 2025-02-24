from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import pandas as pd
import xgboost as xgb
import yfinance as yf
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import numpy as np
import joblib
import logging
import matplotlib
matplotlib.use('Agg')

# Importing custom modules
from finbert_news_model import fetch_top_news, analyze_news_sentiment
from stock_trend_model import get_stock_data, forecast_stock_prices, analyze_trend, plot_stock, plot_forecast, plot_trend_components
from finbert_vision_mission_model import analyze_sentiment
from automate_google_search import fetch_vision_mission
from get_Data import get_sp500_tickers, get_financial_data, get_financial_statements
from AI_agent import get_investment_advice

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

stored_data = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global loaded_model, label_encoder
    try:
        loaded_model = xgb.XGBClassifier()
        loaded_model.load_model('new_xgboost_model.json')
        label_encoder = joblib.load("label_encoder.pkl")
        logger.info("✅ Model Loaded Successfully")
    except Exception as e:
        logger.error(f"❌ Model loading failed: {str(e)}")
        raise e
    yield
    logger.info("🛑 Shutting down...")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/companies")
def get_companies():
    try:
        return JSONResponse(content=get_sp500_tickers())
    except Exception as e:
        logger.error(f"Error fetching companies: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch company list.")

@app.get("/company-summary/{ticker}")
def get_company_summary(ticker: str):
    try:
        return yf.Ticker(ticker).info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/financial-statements/{ticker}")
def get_financial_statements_of_company(ticker: str):
    """Fetches financial statements for a given company."""
    try:
        return get_financial_statements(ticker)
    except Exception as e:
        logger.error(f"Error fetching financial statements for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch financial statements.")

@app.get("/stock-trend/{ticker}")
def get_stock_trend(ticker: str):
    """Analyzes and returns the stock trend description."""
    try:
        stock_data = get_stock_data(ticker)
        _, forecast = forecast_stock_prices(stock_data)
        trend_description = analyze_trend(forecast).strip()
        stored_data["stock_trend"] = trend_description
        return {"current_trend": trend_description}
    except Exception as e:
        logger.error(f"Error analyzing stock trend for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Stock trend analysis failed.")

@app.get("/forecast-plot/{ticker}")
def get_forecast_plot(ticker: str):
    """Returns a forecast plot for the given stock ticker."""
    try:
        stock_data = get_stock_data(ticker)
        model, forecast_data = forecast_stock_prices(stock_data)
        return JSONResponse(content=plot_forecast(model, forecast_data, ticker))
    except Exception as e:
        logger.error(f"Error generating forecast plot for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate forecast plot.")

@app.get("/stock-plot/{ticker}")
def get_stock_plot(ticker: str):
    """Returns a stock price plot for the given ticker."""
    try:
        stock_data = get_stock_data(ticker)
        return JSONResponse(content=plot_stock(stock_data, ticker))
    except Exception as e:
        logger.error(f"Error generating stock plot for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate stock plot.")

@app.get("/trend-components/{ticker}")
def get_trend_components(ticker: str):
    """Returns trend components plot for the given stock."""
    try:
        stock_data = get_stock_data(ticker)
        model, forecast_data = forecast_stock_prices(stock_data)
        return JSONResponse(content=plot_trend_components(model, forecast_data))
    except Exception as e:
        logger.error(f"Error generating trend components for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate trend components.")

@app.get("/sentiment-news/{ticker}")
def get_news_sentiment(ticker: str):
    """Fetches news headlines and sentiment analysis for a company."""
    try:
        headlines, summaries = fetch_top_news(ticker)
        overall_sent, avg_score = analyze_news_sentiment(summaries)
        stored_data["news_sentiment"] = overall_sent
        return {"overall_sentiment": overall_sent, "avg_score": avg_score, "headlines": headlines}
    except Exception as e:
        logger.error(f"Error fetching news sentiment for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news sentiment.")

@app.get("/vision-mission-sentiments/{company}")
def get_vision_mission_sentiments(company: str):
    """Fetches and analyzes the sentiment of a company's vision and mission statement."""
    try:
        result = fetch_vision_mission(company)
        if not result or not result["vision_mission"]:
            raise HTTPException(status_code=404, detail="Vision & Mission statement not found")

        sentiment_label, sentiment_scores = analyze_sentiment(result["vision_mission"])
        stored_data['vision_mission_sentiment'] = sentiment_label
        return {
            "vision_mission_text": result["vision_mission"],
            "sentiment": sentiment_label,
            "detailed_scores": sentiment_scores
        }
    except Exception as e:
        logger.error(f"Error fetching vision & mission sentiments for {company}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch vision & mission sentiments.")

@app.get("/credit-rating/{ticker}")
def get_credit_rating(ticker: str):
    """Predicts the credit rating of a company using the ML model."""
    try:
        df = pd.DataFrame.from_dict(get_financial_data(ticker), orient='index').T
        pred_encoded = loaded_model.predict(df)
        pred_label = label_encoder.inverse_transform(pred_encoded)[0]
        stored_data['credit_rating'] = pred_label
        return {"credit_rating": pred_label}
    except Exception as e:
        logger.error(f"Error predicting credit rating for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Credit rating prediction failed.")


@app.post("/investment-analysis")
def get_expert_advice():
    print(stored_data)
    try:
        required_keys = {"stock_trend", "credit_rating", "vision_mission_sentiment", "news_sentiment"}
        if not required_keys.issubset(stored_data):
            raise HTTPException(status_code=400, detail="Missing required data for investment analysis")
        return {"investment_decision": get_investment_advice(
            stored_data["credit_rating"],
            stored_data["news_sentiment"],
            stored_data["stock_trend"],
            stored_data["vision_mission_sentiment"]
        )}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
