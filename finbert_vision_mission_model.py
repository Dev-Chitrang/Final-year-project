from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import matplotlib.pyplot as plt
from automate_google_search import fetch_vision_mission

# Load FinBERT model and tokenizer
save_directory = "./finbert_model"
tokenizer = AutoTokenizer.from_pretrained(save_directory)
model = AutoModelForSequenceClassification.from_pretrained(save_directory)

print("Model and tokenizer loaded from local storage!")

def analyze_sentiment(text):
    """Performs sentiment analysis using FinBERT."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    scores = torch.nn.functional.softmax(outputs.logits, dim=-1)

    labels = ["negative", "neutral", "positive"]
    sentiment = labels[torch.argmax(scores).item()]

    return sentiment, {labels[i]: scores[0][i].item() for i in range(3)}

def interpret_sentiment(scores):
    """Improved sentiment classification based on the dominant score."""
    max_label = max(scores, key=scores.get)
    max_score = scores[max_label]

    if max_score > 0.5:
        return max_label
    return "neutral"

def overall_sentiment(sentences):
    """Aggregates sentiment scores to get an overall classification."""
    total_scores = {"negative": 0, "neutral": 0, "positive": 0}

    for scores in sentences.values():
        for key in total_scores:
            total_scores[key] += scores[key]

    num_sentences = len(sentences)
    avg_scores = {key: total / num_sentences for key, total in total_scores.items()}

    return interpret_sentiment(avg_scores), avg_scores

def plot_sentiment(title, scores):
    """Plots sentiment distribution."""
    labels = list(scores.keys())
    values = list(scores.values())

    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=["red", "gray", "green"])
    plt.xlabel("Sentiment")
    plt.ylabel("Score")
    plt.title(f"{title} Sentiment Distribution")
    plt.show()

if __name__ == "__main__":
    company = input("Enter the company name: ")
    result = fetch_vision_mission(company)

    if result and result["vision_mission"]:
        vision_mission_text = result["vision_mission"]
        print("\n📌 Extracted Vision & Mission Statement:")
        print(f"🟣 {vision_mission_text}\n")

        sentiment_label, sentiment_scores = analyze_sentiment(vision_mission_text)
        print(f"📊 Sentiment Analysis Result: {sentiment_label}")
        print(f"Detailed Scores: {sentiment_scores}")

        plot_sentiment("Vision-Mission", sentiment_scores)
    else:
        print("❌ No valid Vision & Mission statement found!")
