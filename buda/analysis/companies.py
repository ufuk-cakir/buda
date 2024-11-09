import pandas as pd
import json
from collections import defaultdict
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Define the predefined categories prompt for matching
predefined_categories = """
Please categorize the following company into one of these categories:
1. E-commerce
2. Healthcare
3. Technology
4. Education
5. Finance
6. Hospitality
7. Real Estate
8. Media and Entertainment
9. Consulting
10. Non-profit
11. Food and Beverage
12. Retail
13. Transportation
14. Energy
15. Fashion and Beauty
16. Photography
17. Sports and Fitness
18. Gaming
19. Travel

If the company does not fit into these categories, please respond with 'Other'.

Answer with just the category name (e.g., 'Technology').
"""

def query_on_demand_api(api_key, company_name, external_user_id="anonymous_user"):
    # Create Chat Session
    create_session_url = 'https://api.on-demand.io/chat/v1/sessions'
    create_session_headers = {'apikey': api_key}
    create_session_body = {"pluginIds": [], "externalUserId": external_user_id}

    # Make the request to create a chat session
    response = requests.post(create_session_url, headers=create_session_headers, json=create_session_body)
    response_data = response.json()
    session_id = response_data['data']['id']

    # Construct the query with the company name
    query = predefined_categories + "Company: " + company_name

    # Submit Query
    submit_query_url = f'https://api.on-demand.io/chat/v1/sessions/{session_id}/query'
    submit_query_headers = {'apikey': api_key}
    submit_query_body = {
        "endpointId": "predefined-openai-gpt4o",
        "query": query,
        "pluginIds": ["plugin-1712327325", "plugin-1713962163", "plugin-1713924030"],
        "responseMode": "sync"
    }

    # Make the request to submit a query and retrieve the category
    query_response = requests.post(submit_query_url, headers=submit_query_headers, json=submit_query_body)
    query_response_data = query_response.json()
    return query_response_data["data"]["answer"]

def identify_market_category(company_name, api_key):
    try:
        return query_on_demand_api(api_key, company_name)
    except Exception as e:
        print(f"Error querying API for {company_name}: {e}")
        return "Unknown"

# Function to assign categories asynchronously
def assign_categories_async(data, api_key, debug):
    print("\nAssigning categories to companies...") if debug else None
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(identify_market_category, item["advertiser_name"], api_key): item
            for item in data
        }
        for future in tqdm(as_completed(futures), total=len(futures)):
            item = futures[future]
            try:
                item["category"] = future.result()
                if debug:
                    print(f"Company: {item['advertiser_name']}, Category: {item['category']}")
            except Exception as e:
                item["category"] = "Unknown"
                print(f"Error processing {item['advertiser_name']}: {e}")
    return data

# Function to generate and display statistics
def generate_statistics(data):
    category_count = defaultdict(int)
    tracking_types = {
        "data_file_custom_audience": "has_data_file_custom_audience",
        "remarketing_custom_audience": "has_remarketing_custom_audience",
        "in_person_store_visit": "has_in_person_store_visit"
    }
    stats = defaultdict(lambda: {key: 0 for key in tracking_types})

    for item in data:
        category = item.get("category", "Unknown")
        category_count[category] += 1
        for key, field in tracking_types.items():
            if item.get(field, False):
                stats[category][key] += 1

    # Convert results to DataFrame for display
    category_df = pd.DataFrame({
        "Category": list(category_count.keys()),
        "Number of Companies": list(category_count.values())
    })
    tracking_df = pd.DataFrame(stats).T.reset_index().rename(columns={"index": "Category"})
    tracking_df = tracking_df.merge(category_df, on="Category")

    print("\nStatistics by Category:")
    print(tracking_df)
    return tracking_df

def analyze_companies(data, api_key, debug=False):
    data = data["ig_custom_audiences_all_types"]
    categorized_data = assign_categories_async(data, api_key, debug=debug)
    df = generate_statistics(categorized_data)
    return df