import os
import json
import requests
import logging
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import pandas as pd

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

# Function to interact with the on-demand API
def query_on_demand_api(api_key, company_name, external_user_id="anonymous_user"):
    create_session_url = 'https://api.on-demand.io/chat/v1/sessions'
    create_session_headers = {'apikey': api_key}
    create_session_body = {"pluginIds": [], "externalUserId": external_user_id}

    try:
        response = requests.post(create_session_url, headers=create_session_headers, json=create_session_body)
        response_data = response.json()
        session_id = response_data['data']['id']
        
        query = predefined_categories + "Company: " + company_name
        submit_query_url = f'https://api.on-demand.io/chat/v1/sessions/{session_id}/query'
        submit_query_headers = {'apikey': api_key}
        submit_query_body = {
            "endpointId": "predefined-openai-gpt4o",
            "query": query,
            "pluginIds": ["plugin-1712327325", "plugin-1713962163", "plugin-1713924030"],
            "responseMode": "sync"
        }

        query_response = requests.post(submit_query_url, headers=submit_query_headers, json=submit_query_body)
        query_response_data = query_response.json()
        return query_response_data["data"]["answer"]

    except Exception as e:
        logging.error(f"Error querying API for {company_name}: {e}")
        return "Unknown"

def identify_market_category(company_name, api_key):
    try:
        return query_on_demand_api(api_key, company_name)
    except Exception as e:
        logging.error(f"Error in identify_market_category for {company_name}: {e}")
        return "Unknown"

# Function to assign categories asynchronously with frequent intermediate JSON updates
def assign_categories_async(data, api_key, debug, output_folder, save_frequency=10):
    logging.info("Starting category assignment")
    categorized_data = {}
    json_file_path = os.path.join(output_folder, "categorized_data.json")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(identify_market_category, item["advertiser_name"], api_key): item
            for item in data
        }
        for i, future in enumerate(tqdm(as_completed(futures), total=len(futures))):
            item = futures[future]
            company_name = item["advertiser_name"]
            try:
                category = future.result()
                categorized_data[company_name] = category
                if debug:
                    logging.info(f"Company: {company_name}, Category: {category}")
            except Exception as e:
                categorized_data[company_name] = "Unknown"
                logging.error(f"Error processing {company_name}: {e}")

            # Save intermediate results every 'save_frequency' items
            if (i + 1) % save_frequency == 0:
                with open(json_file_path, "w") as f:
                    json.dump(categorized_data, f, indent=4)
                logging.info(f"Intermediate data saved after processing {i + 1} items")

    # Final save of categorized data
    with open(json_file_path, "w") as f:
        json.dump(categorized_data, f, indent=4)
    
    return categorized_data

# Function to generate and display statistics
def generate_statistics(data, output_folder):
    category_count = defaultdict(int)
    for category in data.values():
        category_count[category] += 1

    # Convert results to DataFrame for display
    category_df = pd.DataFrame({
        "Category": list(category_count.keys()),
        "Number of Companies": list(category_count.values())
    })

    logging.info("Statistics generated successfully")
    
    # Save the statistics to CSV
    category_df.to_csv(os.path.join(output_folder, "category_statistics.csv"), index=False)
    
    return category_df

# Function to load categorized data, map to broader categories, and save summary
def create_broad_category_summary(folder):
    category_mapping = {
        'Media and Entertainment': 'Media',
        'Fashion and Beauty': 'Media',
        'Gaming': 'Media',
        'Photography': 'Media',
        'Sports and Fitness': 'Media',
        'Consulting': 'Business',
        'Real Estate': 'Business',
        'Advertising': 'Business',
        'Finance': 'Business',
        'Non-profit': 'Business',
        'Technology': 'Technology',
        'E-commerce': 'Technology',
        'Retail': 'Technology',
        'Healthcare': 'Health',
        'Food and Beverage': 'Health',
        'PetSafe Brand': 'Health',
        'Travel': 'Travel',
        'Hospitality': 'Travel',
        'Transportation': 'Travel',
        'Energy': 'Energy',
        'Unknown': 'Uncategorized',
        'Other': 'Uncategorized'
    }
    
    # Load data from JSON
    with open(os.path.join(folder, "categorized_data.json"), 'r') as f:
        data = json.load(f)
    
    # Count occurrences in each category
    category_counts = Counter(data.values())
    df = pd.DataFrame(list(category_counts.items()), columns=["Category", "Count"])
    
    # Map to broad categories
    df['Broad Category'] = df['Category'].map(category_mapping)
    summary_df = df.groupby('Broad Category')['Count'].sum().reset_index()

    # Save summary to JSON
    summary_path = os.path.join(folder, "summary_categories.json")
    result = summary_df.set_index('Broad Category')['Count'].to_dict()
    with open(summary_path, 'w') as f:
        json.dump(result, f, indent=4)
    
    logging.info("Broad category summary saved to JSON successfully")
    return summary_df

# Function to get company ad statistics from the summary JSON
def get_company_ad_statistics(file_path="summary_categories.json"):
    with open(file_path, 'r') as f:
        summary = json.load(f)
    return summary

# Main function to analyze companies
def map_companies(data, api_key, output_folder="company_analysis_output_ufuk", logging_level=logging.INFO, debug=True):
    os.makedirs(output_folder, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        filename=os.path.join(output_folder, 'analysis.log'),
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging_level
    )
    data = data["ig_custom_audiences_all_types"]
    categorized_data = assign_categories_async(data, api_key, debug=debug, output_folder=output_folder)
    generate_statistics(categorized_data, output_folder=output_folder)

def analyze_companies(input_folder, output_folder="company_analysis_output_ufuk", filename="ad_companies_data_statistics", logging_level=logging.INFO, debug=True):
    # Generate the broad category summary and save it in the output folder
    create_broad_category_summary(folder=input_folder)
    
    # Load the summary statistics JSON from the input folder and save to the specified output path
    summary = get_company_ad_statistics(file_path=os.path.join(input_folder, "summary_categories.json"))
    
    # Save the output JSON in the specified output folder with the given filename
    output_path = os.path.join(output_folder, f"{filename}.json")
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=4)
    
    logging.info(f"Company ad statistics saved to {output_path}")
    return summary
