**Investment Advisory System Documentation**

## 1. Project Introduction

### 1.1 Vision

An intelligent, data-driven investment advisory system that leverages advanced machine learning techniques to provide comprehensive financial insights and recommendations.

### 1.2 Core Objective

Empower investors with AI-powered analysis by combining multiple data sources and sophisticated predictive models to generate actionable investment intelligence.

---

## 2. System Architecture

### 2.1 High-Level Components

**Backend Directory Structure:**

```
backend/
│
├── app.py                     # Main API application
├── AI_agent.py                # Central intelligence for investment advice
├── get_Data.py                # Data retrieval and processing
├── stock_trend_model.py       # Stock trend prediction
├── xgboost_ml_model.py        # Machine learning model
├── save_finbert.py            # Model persistence utility
├── finbert_news_model.py      # News sentiment analysis
└── finbert_vision_mission_model.py  # Company statement analysis
```

### 2.2 Technology Stack

| Category         | Technologies                |
| ---------------- | --------------------------- |
| Web Framework    | FastAPI                     |
| Machine Learning | XGBoost, FinBERT, Prophet   |
| Data Processing  | Pandas, NumPy, Scikit-learn |
| Data Source      | Yahoo Finance               |
| Deployment       | Uvicorn                     |

---

## 3. Detailed Feature Breakdown

### 3.1 Credit Rating Analysis

- **Location:** `app.py → get_credit_rating()`
- **Purpose:** Evaluate a company's financial health
- **Key Metrics:**
  - Debt levels
  - Financial stability
  - Risk assessment

### 3.2 News Sentiment Analysis

- **Location:** `finbert_news_model.py → analyze_sentiment()`
- **Technology:** FinBERT (Financial BERT)
- **Capabilities:**
  - Extract sentiment from financial news
  - Classify sentiment as positive, negative, or neutral
  - Provide contextual understanding of news impact

### 3.3 Stock Trend Prediction

- **Location:** `stock_trend_model.py → forecast_stock_prices()`
- **Techniques:**
  - Time series forecasting
  - Machine learning regression
  - Historical price analysis
- **Outputs:**
  - Future price predictions
  - Trend direction
  - Confidence intervals

### 3.4 Vision & Mission Sentiment Evaluation

- **Location:** `finbert_vision_mission_model.py → analyze_sentiment()`
- **Approach:**
  - Natural Language Processing
  - Sentiment scoring
  - Contextual understanding of company statements

---

## 4. API Endpoint Architecture

### 4.1 Endpoint Categories

#### Company Insights

- `/company-summary/{ticker}`
- `/credit-rating/{ticker}`
- `/financial-statements/{ticker}`

#### Market Analysis

- `/stock-trend/{ticker}`
- `/news-sentiment/{ticker}`

#### Advanced Intelligence

- `/vision-mission`
- `/expert-advice`

---

## 5. Machine Learning Models

### 5.1 XGBoost Model

- **File:** `xgboost_ml_model.py`
- **Purpose:** Advanced predictive modeling
- **Features:**
  - Gradient boosting
  - Handles complex financial datasets
  - High prediction accuracy

### 5.2 FinBERT Model

- **File:** `save_finbert.py`
- **Purpose:** Financial sentiment analysis
- **Capabilities:**
  - Pre-trained on financial corpus
  - Contextual language understanding
  - Sentiment classification

---

## 6. Data Management

### 6.1 Data Sources

- Yahoo Finance
- Financial news APIs
- Company financial statements

### 6.2 Data Processing Pipeline

1. Data retrieval
2. Cleaning and normalization
3. Feature engineering
4. Model training
5. Prediction generation

---

## 7. Development and Deployment

### 7.1 Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Prepare models
python save_finbert.py
python xgboost_ml_model.py

# Run application
python app.py
```

### 7.2 Dependencies

- **Python** 3.8+
- **FastAPI** 0.115.8+
- **Pandas** 2.2.3+
- **Scikit-learn** 1.6.1+
- **Transformers** 4.48.3+

---

## 8. Security and Performance

### 8.1 Security Measures

- Environment-based configuration
- Secure API endpoints
- Error handling mechanisms

### 8.2 Performance Optimization

- Asynchronous API design
- Efficient machine learning models
- Caching strategies

---

## 9. Future Roadmap

### 9.1 Planned Enhancements

- Real-time model retraining
- Enhanced risk assessment
- Expanded data sources
- Improved model interpretability

