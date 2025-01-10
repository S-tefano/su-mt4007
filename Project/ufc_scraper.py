import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import string

# Define weight classes globally
weight_classes = [
    {"class_name": "Strawweight", "lower_limit": 0, "upper_limit": 115},
    {"class_name": "Flyweight", "lower_limit": 115, "upper_limit": 125},
    {"class_name": "Bantamweight", "lower_limit": 125, "upper_limit": 135},
    {"class_name": "Featherweight", "lower_limit": 135, "upper_limit": 145},
    {"class_name": "Lightweight", "lower_limit": 145, "upper_limit": 155},
    {"class_name": "Super lightweight", "lower_limit": 155, "upper_limit": 165},
    {"class_name": "Welterweight", "lower_limit": 165, "upper_limit": 170},
    {"class_name": "Super welterweight", "lower_limit": 170, "upper_limit": 175},
    {"class_name": "Middleweight", "lower_limit": 175, "upper_limit": 185},
    {"class_name": "Super middleweight", "lower_limit": 185, "upper_limit": 195},
    {"class_name": "Light heavyweight", "lower_limit": 195, "upper_limit": 205},
    {"class_name": "Cruiserweight", "lower_limit": 205, "upper_limit": 225},
    {"class_name": "Heavyweight", "lower_limit": 225, "upper_limit": 265},
    {"class_name": "Super heavyweight", "lower_limit": 265, "upper_limit": float('inf')}
]

# Function to assign weight class
def assign_weight_class(weight):
    for weight_class in weight_classes:
        if weight_class["lower_limit"] < weight <= weight_class["upper_limit"]:
            return weight_class["class_name"]
    return None

# Function for scraping UFC data
def fetch_ufc_data():
    base_url = "http://www.ufcstats.com/statistics/fighters?char="
    letters = list(string.ascii_lowercase)
    data_frames = []

    for letter in letters:
        page_url = base_url + letter + "&page=all"
        print(f"Fetching data for {page_url}")
        
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the table
        table = soup.find('table', class_='b-statistics__table')
        
        if table:
            try:
                data = pd.read_html(str(table), flavor='bs4')[0]
                data_frames.append(data)
            except Exception as e:
                print(f"Failed to parse table for {page_url}: {e}")
        else:
            print(f"No table found for {page_url}")

    if data_frames:
        combined_data = pd.concat(data_frames, ignore_index=True)
        print(f"Scraped data shape: {combined_data.shape}")
        return combined_data
    else:
        print("No data was fetched.")
        return pd.DataFrame()

# Function to clean and process data
def clean_and_combine_data(data_frames):
    import pandas as pd
    import numpy as np

    # Debug: Confirm input type
    print(f"Type of data_frames: {type(data_frames)}")

    if not isinstance(data_frames, pd.DataFrame):
        raise ValueError("Input data_frames must be a pandas DataFrame")

    # Debug: Inspect DataFrame before processing
    print(f"Shape of data_frames: {data_frames.shape}")
    print(data_frames.head())

    # Explicitly check if DataFrame is empty
    if data_frames.empty:  # Use .empty to check
        print("The DataFrame is empty. Returning an empty DataFrame.")
        return pd.DataFrame()

    # Drop rows where all columns are NaN
    data_frames.dropna(how='all', inplace=True)
    print(f"Shape after dropping NaN rows: {data_frames.shape}")

    # Reset the index
    data_frames.reset_index(drop=True, inplace=True)

    # Ensure 'Wt.' column exists before processing
    if 'Wt.' in data_frames.columns:
        print("'Wt.' column exists. Cleaning weights...")
        data_frames['Wt.'] = data_frames['Wt.'].astype(str)
        data_frames['Wt.'] = data_frames['Wt.'].str.replace('lbs.', '', regex=False).str.strip()
        data_frames['Wt.'] = pd.to_numeric(data_frames['Wt.'], errors='coerce')

        # Handle missing weights explicitly
        if not data_frames['Wt.'].isnull().all():  # Check if all weights are not NaN
            most_common_weight = data_frames['Wt.'].mode()[0]
            data_frames['Wt.'].fillna(most_common_weight, inplace=True)
        else:
            print("All weights are missing. Skipping weight processing.")
    else:
        print("Column 'Wt.' is missing. Skipping weight processing.")

    # Assign weight classes if 'Wt.' exists
    if 'Wt.' in data_frames.columns:
        data_frames['Weight Class'] = data_frames['Wt.'].apply(assign_weight_class)
    else:
        print("'Wt.' column is missing. Cannot assign weight classes.")

    # Final debug output
    print(f"Final shape of cleaned data: {data_frames.shape}")
    print(data_frames.head())

    return data_frames

