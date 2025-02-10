from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import matplotlib.pyplot as plt

save_directory = "./finbert_model"  # Ensure this directory exists or use a pretrained model like 'yiyanghkust/finbert'
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

    for scores in sentences.values():  # Fix: Only pass the score dictionary
        for key in total_scores:
            total_scores[key] += scores[key]

    num_sentences = len(sentences)
    avg_scores = {key: total / num_sentences for key, total in total_scores.items()}

    return interpret_sentiment(avg_scores), avg_scores


# def plot_sentiment(title, scores):
#     """Plots sentiment distribution."""
#     labels = list(scores.keys())
#     values = list(scores.values())

#     plt.figure(figsize=(6, 4))
#     plt.bar(labels, values, color=["red", "gray", "green"])
#     plt.xlabel("Sentiment")
#     plt.ylabel("Score")
#     plt.title(f"{title} Sentiment Distribution")
#     plt.show()


if __name__ == "__main__":
    # Example Vision & Mission statements
    vision_sentences = [
        "Inspire the world with innovative products and technologies",
        "Create a new future where technology enhances lives",
        "Set trends and drive industry transformations",
        "Be a leading brand that people love"
    ]

    mission_sentences = [
        "Enhance people's lives through innovative technologies and designs",
        "Create the best products and services",
        "Contribute to a better global society",
        "Support people to be their best"
    ]

    # Analyze vision and mission separately
    vision_results = {sentence: analyze_sentiment(sentence) for sentence in vision_sentences}
    mission_results = {sentence: analyze_sentiment(sentence) for sentence in mission_sentences}

    # Recalculate Final Sentiments
    final_vision_results = {
        sentence: (interpret_sentiment(scores), scores) for sentence, (_, scores) in vision_results.items()
    }
    final_mission_results = {
        sentence: (interpret_sentiment(scores), scores) for sentence, (_, scores) in mission_results.items()
    }

    # Compute Overall Sentiment
    final_vision_sentiment, avg_vision_scores = overall_sentiment(final_vision_results)
    final_mission_sentiment, avg_mission_scores = overall_sentiment(final_mission_results)

    # Print Results
    print("Final Vision Sentiments:", final_vision_results)
    print("Final Mission Sentiments:", final_mission_results)
    print("\nOverall Vision Sentiment:", final_vision_sentiment, avg_vision_scores)
    print("Overall Mission Sentiment:", final_mission_sentiment, avg_mission_scores)

    # Plot Sentiment Distributions
    plot_sentiment("Vision", avg_vision_scores)
    plot_sentiment("Mission", avg_mission_scores)
