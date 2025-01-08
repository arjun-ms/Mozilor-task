import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse
import openai

# Set up OpenAI API
openai.api_key = 'your-api-key-here'

def get_website_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_info(html_content):
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

def check_keywords(text, keywords):
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
    
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150
    )
    
    decision = response.choices[0].text.strip()
    is_approved = decision.lower().startswith('yes')
    
    return is_approved, decision

def process_agency(url, keywords):
    content = get_website_content(url)
    if not content:
        return False, "Failed to fetch website content", []

    info = extract_info(content)
    found_keywords = check_keywords(content, keywords)
    is_approved, decision = evaluate_eligibility(url, info, found_keywords)

    return is_approved, decision, found_keywords

def main():
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
        "https://github.com/",
        "https://www.tatamotors.com/",
        "https://www.tcs.com/",
        "https://www.spiderworks.in/",
        "https://www.adoxglobal.com/"
    ]
        
    results = []

    for url in agencies:
        is_approved, decision, found_keywords = process_agency(url, keywords)
        domain = urlparse(url).netloc
        results.append({
            'url': url,
            'domain': domain,
            'is_approved': is_approved,
            'decision': decision,
            'found_keywords': ', '.join(found_keywords)
        })

    # Write results to CSV
    with open('agency_verification_results_2.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['url', 'domain', 'is_approved', 'decision', 'found_keywords']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

    print("Processing complete. Results saved in 'agency_verification_results.csv'")

if __name__ == "__main__":
    main()