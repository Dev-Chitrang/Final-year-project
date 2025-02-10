import yfinance as yf
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# Load FinBERT model and tokenizer
save_directory = "./finbert_model"  # Ensure this directory exists or use a pretrained model like 'yiyanghkust/finbert'
tokenizer = AutoTokenizer.from_pretrained(save_directory)
model = AutoModelForSequenceClassification.from_pretrained(save_directory)

print("Model and tokenizer loaded from local storage!")

# Function to fetch top 10 news for a given stock ticker
def fetch_top_news(ticker):
    stock = yf.Ticker(ticker)
    news = stock.news[:10]  # Fetch the top 10 latest news articles
    
    # Check and handle the structure of the news data
    headlines = []
    summary = []
    for article in news:
        headlines.append(article['content']['title'])
        summary.append(article['content']['summary'])
    
    return headlines, summary

# Function to perform sentiment analysis on news
def analyze_sentiment(text):
    """Performs sentiment analysis using FinBERT."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    scores = torch.nn.functional.softmax(outputs.logits, dim=-1)

    labels = ["negative", "neutral", "positive"]
    sentiment = labels[torch.argmax(scores).item()]
    return sentiment, {labels[i]: scores[0][i].item() for i in range(3)}

# Function to interpret sentiment based on thresholds
def interpret_sentiment(scores):
    """Classifies sentiment based on the dominant score."""
    max_score = max(scores, key=scores.get)
    return max_score

# Function to aggregate sentiment across multiple news headlines
def analyze_news_sentiment(news_list):
    """Aggregates sentiment of multiple news headlines."""
    total_scores = {"negative": 0, "neutral": 0, "positive": 0}

    for headline in news_list:
        _, scores = analyze_sentiment(headline)
        for key in total_scores:
            total_scores[key] += scores[key]

    num_headlines = len(news_list)
    avg_scores = {key: total / num_headlines for key, total in total_scores.items()}
    return interpret_sentiment(avg_scores), avg_scores

if __name__ == "__main__":
    # Fetch and analyze news sentiment for a specific stock ticker (e.g., 'AAPL' for Apple)
    ticker = 'AAPL'
    top_news = fetch_top_news(ticker)

    # Classify sentiment for the news
    overall_sentiment, avg_scores = analyze_news_sentiment(top_news[1])

    # Print the overall sentiment and distribution
    print("\nOverall News Sentiment:", overall_sentiment)
    print("Average Sentiment Scores:", avg_scores)
