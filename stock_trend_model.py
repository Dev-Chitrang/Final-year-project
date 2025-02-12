import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
import plotly.express as px
import json
import base64
import io

# Function to fetch historical stock data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="6mo")

    # Ensure the index (date) is converted to a column and named 'ds'
    df = df.reset_index()
    df.rename(columns={"Date": "ds", "Close": "y"}, inplace=True)

    # Prophet requires datetime format
    df["ds"] = pd.to_datetime(df["ds"]).dt.tz_localize(None)

    return df[["ds", "y"]]  # Return only the required columns



# Function to train the Prophet model and forecast future stock prices
def forecast_stock_prices(df, periods=180):  # Predict next 180 days
    model = Prophet(daily_seasonality=True)
    model.fit(df)
    
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    
    return model, forecast


# Function to visualize forecasted stock prices
def plot_forecast(model, forecast, ticker):
    """Generates a stock forecast plot as a base64-encoded image."""
    fig = model.plot(forecast)
    plt.title(f'{ticker} Stock Price Forecast')
    plt.xlabel('Date')
    plt.ylabel('Close Price (USD)')

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    
    return {"image": img_str}

def plot_stock(data, symbol):
    fig = px.line(data, x="ds", y="y", title=f"{symbol} Stock Prices")
    fig_json = json.loads(fig.to_json())  # Convert Plotly figure to JSON
    return fig_json


def plot_trend_components(model, forecast):
    """Generates trend component plots as a base64-encoded image."""
    fig = model.plot_components(forecast)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")

    return {"image": img_str}

def analyze_trend(forecast):
    """Determine the trend direction based on the last few predictions."""
    last_10 = forecast[['ds', 'yhat']].tail(10)  # Get last 10 predictions
    trend_slope = (last_10['yhat'].iloc[-1] - last_10['yhat'].iloc[0]) / 10  # Slope calculation

    if trend_slope > 0:
        return("\n📈 The stock trend is UPWARD.")
    elif trend_slope < 0:
        return("\n📉 The stock trend is DOWNWARD.")
    else:
        return("\n➖ The stock trend is STABLE.")


# Main Execution
if __name__ == "__main__":
    ticker = "AAPL"  # Example: Apple stock
    stock_data = get_stock_data(ticker)

    # Plot historical stock prices

    # Train model and forecast
    model, forecast = forecast_stock_prices(stock_data)

# Display latest forecasted values
    latest_forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(10)
    print("\nLatest Forecasted Prices:")
    print(latest_forecast)

    # Call analyze_trend after generating forecast
    analyze_trend(forecast)

    # Plot forecasted stock prices
    plot_forecast(model, forecast, ticker)

    # Plot trend components
    plot_trend_components(model, forecast)

