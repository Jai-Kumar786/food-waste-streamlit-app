Local Food Wastage Management System
A comprehensive, data-driven Streamlit web application designed to tackle local food wastage. This platform connects food providers with receivers, provides deep analytical insights into wastage trends, and offers a full suite of management tools for food listings and claims.

🚀 Overview & Problem Statement
Food wastage is a significant global issue. While surplus food from restaurants and households is often discarded, many individuals face food insecurity. This project aims to bridge that gap by creating a centralized system where surplus food can be listed, claimed, and distributed efficiently. The application leverages a SQL database for robust data storage and a user-friendly Streamlit interface for seamless interaction, data analysis, and management.

✨ Key Features
This application is more than just a data display; it's a complete management and analysis tool.

📊 Interactive Analytics Dashboard
Key Performance Indicators (KPIs): Get an at-a-glance overview of total providers, receivers, available food quantity, and claim completion rates.

Geographical Analysis: Visualize providers and receivers by city with an interactive bar chart, filterable by the first letter for improved readability.

Trend Analysis: Explore insights on top contributing provider types, food listings by city, and items nearing expiry.

Claims Insights: Analyze claim status distribution and the most popular meal types with interactive pie charts.

📝 Full CRUD Functionality
Manage Food Listings: A robust interface with separate tabs to Create, Read, Update, and Delete food listings.

Smart UI: Features cascading dropdowns (e.g., filter providers by letter before selecting a name) and direct ID input for efficient updates and deletions.

Data Validation: Includes both front-end and back-end checks to prevent invalid data entry, such as selecting expiry dates in the past.

✅ Claims Management Workflow
Centralized Claims Hub: A dedicated page to view and manage claims.

Status Filtering: Easily filter claims by their status ('Pending', 'Completed', 'Cancelled').

Actionable Workflow: Mark 'Pending' claims as 'Completed' or 'Cancelled' with a single click.

Smart Logic:

When a claim is completed, the corresponding food listing is automatically removed.

When a claim is cancelled, the system checks the item's expiry date and removes it only if it has expired.

🧼 Automated Data Cleaning & Enrichment
Pincode Extraction (Text Mining): Automatically parses address strings to extract and store 5-digit PIN codes in a dedicated column.

Date & Phone Number Standardization: Cleans and formats inconsistent date and phone number data from raw CSV files into a uniform, professional format before loading into the database.

🛠️ Tech Stack
Language: Python

Framework: Streamlit

Database: SQLite (via SQLAlchemy)

Data Manipulation: Pandas

Visualization: Plotly Express, Streamlit Native Charts

📂 Project Structure
local-food-wastage-management/
├── data/
│   ├── providers_data.csv
│   ├── receivers_data.csv
│   ├── food_listings_data.csv
│   └── claims_data.csv
├── database/
│   └── food_wastage.db
├── .venv/
├── app.py                  # Main Streamlit application
├── database_setup.py       # Creates the database schema
├── load_data.py            # Cleans and loads data into the DB
├── sql_queries.py          # Stores all analytical SQL queries
├── requirements.txt        # Project dependencies
└── README.md               # This file

⚙️ Setup and Installation
Follow these steps to get the project running locally.

Prerequisites
Python 3.8+

pip (Python package installer)

1. Clone the Repository
git clone <your-repository-url>
cd local-food-wastage-management

2. Create and Activate a Virtual Environment
Windows:

python -m venv .venv
.venv\Scripts\activate

macOS/Linux:

python3 -m venv .venv
source .venv/bin/activate

3. Install Dependencies
Install all the required Python libraries using the requirements.txt file.

pip install -r requirements.txt

▶️ How to Run the Application
The application requires a one-time database setup and data loading process.

1. Initialize the Database
This script creates the food_wastage.db file and sets up all the necessary tables and schemas.

python database_setup.py

2. Clean and Load the Data
This script reads the raw data from the data/ folder, performs all cleaning and enrichment operations, and populates the database.

python load_data.py

3. Launch the Streamlit App
Run the main application file. Streamlit will provide a local URL to view the app in your browser.

streamlit run app.py

💡 Future Enhancements
User Authentication: Implement a login system to differentiate between Providers, Receivers, and Admins, showing tailored interfaces for each role.

Geolocation Features: Integrate a map-based view (e.g., using st.map) to visualize the locations of available food items.

Real-time Notifications: Add a system to notify receivers when new food items are listed in their area.

Advanced Analytics: Incorporate predictive models to forecast food surplus hotspots or peak demand times.
