from fastapi import FastAPI, HTTPException, Form
from contextlib import asynccontextmanager
import pandas as pd
import xgboost as xgb
import yfinance as yf
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import plotly.io as pio  # Added import
from finbert_news_model import fetch_top_news, analyze_news_sentiment
from stock_trend_model import get_stock_data, forecast_stock_prices, analyze_trend, plot_stock, plot_forecast, plot_trend_components
from finbert_vision_mission_model import analyze_sentiment, interpret_sentiment, overall_sentiment
from get_Data import get_sp500_tickers, get_financial_data, get_financial_statements
from AI_agent import get_investment_advice
import uvicorn
import numpy as np
import matplotlib
matplotlib.use('Agg')

investment_mapping = {
    0: ['AAA', 'AA+', 'AA', 'AA-'],
    1: ['A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-'],
    2: ['BB+', 'BB', 'BB-', 'B+', 'B', 'B-'],
    3: ['CCC+', 'CCC', 'CCC-', 'CC', 'SD']
}

grade_mapping = {
    0: "Prime Investment Grade",
    1: "Investment Grade",
    2: "Speculative Grade",
    3: "Default"
}

risk_mapping = {
    0: "Very Low Risk",
    1: "Low to Moderate Risk",
    2: "Moderate to High Risk",
    3: "Very High Risk"
}

stored_data = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global loaded_model
    loaded_model = xgb.XGBClassifier()
    loaded_model.load_model('xgboost_model.json')
    print("✅ Model Loaded Successfully")
    yield
    print("🛑 Shutting down...")

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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/company-summary/{ticker}")
def get_company_summary(ticker: str):
    try:
        return yf.Ticker(ticker).info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/financial-statements/{ticker}")
def get_financial_statements_of_company(ticker: str):
    try:
        return get_financial_statements(ticker)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock-trend/{ticker}")
def get_stock_trend(ticker: str):
    try:
        forecast = forecast_stock_prices(get_stock_data(ticker))[1]
        trend_description = analyze_trend(forecast).strip()
        stored_data["stock_trend"] = {"current_trend": trend_description}
        return JSONResponse(content=stored_data["stock_trend"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/forecast-plot/{ticker}")
def get_forecast_plot(ticker: str):
    df = get_stock_data(ticker)
    model, forecast_data = forecast_stock_prices(df)  # Fetch forecast data

    img_data = plot_forecast(model, forecast_data, ticker)
    return JSONResponse(content=img_data)

@app.get("/stock-plot/{ticker}")
def get_stock_plot(ticker: str):
    stock_data = get_stock_data(ticker)
    stock_data.rename(columns={"Date": "ds", "Close": "y"}, inplace=True)

    try:
        plot_json = plot_stock(stock_data, ticker)
        return JSONResponse(content=plot_json)  # Return JSON, not an image
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trend-components/{ticker}")
def get_trend_components(ticker: str):
    df = get_stock_data(ticker)
    model, forecast_data = forecast_stock_prices(df)  # Fetch forecast data

    img_data = plot_trend_components(model, forecast_data)
    return JSONResponse(content=img_data)

@app.get("/sentiment-news/{ticker}")
def get_news_sentiment(ticker: str):
    try:
        headlines, summaries = fetch_top_news(ticker)
        overall_sent, avg_score = analyze_news_sentiment(summaries)
        stored_data["news_sentiment"] = {"overall_sentiment": overall_sent, "avg_score": avg_score, "headlines": headlines}
        return JSONResponse(content=stored_data["news_sentiment"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vision-mission-sentiments")
def submit_vision_mission(vision: str = Form(...), mission: str = Form(...)):
    try:
        vision_scores, mission_scores = analyze_sentiment(vision), analyze_sentiment(mission)
        stored_data.update({
            "vision_sentiment": interpret_sentiment(vision_scores[1]),
            "mission_sentiment": interpret_sentiment(mission_scores[1]),
            "overall_vm_sentiment": overall_sentiment({"vision": vision_scores[1], "mission": mission_scores[1]})[0]
        })
        return stored_data["overall_vm_sentiment"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/credit-rating/{ticker}")
def get_credit_rating(ticker: str):
    try:
        df = pd.DataFrame.from_dict(get_financial_data(ticker), orient='index').T
        if loaded_model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")
        rating_class = loaded_model.predict(df).tolist()[0]
        stored_data["credit_rating"] = {
            "ratings": investment_mapping.get(rating_class, "Unknown"),
            "grade": grade_mapping.get(rating_class, "Unknown"),
            "risk": risk_mapping.get(rating_class, "Unknown")
        }
        return stored_data["credit_rating"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/investment-analysis")
def get_expert_advice():
    try:
        required_keys = {"credit_rating", "news_sentiment", "stock_trend", "overall_vm_sentiment"}
        if not required_keys.issubset(stored_data):
            raise HTTPException(status_code=400, detail="Missing required data for investment analysis")
        return {"investment_decision": get_investment_advice(
            stored_data["credit_rating"],
            stored_data["news_sentiment"]["overall_sentiment"],
            stored_data["stock_trend"]["current_trend"],
            stored_data["overall_vm_sentiment"]
        )}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
