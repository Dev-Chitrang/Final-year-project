import ollama

def get_investment_advice(credit_rating, news_sentiment, stock_trend, vision_mission_sentiment):
    system_prompt = """
    You are an expert investment advisor with a deep understanding of financial markets, corporate credit ratings. Your task is to analyze key financial indicators and provide a structured, insightful, and easy-to-interpret investment recommendation.

    ### Your analysis should consider the following factors:
    - **Credit Rating:** (AAA, AA, BBB, etc.)
    - **News Sentiment:** (Positive, Neutral, Negative)
    - **Stock Trend:** (Upward, Stable, Downward)
    - **Vision & Mission Sentiment:** (Positive, Neutral, Negative)

    ### Your response must be structured as follows:

    #### **1. Predicted Credit Rating**
    - Based on the given data, determine the most likely **credit rating** of the company (AAA, AA, BBB, etc.).
    - Justify the rating based on financial, sentiment, and market indicators.

    #### **2. Investment Overview**
    - Provide a high-level summary of the company’s financial health and market position.

    #### **3. Risk Assessment**
    - Analyze the company's risk profile and highlight potential advantages or concerns.

    #### **4. Recommended Investment Strategy**
    - Indicate whether the investor should **invest in bonds, equity, both, or neither**.
    - If investing, suggest an optimal **investment horizon** (Short-term, Long-term, or Moderate).
    - If not investing, clearly explain the risks and rationale concisely yet compellingly.

    Ensure your response is **structured, engaging, and free from ambiguity**—your words should be insightful yet easy to understand.
    """

    user_input = f"""
    Based on the given data, can you determine the company's **most likely credit rating**?

    Here are the key indicators:
    - **Credit Rating Group:** {credit_rating}
    - **News Sentiment:** {news_sentiment}
    - **Stock Trend:** {stock_trend}
    - **Vision & Mission Sentiment:** {vision_mission_sentiment}
    """

    response = ollama.chat(model="mistral", messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ])

    return response['message']['content']


if __name__ == "__main__":
    # Example input data
    credit_rating = 0  # This will pass all ratings from mapping[0]
    news_sentiment = "Positive"
    stock_trend = "Upward"
    vision_mission_sentiment = "Neutral"

    advice = get_investment_advice(credit_rating, news_sentiment, stock_trend, vision_mission_sentiment)
    print("Investment Advice:\n", advice)
