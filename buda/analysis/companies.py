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

def query_on_demand_api(api_key, company_name, external_user_id="anonymous_user"):
    """
    Interact with the on-demand API to categorize a company.

    Sends a request to the on-demand API with the company name and retrieves the category.

    Parameters
    ----------
    api_key : str
        API key for authentication.
    company_name : str
        The name of the company to be categorized.
    external_user_id : str, optional
        An identifier for the user making the request, by default "anonymous_user".

    Returns
    -------
    str
        The category assigned to the company by the API.

    Notes
    -----
    If an error occurs during the API request, the function logs the error and returns "Unknown".
    """
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
    """
    Identify the market category of a company using the on-demand API.

    Parameters
    ----------
    company_name : str
        The name of the company to categorize.
    api_key : str
        API key for authentication.

    Returns
    -------
    str
        The category assigned to the company.

    Notes
    -----
    This function wraps the `query_on_demand_api` function and handles exceptions.
    """
    try:
        return query_on_demand_api(api_key, company_name)
    except Exception as e:
        logging.error(f"Error in identify_market_category for {company_name}: {e}")
        return "Unknown"

def assign_categories_async(data, api_key, debug, output_folder, save_frequency=10):
    """
    Assign categories to companies asynchronously, with intermediate JSON updates.

    Processes a list of company data, queries the API for each company,
    and saves the results periodically to a JSON file.

    Parameters
    ----------
    data : list
        A list of dictionaries containing company information.
    api_key : str
        API key for authentication.
    debug : bool
        Flag to enable or disable debug logging.
    output_folder : str
        The folder where output files will be saved.
    save_frequency : int, optional
        Frequency at which intermediate results are saved, by default 10.

    Returns
    -------
    dict
        A dictionary mapping company names to their assigned categories.

    Notes
    -----
    The function logs progress and errors, and saves intermediate results
    to 'categorized_data.json' in the specified output folder.
    """
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

def generate_statistics(data, output_folder):
    """
    Generate statistics from the categorized data and save them to a CSV file.

    Counts the number of companies per category and saves the statistics.

    Parameters
    ----------
    data : dict
        A dictionary mapping company names to categories.
    output_folder : str
        The folder where the statistics CSV will be saved.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing category statistics.

    Notes
    -----
    The statistics are saved to 'category_statistics.csv' in the specified output folder.
    """
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

def create_broad_category_summary(folder):
    """
    Load categorized data, map to broader categories, and save a summary.

    Maps existing categories to broader categories and counts the number
    of companies in each broad category.

    Parameters
    ----------
    folder : str
        The folder where 'categorized_data.json' is located and where the summary will be saved.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the summary of broad categories.

    Notes
    -----
    The summary is saved to 'summary_categories.json' in the specified folder.
    """
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

def get_company_ad_statistics(file_path="summary_categories.json"):
    """
    Retrieve company advertisement statistics from a summary JSON file.

    Parameters
    ----------
    file_path : str, optional
        Path to the summary JSON file, by default "summary_categories.json".

    Returns
    -------
    dict
        A dictionary containing the summary of company advertisement statistics.

    Notes
    -----
    The summary JSON should be structured with broad categories as keys and counts as values.
    """
    with open(file_path, 'r') as f:
        summary = json.load(f)
    return summary

def map_companies(data, api_key, output_folder="company_analysis_output_ufuk", logging_level=logging.INFO, debug=True):
    """
    Main function to map companies to categories and generate statistics.

    Processes the data to assign categories to companies, generate statistics,
    and save the results.

    Parameters
    ----------
    data : dict
        The input data containing company information.
    api_key : str
        API key for authentication.
    output_folder : str, optional
        The folder where output files will be saved, by default "company_analysis_output_ufuk".
    logging_level : int, optional
        Logging level to control the verbosity, by default logging.INFO.
    debug : bool, optional
        Flag to enable debug mode, by default True.

    Returns
    -------
    None

    Notes
    -----
    This function sets up logging, processes the data, and saves categorized data and statistics.
    """
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
    """
    Analyze companies by creating a broad category summary and saving statistics.

    Parameters
    ----------
    input_folder : str
        The folder where the input data ('categorized_data.json') is located.
    output_folder : str, optional
        The folder where output files will be saved, by default "company_analysis_output_ufuk".
    filename : str, optional
        The base filename for the output JSON file, by default "ad_companies_data_statistics".
    logging_level : int, optional
        Logging level to control the verbosity, by default logging.INFO.
    debug : bool, optional
        Flag to enable debug mode, by default True.

    Returns
    -------
    dict
        A dictionary containing the summary of company advertisement statistics.

    Notes
    -----
    This function generates a broad category summary, saves it, and logs the process.
    """
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