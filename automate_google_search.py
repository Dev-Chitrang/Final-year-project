import requests
from bs4 import BeautifulSoup
from googlesearch import search
from fake_useragent import UserAgent
import re

def fetch_vision_mission(company_name, num_results=5):
    ua = UserAgent()
    user_agent = ua.random  

    # Step 1: Google Search Query
    query = f"{company_name} company vision and mission statement"
    print(f"🔍 Searching for Vision & Mission of: {company_name}...\n")

    # Step 2: Get Search Results from Google
    search_results = list(search(query, num_results=num_results))

    first_url = None
    for url in search_results:
        if url.startswith("http"):  # Ensure it's a valid URL
            first_url = url
            break

    if not first_url:
        print("❌ No valid search results found!")
        return None

    print(f"🔗 Extracting from: {first_url}\n")

    # Step 3: Fetch Web Page
    headers = {"User-Agent": user_agent}
    response = requests.get(first_url, headers=headers)

    if response.status_code != 200:
        print("❌ Failed to fetch page!")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(separator=" ")

    # Step 4: Extract Vision & Mission using Regex
    vision_pattern = re.search(r"vision(?: statement)?[:\s]+(.*?)(?=\.\s|$)", text, re.IGNORECASE)
    mission_pattern = re.search(r"mission(?: statement)?[:\s]+(.*?)(?=\.\s|$)", text, re.IGNORECASE)

    vision = vision_pattern.group(1).strip() if vision_pattern else None
    mission = mission_pattern.group(1).strip() if mission_pattern else None

    # Step 5: Remove Irrelevant Data
    unwanted_phrases = ["home", ">", "companies", "mission and vision statement"]
    
    if vision:
        for phrase in unwanted_phrases:
            vision = vision.replace(phrase, "").strip()
    
    if mission:
        for phrase in unwanted_phrases:
            mission = mission.replace(phrase, "").strip()

    # Step 6: Combine Vision & Mission
    combined_statement = None
    if vision and mission:
        combined_statement = f"{mission} {vision}"
    elif vision:
        combined_statement = vision
    elif mission:
        combined_statement = mission

    return {"vision_mission": combined_statement}

# Input Company Name
if __name__ == "__main__":
    company = input("Enter the company name: ")
    result = fetch_vision_mission(company)

    if result and result["vision_mission"]:
        print("\n📌 Extracted Vision & Mission Statement:")
        print(f"🟣 {result['vision_mission']}")
    else:
        print("❌ Vision & Mission statement not found!")
