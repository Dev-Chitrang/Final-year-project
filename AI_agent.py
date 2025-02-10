import ollama


def get_investment_advice(credit_rating, news_sentiment, stock_trend, vision_mission_sentiment):
    system_prompt = """
    You are an expert investment advisor, adept at deciphering the intricate tapestry of financial markets. Your mission is to analyze and synthesize key investment indicators to provide well-structured, insightful, and easy-to-interpret recommendations.  

    Your analysis must intertwine the following factors:  
    - **Credit Rating:** (AAA, AA, BBB, etc.)  
    - **Grade of the Company:** (Prime Investment Grade, Investment Grade, Speculative Grade, Default)  
    - **Risk Level:** (Very Low Risk, Low to Moderate Risk, Moderate to High Risk, Very High Risk)  
    - **News Sentiment:** (Positive, Neutral, Negative)  
    - **Stock Trend:** (Upward, Stable, Downward)  
    - **Vision & Mission Sentiment:** (Positive, Neutral, Negative)  

    Your response should be structured as follows:  

    **1. Investment Overview**  
    - Provide a high-level summary of the company’s financial health and market position.  

    **2. Risk Assessment**  
    - Delve into the risk profile, analyzing potential concerns or advantages.  

    **3. Recommended Investment Strategy**  
    - Clearly indicate whether the investor should **invest in bonds, equity, both, or neither**.  
    - If investing, suggest an optimal **investment horizon** (Short-term, Long-term, or Moderate).  
    - If not investing, elucidate the risks and rationale in a compelling yet concise manner.  

    Ensure your response is structured, engaging, and free from ambiguity—your words should transcend complexity while maintaining depth.  
    """

    user_input = f"""
    Credit Rating belongs to: {credit_rating['ratings']}
    Risk Type: {credit_rating['risk']}
    Investment Type: {credit_rating['grade']}
    News Sentiment: {news_sentiment}
    Stock Trend: {stock_trend}
    Vision & Mission Sentiment: {vision_mission_sentiment}
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
