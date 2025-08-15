# load_data.py
# This script handles the one-time task of loading data from CSV files
# into the SQLite database. It includes data cleaning and is idempotent.

import pandas as pd
from sqlalchemy import create_engine, text
import os
import re  # Import the regular expression module for phone number cleaning
import random  # Import the random module to generate phone numbers

# --- Configuration ---
DB_PATH = 'sqlite:///database/food_wastage.db'
DATA_FOLDER = 'data'
TABLE_NAMES = {
    'providers_data.csv': 'Providers',
    'receivers_data.csv': 'Receivers',
    'food_listings_data.csv': 'Food_Listings',
    'claims_data.csv': 'Claims'
}

# Create a database engine
engine = create_engine(DB_PATH)


def generate_random_phone():
    """Generates a realistic-looking random 10-digit US phone number."""
    area_code = random.randint(201, 999)  # Avoids codes like 000 or 1XX
    central_office_code = random.randint(100, 999)
    line_number = random.randint(1000, 9999)
    return f"({area_code}) {central_office_code:03d}-{line_number:04d}"

def extract_pincode(address):
    """
    Uses a regular expression to find a 5-digit number at the end of a string,
    which is assumed to be the PIN code.
    """
    if not isinstance(address, str):
        return None
    # This regex looks for a sequence of 5 digits (\d{5}) at the end of the string ($).
    match = re.search(r'\d{5}$', address)
    if match:
        return match.group(0) # Return the found 5-digit string
    return None # Return None if no 5-digit number is found at the end
def standardize_phone_number(phone):
    """
    Uses regular expressions to find all digits in a phone number string
    and formats them into a standard (XXX) XXX-XXXX format.
    Returns None if the number is not valid.
    """
    if not isinstance(phone, str):
        return None

    # Find all digits in the string
    digits = re.findall(r'\d', phone)

    # Check if we have exactly 10 digits
    if len(digits) == 10:
        return f"({digits[0]}{digits[1]}{digits[2]}) {digits[3]}{digits[4]}{digits[5]}-{digits[6]}{digits[7]}{digits[8]}{digits[9]}"
    else:
        # Return None for invalid formats, which will be replaced later
        return None


def clean_data(df, table_name):
    """
    Cleans the DataFrame by normalizing column names, trimming whitespace,
    and handling data types before loading into the database.
    """
    # Normalize column names (e.g., 'Provider ID' -> 'provider_id')
    df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]

    # Trim whitespace from all string/object columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()

    # --- Standardize Phone Numbers ---
    if 'contact' in df.columns:
        print(f"Standardizing and generating phone numbers for {table_name}...")
        # First, try to standardize existing numbers
        df['contact'] = df['contact'].apply(standardize_phone_number)

        # --- NEW: Generate random numbers for any that are still null ---
        df['contact'] = df['contact'].apply(lambda x: generate_random_phone() if pd.isnull(x) else x)

    # --- Standardize Date Columns ---
    if 'expiry_date' in df.columns:
        # This line converts the column to datetime objects, then the `.dt.date` part
        # strips out the time, leaving only the YYYY-MM-DD date.
        df['expiry_date'] = pd.to_datetime(df['expiry_date'], errors='coerce').dt.date
    if 'timestamp' in df.columns:
        # For timestamps, we want to keep the time, so we don't use .dt.date here
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # Drop rows with invalid dates if any
    df.dropna(subset=[col for col in ['expiry_date', 'timestamp'] if col in df.columns], inplace=True)
    # Inside the clean_data function in load_data.py

    # --- NEW: Pincode Extraction ---
    if 'address' in df.columns:
        print(f"Extracting PIN codes for {table_name}...")
        df['pincode'] = df['address'].apply(extract_pincode)

    # Ensure primary keys are unique
    pk_map = {
        'Providers': 'provider_id',
        'Receivers': 'receiver_id',
        'Food_Listings': 'food_id',
        'Claims': 'claim_id'
    }
    if table_name in pk_map:
        pk = pk_map[table_name]
        df.drop_duplicates(subset=[pk], keep='first', inplace=True)

    return df


def load_data():
    """
    Main function to clear existing data and load fresh data from CSVs.
    """
    print("Starting data loading process...")
    with engine.connect() as conn:
        # --- Make the script idempotent by clearing tables first ---
        print("Clearing existing data from tables...")
        conn.execute(text("DELETE FROM Claims;"))
        conn.execute(text("DELETE FROM Food_Listings;"))
        conn.execute(text("DELETE FROM Receivers;"))
        conn.execute(text("DELETE FROM Providers;"))
        conn.commit()  # Commit the deletions
        print("Tables cleared.")

        # --- Load new data from CSV files ---
        for csv_file, table_name in TABLE_NAMES.items():
            file_path = os.path.join(DATA_FOLDER, csv_file)
            if os.path.exists(file_path):
                print(f"Processing {csv_file} -> {table_name}...")
                try:
                    df = pd.read_csv(file_path)

                    # Clean the data using our updated function
                    df_cleaned = clean_data(df, table_name)

                    # Load data into the SQL table
                    df_cleaned.to_sql(table_name, con=engine, if_exists='append', index=False)
                    print(f"Successfully loaded {len(df_cleaned)} rows into {table_name}.")
                except Exception as e:
                    print(f"Error loading data for {table_name}: {e}")
            else:
                print(f"Warning: {csv_file} not found in {DATA_FOLDER}. Skipping.")

    print("\nData loading process completed.")


if __name__ == '__main__':
    load_data()
