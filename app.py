from fastapi import FastAPI, HTTPException, Form
from contextlib import asynccontextmanager
import pandas as pd
import xgboost as xgb
import yfinance as yf
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from finbert_news_model import fetch_top_news, analyze_news_sentiment
from stock_trend_model import get_stock_data, forecast_stock_prices, analyze_trend
from finbert_vision_mission_model import analyze_sentiment, interpret_sentiment, overall_sentiment
from get_Data import get_sp500_tickers, get_financial_data, get_financial_statements
from AI_agent import get_investment_advice
import uvicorn
import numpy as np

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
    allow_origins=["http://localhost:5173"],
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
        stock = yf.Ticker(ticker)
        return stock.info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/financial-statements/{ticker}")
def get_financial_statements_of_company(ticker: str):
    try:
        financial_statements = get_financial_statements(ticker)
        return {
            "income_statement": financial_statements['income_statement'],
            "balance_sheet": financial_statements['balance_sheet'],
            "cashflow": financial_statements['cashflow'],
            "info": financial_statements['info']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock-trend/{ticker}")
def get_stock_trend(ticker: str):
    try:
        stock_data = get_stock_data(ticker)
        _, forecast = forecast_stock_prices(stock_data)
        stored_data["stock_trend"] = {"current_trend": analyze_trend(forecast)}
        return stored_data["stock_trend"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sentiment-news/{ticker}")
def get_news_sentiment(ticker: str):
    try:
        headlines, summaries = fetch_top_news(ticker)
        overall_sent, avg_score = analyze_news_sentiment(summaries)
        stored_data["news_sentiment"] = {
            "overall_sentiment": overall_sent, 
            "avg_score": avg_score, 
            "headlines": headlines
        }
        return stored_data["news_sentiment"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vision-mission-sentiments")
def submit_vision_mission(vision: str = Form(...), mission: str = Form(...)):
    try:
        vision_sentiment, vision_scores = analyze_sentiment(vision)
        mission_sentiment, mission_scores = analyze_sentiment(mission)

        stored_data["vision_sentiment"] = interpret_sentiment(vision_scores)
        stored_data["mission_sentiment"] = interpret_sentiment(mission_scores)

        stored_data["overall_vm_sentiment"], _ = overall_sentiment({
            "vision": vision_scores, 
            "mission": mission_scores
        })

        return stored_data["overall_vm_sentiment"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/credit-rating/{ticker}")
def get_credit_rating(ticker: str):
    try:
        df = get_financial_data(ticker)
        df = pd.DataFrame.from_dict(df, orient='index').T
        if loaded_model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")

        pred = loaded_model.predict(df)
        rating_class = pred.tolist()[0]
        
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
        if not all(k in stored_data for k in ["credit_rating", "news_sentiment", "stock_trend", "overall_vm_sentiment"]):
            raise HTTPException(status_code=400, detail="Missing required data for investment analysis")
        
        investment_decision = get_investment_advice(
            stored_data["credit_rating"],
            stored_data["news_sentiment"]["overall_sentiment"],
            stored_data["stock_trend"]["current_trend"],
            stored_data["overall_vm_sentiment"]
        )
        return {"investment_decision": investment_decision}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
