import os
import json
import requests
import logging
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import pandas as pd

# Define categories for Instagram accounts
predefined_categories = """
Please categorize the following Instagram account into one of these categories:
1. Influencer
2. Brand
3. Personal Blog
4. Art
5. Technology
6. Education
7. Fashion
8. Health and Wellness
9. Food and Beverage
10. Travel
11. Fitness
12. Entertainment
13. Non-profit
14. Sports
15. Photography
16. Gaming
17. Business
18. Cats
19. Dogs
20. Music
21. Personal

Answer with just the category name (e.g., 'Influencer').
"""

def query_instagram_api(api_key, account_name, external_user_id="instagram_user"):
    """
    Query the Instagram API to categorize an account.

    Sends a request to the API with the account name and receives the predicted category.

    Parameters
    ----------
    api_key : str
        API key for authentication.
    account_name : str
        The Instagram account name to be categorized.
    external_user_id : str, optional
        An identifier for the user making the request, by default "instagram_user".

    Returns
    -------
    str
        The predicted category for the Instagram account.

    Raises
    ------
    Exception
        If there is an error during the API request.
    """
    session_url = 'https://api.on-demand.io/chat/v1/sessions'
    headers = {'apikey': api_key}
    body = {"pluginIds": [], "externalUserId": external_user_id}
    try:
        response = requests.post(session_url, headers=headers, json=body)
        session_id = response.json()['data']['id']
        
        query = predefined_categories + f"Account: {account_name}"
        query_url = f'https://api.on-demand.io/chat/v1/sessions/{session_id}/query'
        query_body = {
            "endpointId": "predefined-openai-gpt4o",
            "query": query,
            "responseMode": "sync",
            "pluginIds": ["plugin-1716164040"]
        }
        
        query_response = requests.post(query_url, headers=headers, json=query_body)
        return query_response.json()["data"]["answer"]
    
    except Exception as e:
        logging.error(f"Error querying API for {account_name}: {e}")
        return "Unknown"

def assign_categories(data, api_key, output_folder, save_frequency=10):
    """
    Assign categories to Instagram accounts using the API.

    Processes a list of data, queries the API for each account, and saves the results periodically.

    Parameters
    ----------
    data : list
        A list of dictionaries containing account information.
    api_key : str
        API key for authentication.
    output_folder : str
        The folder where output files will be saved.
    save_frequency : int, optional
        Frequency at which intermediate results are saved, by default 10.

    Returns
    -------
    dict
        A dictionary mapping account names to their assigned categories.

    Raises
    ------
    Exception
        If there is an error during processing.
    """
    categorized_data = {}
    json_file_path = os.path.join(output_folder, "categorized_data.json")

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(query_instagram_api, api_key, item.get("title", "Unknown")): item
            for item in data
        }
        for i, future in enumerate(tqdm(as_completed(futures), total=len(futures))):
            item = futures[future]
            account_name = item.get("title", "Unknown")
            try:
                category = future.result()
                categorized_data[account_name] = category
            except Exception as e:
                categorized_data[account_name] = "Unknown"
                logging.error(f"Error processing {account_name}: {e}")

            if (i + 1) % save_frequency == 0:
                with open(json_file_path, "w") as f:
                    json.dump(categorized_data, f, indent=4)

    with open(json_file_path, "w") as f:
        json.dump(categorized_data, f, indent=4)
    
    return categorized_data

def generate_statistics(data, output_folder):
    """
    Generate statistics from categorized data and save to CSV.

    Counts the number of accounts per category and saves the statistics.

    Parameters
    ----------
    data : dict
        A dictionary mapping account names to categories.
    output_folder : str
        The folder where the statistics CSV will be saved.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing category statistics.
    """
    category_count = defaultdict(int)
    for category in data.values():
        category_count[category] += 1

    category_df = pd.DataFrame({
        "Category": list(category_count.keys()),
        "Number of Accounts": list(category_count.values())
    })

    category_df.to_csv(os.path.join(output_folder, "category_statistics.csv"), index=False)
    return category_df

def analyze_categories(data, output_folder):
    """
    Analyze and remap categories to broader categories.

    Maps the existing categories to predefined broader categories and counts them.

    Parameters
    ----------
    data : dict
        A dictionary mapping account names to categories.
    output_folder : str
        The folder where the analyzed category counts will be saved.

    Returns
    -------
    dict
        A dictionary mapping broader categories to counts.
    """
    category_mapping = {
        "Cats": "Pets",
        "Photography": "Art",
        "Influencer": "Lifestyle",
        "Personal Blog": "Lifestyle",
        "Music": "Art",
        "Unknown": "Friends",
        "Food and Beverage": "Lifestyle",
        "Art": "Art",
        "Fitness": "Lifestyle",
    }

    category_counts = {}

    for user, category in data.items():
        # Map the existing category to one of the broader categories
        mapped_category = category_mapping.get(category, "Other")
        # Increment the count for the mapped category
        category_counts[mapped_category] = category_counts.get(mapped_category, 0) + 1

    # Save the category counts to a JSON file
    with open(os.path.join(output_folder, "liked_posts_category_counts.json"), "w") as f:
        json.dump(category_counts, f, indent=4)
    return category_counts

def analyze_instagram_accounts(data, api_key, output_folder="instagram_analysis_output", debug=True):
    """
    Main function to analyze Instagram accounts.

    Processes the data to assign categories, generate statistics, and analyze categories.

    Parameters
    ----------
    data : dict
        The input data containing account information.
    api_key : str
        API key for authentication.
    output_folder : str, optional
        The folder where output files will be saved, by default "instagram_analysis_output".
    debug : bool, optional
        Flag to enable debug mode, by default True.

    Returns
    -------
    None
    """
    data = data["likes_media_likes"]
    
    with open(os.path.join('../data', "liked_posts.json"), "w") as f:
        total_likes = len(data)
        json.dump(total_likes, f, indent=4)
    
    os.makedirs(output_folder, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(output_folder, 'analysis.log'),
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    categorized_data = assign_categories(data, api_key, output_folder)
    generate_statistics(categorized_data, output_folder)
    analyze_categories(categorized_data, output_folder)