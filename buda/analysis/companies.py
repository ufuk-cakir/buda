import pandas as pd
import json
from collections import defaultdict
from buda.utils import load_data


def identify_market_category(company_name):
    # TODO: Implement logic with LLM API call
    company_market_mapping = {
        "ADARA": "Travel",
        "Liquid I.V.": "Health",
        "The Motherhood Inc.": "Media",
        "Code3": "Marketing",
        "Spotify": "Entertainment",
        "Netflix": "Entertainment",
        "Amazon": "E-commerce",
        "Apple": "Technology",
        "Google": "Technology",
        "Microsoft": "Technology",
        "Samsung": "Electronics",
        "Nike": "Sportswear",
        "Coca-Cola": "Beverage"
    }
    return company_market_mapping.get(company_name, "Unknown")



# Function to assign categories to companies using LLM lookup
def assign_categories(data):
    for item in data:
        print(item)
        company = item["advertiser_name"]
        item["category"] = identify_market_category(company)
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

def analyze_companies(data):
    data = data["ig_custom_audiences_all_types"]
    categorized_data = assign_categories(data)
    df= generate_statistics(categorized_data)
    return df
    
    

