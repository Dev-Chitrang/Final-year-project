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
    print(f"\U0001F50D Searching for Vision & Mission of: {company_name}...\n")

    # Step 2: Get Search Results from Google
    search_results = list(search(query, num_results=num_results))

    for url in search_results:
        if url.startswith("http"):  # Ensure it's a valid URL
            print(f"\U0001F517 Extracting from: {url}\n")

            # Step 3: Fetch Web Page
            headers = {"User-Agent": user_agent}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                print("❌ Failed to fetch page! Trying next result...")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator=" ")

            # Step 4: Extract Vision & Mission using Improved Regex
            vision_pattern = re.search(r"(?:vision|our vision|company vision)[\s\S]{0,50}[:\n]+(.*?)(?=\.\s|\n|$)", text, re.IGNORECASE)
            mission_pattern = re.search(r"(?:mission|our mission|company mission)[\s\S]{0,50}[:\n]+(.*?)(?=\.\s|\n|$)", text, re.IGNORECASE)

            vision = vision_pattern.group(1).strip() if vision_pattern else None
            mission = mission_pattern.group(1).strip() if mission_pattern else None

            # Step 5: Extract from HTML Tags as Backup
            headings = soup.find_all(['h1', 'h2', 'h3', 'strong', 'b'])
            for heading in headings:
                if "vision" in heading.text.lower() and not vision:
                    vision = heading.find_next('p').text.strip() if heading.find_next('p') else None
                if "mission" in heading.text.lower() and not mission:
                    mission = heading.find_next('p').text.strip() if heading.find_next('p') else None

            # Step 6: Clean Up Extracted Text
            unwanted_phrases = ["home", ">", "companies", "mission and vision statement"]
            if vision:
                for phrase in unwanted_phrases:
                    vision = vision.replace(phrase, "").strip()
            if mission:
                for phrase in unwanted_phrases:
                    mission = mission.replace(phrase, "").strip()

            # Step 7: Combine Vision & Mission
            if vision or mission:
                combined_statement = f"{mission} {vision}" if mission and vision else vision or mission
                return {"vision_mission": combined_statement}

    return None

# Input Company Name
if __name__ == "__main__":
    company = input("Enter the company name: ")
    result = fetch_vision_mission(company)

    if result and result["vision_mission"]:
        print("\n📌 Extracted Vision & Mission Statement:")
        print(f"🟣 {result['vision_mission']}")
    else:
        print("❌ Vision & Mission statement not found!")
