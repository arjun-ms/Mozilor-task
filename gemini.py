import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up Gemini API (you'll need to provide your own API key)
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
# genai.configure(api_key='your-gemini-api-key-here')

# To check if the API key is loaded correctly
print(f"API Key loaded: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")

# Function to Fetch Website Content
def get_website_content(url):
    # Some websites have protection against web scraping. We can try to mimic a real browser by adding a User-Agent header to our request. 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        # Returns the HTML content if the request is successful, otherwise, logs an error and returns None.
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to Extract Website Information
def extract_info(html_content):
    """
    Extracts:
        Text content (first 1000 characters).
        Meta description (if available).
        Headings (h1, h2, h3 tags, first 300 characters).
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    text_content = soup.get_text()
    meta_description = soup.find('meta', attrs={'name': 'description'})
    meta_description = meta_description['content'] if meta_description else ''
    headings = ' '.join([h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])])
    
    return {
        'text_content': text_content[:1000],  # Limit to first 1000 characters
        'meta_description': meta_description,
        'headings': headings[:300]  # Limit to first 300 characters
    }

# Converts text to lowercase and checks if any of the keywords appear in it.
def check_keywords(text, keywords):
    """
    Returns a list of found keywords.
    """
    text = text.lower()
    return [keyword for keyword in keywords if keyword.lower() in text]


def evaluate_eligibility(url, content, found_keywords):
    prompt = f"""
    Analyze the following information about a website and determine if it belongs to a digital agency:
    
    URL: {url}
    Found keywords: {', '.join(found_keywords)}
    
    Meta description: {content['meta_description']}
    
    Headings: {content['headings']}
    
    Content snippet:
    {content['text_content']}
    
    Based on this information, is this website likely to belong to a digital agency? 
    Respond with 'Yes' or 'No' followed by a brief explanation.
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    decision = response.text.strip()
    is_approved = decision.lower().startswith('yes')
    
    return is_approved, decision

# uses the functions we defined to process a given agency URL.
def process_agency(url, keywords):
    """
    Returns approval status, decision, and found keywords for a given agency URL.
    """
    content = get_website_content(url)
    if not content:
        return False, "Failed to fetch website content", []

    info = extract_info(content)
    found_keywords = check_keywords(content, keywords)
    is_approved, decision = evaluate_eligibility(url, info, found_keywords)

    return is_approved, decision, found_keywords

def main():
    # Defines keywords to identify digital agencies.
    keywords = [
        "Services", "Web design", "Web Development", "SEO agency",
        "Ads Agency", "Digital marketing agency", "Agency", "Website creation"
    ]

    # agencies = [
    #     "https://www.digitalsilk.com/",
    #     "https://www.baunfire.com/",
    #     "https://fourbynorth.com/"
    # ]

    agencies = [
        "https://www.blackwelldigital.com",
        "https://addurance.com",
        "https://andanotherday.com",
        "http://mosaicpowered.com",
        "https://kafedigitalmarketing.com",
        "https://smashbeatmedia.com",
        "https://www.simplicitykey.ca",
        "https://dasweb.ca",
        "https://brawnmediany.com/",
        "https://www.clairejarrett.com/",
        "https://www.generaxion.com/",
        "https://keiyo.fr",
        "https://xtego.com",
        "https://jooren.marketing",
        "https://nodosnet.com",
        "https://www.it-webmedia.de/",
        "https://www.facebook.com100087619837431",
        "https://webdigital.ro/",
        "http://www.nettowerbung.ch",
        "https://Gabriel0226ElectricistasRD@gmail.com",
        "https://www.yong9ai.com/",
        "https://promonorge.no",
        "https://digitalbrothers.it/",
        "https://dasweb.ca",
        "https://www.alemayohu@gmail.com",
        "https://www.altosor-communication.com/",
        "https://www.sardegnainnova.com",
        "https://www.tactikmedia.com/",
        "https://talosabogados.com/",
    ]
    
    results = []

    for url in agencies:
        try:
            is_approved, decision, found_keywords = process_agency(url, keywords)
            domain = urlparse(url).netloc
            results.append({
                'url': url,
                'domain': domain,
                'is_approved': is_approved,
                'decision': decision,
                'found_keywords': ', '.join(found_keywords)
            })
        except Exception as e:
            print(f"Error processing {url}: {e}")
            # results.append({
            #     'url': url,
            #     'domain': urlparse(url).netloc,
            #     'is_approved': False,
            #     'decision': f"Error: {str(e)}",
            #     'found_keywords': ''
            # })

    # Write results to a CSV file
    with open('results_mozilor_samples.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['url', 'domain', 'is_approved', 'decision', 'found_keywords']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

    print("Processing complete. Results saved in 'results_mozilor_samples.csv'")

if __name__ == "__main__":
    main()