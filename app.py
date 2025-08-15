# app.py
# This is the main script for the Streamlit web application.
# It provides the user interface for an advanced and robust claiming system.

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, date
import string  # Import the string module to get alphabets
import random  # Import to select a random receiver
import plotly.express as px
import re # Import for clickable phone numbers
# --- Page Configuration ---
st.set_page_config(
    page_title="Local Food Waste Management Dashboard",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- Database Connection ---
@st.cache_resource
def get_engine():
    """Creates a SQLAlchemy engine for connecting to the database."""
    return create_engine('sqlite:///database/food_wastage.db')


engine = get_engine()


# --- Helper Functions for DB Interaction ---
@st.cache_data(ttl=600)
def run_query(query: str, params: dict = None) -> pd.DataFrame:
    """Runs a SQL query safely and returns a DataFrame."""
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params)


def execute_mutation(query: str, params: dict = None, should_rerun=True):
    """Executes a data-modifying query (INSERT, UPDATE, DELETE)."""
    with engine.begin() as conn:
        conn.execute(text(query), params)
    st.cache_data.clear()
    if should_rerun:
        st.rerun()  # Automatically refresh the page to show changes


# --- Import Queries ---
from sql_queries import *

# --- Main Application UI ---
st.title("♻️ Local Food Waste Management Dashboard")
st.markdown("An interactive platform to connect food donors with receivers, reducing waste and fighting hunger.")

# --- Sidebar for Navigation and Filters ---
st.sidebar.title("Dashboard Controls")
page = st.sidebar.radio("Navigate", ["📊 Analytics Dashboard", "📝 Manage Food Listings", "✅ Manage Claims"])

st.sidebar.header("Global Filters")
try:
    alphabets = ['All'] + list(string.ascii_uppercase)
    selected_alphabet = st.sidebar.selectbox("Filter Cities by Letter", alphabets)

    city_query = "SELECT DISTINCT City FROM Providers"
    city_params = {}
    if selected_alphabet != 'All':
        city_query += " WHERE City LIKE :pattern"
        city_params['pattern'] = f"{selected_alphabet}%"
    city_query += " ORDER BY City;"

    cities = ['All'] + run_query(city_query, params=city_params)['City'].tolist()
    selected_city = st.sidebar.selectbox("Filter by City", cities)

    provider_types = ['All'] + run_query("SELECT DISTINCT Provider_Type FROM Food_Listings ORDER BY Provider_Type;")[
        'Provider_Type'].tolist()
    food_types = ['All'] + run_query("SELECT DISTINCT Food_Type FROM Food_Listings ORDER BY Food_Type;")[
        'Food_Type'].tolist()
    meal_types = ['All'] + run_query("SELECT DISTINCT Meal_Type FROM Food_Listings ORDER BY Meal_Type;")[
        'Meal_Type'].tolist()

    selected_provider_type = st.sidebar.selectbox("Filter by Provider Type", provider_types)
    selected_food_type = st.sidebar.selectbox("Filter by Food Type", food_types)
    selected_meal_type = st.sidebar.selectbox("Filter by Meal Type", meal_types)

except Exception as e:
    st.sidebar.error(f"Failed to load filters: {e}")
    selected_alphabet = "All"
    selected_city = "All"
    selected_provider_type = "All"
    selected_food_type = "All"
    selected_meal_type = "All"

# --- Build Dynamic WHERE clause for filters ---
where_clauses = []
params = {}
if selected_city != 'All':
    where_clauses.append("fl.Location = :city")
    params['city'] = selected_city
if selected_provider_type != 'All':
    where_clauses.append("fl.Provider_Type = :provider_type")
    params['provider_type'] = selected_provider_type
if selected_food_type != 'All':
    where_clauses.append("fl.Food_Type = :food_type")
    params['food_type'] = selected_food_type
if selected_meal_type != 'All':
    where_clauses.append("fl.Meal_Type = :meal_type")
    params['meal_type'] = selected_meal_type

filter_clause = " AND ".join(where_clauses)

# --- Analytics Dashboard Page ---
if page == "📊 Analytics Dashboard":
    st.header("Key Performance Indicators (KPIs)")
    try:
        kpi_data_df = run_query(kpi_query)
        if not kpi_data_df.empty:
            kpi_data = kpi_data_df.iloc[0].fillna(0).infer_objects(copy=False)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Providers", f"{int(kpi_data['total_providers']):,}")
            col2.metric("Total Receivers", f"{int(kpi_data['total_receivers']):,}")
            col3.metric("Available Food Qty", f"{int(kpi_data['available_quantity']):,}")
            col4.metric("Claim Completion Rate", f"{kpi_data['completion_rate']}%")
        else:
            st.warning("Could not calculate KPIs. The database might be empty.")
    except Exception as e:
        st.warning(f"Could not load KPIs: {e}")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Provider & Receiver Insights", "Food Availability & Trends", "Claims Analysis"])

    with tab1:
        st.subheader("Providers and Receivers by City")
        df_q1 = run_query(q1_providers_receivers_by_city)
        if selected_alphabet != 'All':
            df_q1 = df_q1[df_q1['City'].str.startswith(selected_alphabet)]

        if not df_q1.empty:
            st.bar_chart(df_q1.set_index('City'))
        else:
            st.info("No provider/receiver data available for the selected letter.")

        st.subheader("Top Provider Types by Quantity Donated")
        st.dataframe(run_query(q2_top_provider_type_by_quantity), use_container_width=True)

    with tab2:
        st.subheader("Food Listings by City")
        st.dataframe(run_query(q6_city_with_most_listings), use_container_width=True)

        st.subheader("⚠️ Food Nearing Expiry (Next 3 Days)")
        st.dataframe(run_query(q14_nearing_expiry_items), use_container_width=True)

    with tab3:
        # --- UPDATED: Claim Status Pie Chart ---
        st.subheader("Claim Status Distribution")
        df_q10 = run_query(q10_claim_status_distribution)
        if not df_q10.empty:
            fig1 = px.pie(df_q10, names='Status', values='TotalClaims', title='Claim Status Breakdown')
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No claim data available.")

        # --- UPDATED: Meal Type Pie Chart ---
        st.subheader("Most Claimed Meal Types")
        df_q12 = run_query(q12_most_claimed_meal_type)
        if not df_q12.empty:
            fig2 = px.pie(df_q12, names='Meal_Type', values='NumberOfClaims', title='Popularity of Meal Types')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No meal type claim data available.")


# --- Manage Food Listings Page (CRUD) ---
elif page == "📝 Manage Food Listings":
    st.header("Manage Food Listings")

    crud_tab1, crud_tab2, crud_tab3 = st.tabs(["➕ Create Listing", "✏️ Update Listing", "❌ Delete Listing"])

    with crud_tab1:
        st.subheader("Add a New Food Listing")
        provider_alphabet = st.selectbox("Filter Provider by Letter", ['All'] + list(string.ascii_uppercase),
                                         key="provider_alpha")
        with st.form("add_listing_form", clear_on_submit=True):
            provider_query = "SELECT Provider_ID, Name FROM Providers"
            provider_params = {}
            if provider_alphabet != 'All':
                provider_query += " WHERE Name LIKE :pattern"
                provider_params['pattern'] = f"{provider_alphabet}%"
            provider_query += " ORDER BY Name;"

            provider_names = run_query(provider_query, params=provider_params)
            provider_map = dict(zip(provider_names['Name'], provider_names['Provider_ID']))

            col1, col2 = st.columns(2)
            with col1:
                selected_provider_name = st.selectbox("Select Provider", options=provider_map.keys())
                food_name = st.text_input("Food Name")
                quantity = st.number_input("Quantity", min_value=1, step=1)
            with col2:
                expiry_date = st.date_input("Expiry Date", min_value=datetime.now().date())
                food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
                meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])

            submitted = st.form_submit_button("Add Listing")

            if submitted:
                if not selected_provider_name:
                    st.error("No provider selected. Please select a provider from the list.")
                elif not food_name:
                    st.error("Food Name cannot be empty.")
                elif expiry_date < datetime.now().date():
                    st.error("Expiry Date cannot be in the past.")
                else:
                    try:
                        with engine.begin() as conn:
                            provider_id = provider_map[selected_provider_name]
                            provider_details_df = pd.read_sql(
                                text("SELECT Type, City FROM Providers WHERE Provider_ID = :pid"), conn,
                                params={'pid': provider_id})
                            provider_details = provider_details_df.iloc[0]

                            insert_listing_query = """
                            INSERT INTO Food_Listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                            VALUES (:fn, :qty, :exp, :pid, :pt, :loc, :ft, :mt)
                            """
                            params_insert = {
                                "fn": food_name, "qty": quantity, "exp": expiry_date,
                                "pid": provider_id, "pt": provider_details['Type'],
                                "loc": provider_details['City'], "ft": food_type, "mt": meal_type
                            }
                            result = conn.execute(text(insert_listing_query), params_insert)

                            new_food_id = result.lastrowid

                            receiver_ids_df = pd.read_sql(text("SELECT Receiver_ID FROM Receivers"), conn)
                            if not receiver_ids_df.empty:
                                random_receiver_id = random.choice(receiver_ids_df['Receiver_ID'].tolist())

                                insert_claim_query = """
                                INSERT INTO Claims (Food_ID, Receiver_ID, Status)
                                VALUES (:fid, :rid, 'Pending')
                                """
                                conn.execute(text(insert_claim_query), {'fid': new_food_id, 'rid': random_receiver_id})
                                st.success(f"Successfully added '{food_name}' and created a pending claim!")
                            else:
                                st.warning("Listing added, but no receivers were available to create a pending claim.")

                        st.cache_data.clear()
                        st.rerun()

                    except Exception as e:
                        st.error(f"An error occurred: {e}")

    with crud_tab2:
        st.subheader("Update an Existing Food Listing")
        update_id = st.number_input("Enter the Food ID of the listing to update:", min_value=1, step=1, key="update_id")

        if update_id:
            current_data_df = run_query("SELECT * FROM Food_Listings WHERE Food_ID = :id", params={'id': update_id})

            if not current_data_df.empty:
                current_data = current_data_df.iloc[0]
                with st.form("update_listing_form"):
                    st.write(f"**Updating:** {current_data['Food_Name']}")
                    new_quantity = st.number_input("Update Quantity", min_value=1, step=1,
                                                   value=int(current_data['Quantity']))

                    current_expiry = pd.to_datetime(current_data['Expiry_Date']).date()
                    # --- FIX: Removed min_value from this date_input ---
                    new_expiry_date = st.date_input("Update Expiry Date", value=current_expiry)

                    update_submitted = st.form_submit_button("Update Listing")

                    if update_submitted:
                        # Add validation check here instead of in the widget
                        if new_expiry_date < datetime.now().date():
                            st.error("Expiry Date cannot be in the past.")
                        else:
                            update_query = "UPDATE Food_Listings SET Quantity = :qty, Expiry_Date = :exp WHERE Food_ID = :id"
                            execute_mutation(update_query,
                                             params={'qty': new_quantity, 'exp': new_expiry_date, 'id': update_id})
                            st.success(f"Successfully updated listing ID: {update_id}")
            else:
                st.warning(f"No listing found with Food ID: {update_id}")

    with crud_tab3:
        st.subheader("Delete a Food Listing")
        delete_id = st.number_input("Enter the Food ID of the listing to delete:", min_value=1, step=1, key="delete_id")

        if delete_id:
            delete_data_df = run_query("SELECT Food_Name FROM Food_Listings WHERE Food_ID = :id",
                                       params={'id': delete_id})
            if not delete_data_df.empty:
                st.warning(
                    f"You are about to delete **{delete_data_df.iloc[0]['Food_Name']}** (ID: {delete_id}). This action cannot be undone.")
                if st.button("❌ Confirm Deletion"):
                    try:
                        delete_query = "DELETE FROM Food_Listings WHERE Food_ID = :id"
                        execute_mutation(delete_query, params={'id': delete_id})
                        st.success(f"Successfully deleted listing ID: {delete_id}")
                    except Exception as e:
                        st.error(f"An error occurred during deletion: {e}")
            else:
                st.warning(f"No listing found with Food ID: {delete_id}")

    st.markdown("---")

    st.subheader("Current Food Listings")
    # --- UPDATED: Pagination Logic ---
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1

    PAGE_SIZE = 25

    # Count total records for pagination controls
    count_query = "SELECT COUNT(*) FROM Food_Listings fl"
    if filter_clause:
        count_query += f" WHERE {filter_clause.replace('p.', 'fl.')}"  # Adjust alias for count

    total_records = run_query(count_query, params=params).iloc[0, 0]
    total_pages = (total_records // PAGE_SIZE) + (1 if total_records % PAGE_SIZE > 0 else 0)

    try:
        offset = (st.session_state.page_number - 1) * PAGE_SIZE
        listings_query = f"""
        SELECT 
            fl.Food_ID, fl.Food_Name, fl.Quantity, fl.Expiry_Date, p.Name AS Provider_Name,
            fl.Provider_Type, p.Pincode, p.Contact, fl.Location, fl.Food_Type, fl.Meal_Type
        FROM Food_Listings fl JOIN Providers p ON fl.Provider_ID = p.Provider_ID
        """
        if filter_clause:
            listings_query += f" WHERE {filter_clause}"
        listings_query += f" ORDER BY fl.Expiry_Date DESC LIMIT {PAGE_SIZE} OFFSET {offset}"

        current_listings_df = run_query(listings_query, params=params)

        if not current_listings_df.empty:
            if 'Expiry_Date' in current_listings_df.columns:
                current_listings_df['Expiry_Date'] = pd.to_datetime(current_listings_df['Expiry_Date']).dt.strftime(
                    '%Y-%m-%d')

            if 'Contact' in current_listings_df.columns:
                def make_clickable(phone):
                    if phone:
                        tel_link = re.sub(r'\D', '', str(phone))
                        return f"[{phone}](tel:{tel_link})"
                    return "N/A"


                current_listings_df['Contact'] = current_listings_df['Contact'].apply(make_clickable)

            st.markdown(current_listings_df.to_markdown(index=False), unsafe_allow_html=True)

            # Pagination controls
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.session_state.page_number > 1:
                    if st.button("⬅️ Previous"):
                        st.session_state.page_number -= 1
                        st.rerun()
            with col2:
                st.write(f"Page {st.session_state.page_number} of {total_pages}")
            with col3:
                if st.session_state.page_number < total_pages:
                    if st.button("Next ➡️"):
                        st.session_state.page_number += 1
                        st.rerun()
        else:
            st.info("No listings found for the current filters.")

    except Exception as e:
        st.error(f"Could not load food listings: {e}")

# --- Manage Claims Page ---
elif page == "✅ Manage Claims":
    st.header("Manage Claims")

    status_filter = st.selectbox("Filter Claims by Status", ['Pending', 'Completed', 'Cancelled'])

    claims_query = """
        SELECT
            c.Claim_ID,
            c.Food_ID,
            fl.Food_Name,
            fl.Expiry_Date,
            r.Name as Receiver_Name,
            c.Timestamp
        FROM Claims c
        LEFT JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
        JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
        WHERE c.Status = :status
        ORDER BY c.Timestamp DESC;
    """
    claims_df = run_query(claims_query, params={'status': status_filter})

    st.dataframe(claims_df, use_container_width=True)

    if status_filter == 'Pending' and not claims_df.empty:
        st.subheader("Update Claim Status")
        claim_id_to_update = st.number_input("Enter the Claim ID to update:", min_value=1, step=1)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Mark as Completed"):
                if claim_id_to_update:
                    if claim_id_to_update in claims_df['Claim_ID'].values:
                        try:
                            with engine.begin() as conn:
                                food_id_df = pd.read_sql(text("SELECT Food_ID FROM Claims WHERE Claim_ID = :cid"), conn,
                                                         params={'cid': claim_id_to_update})
                                food_id = food_id_df.iloc[0]['Food_ID']

                                conn.execute(text("UPDATE Claims SET Status = 'Completed' WHERE Claim_ID = :cid"),
                                             {'cid': claim_id_to_update})

                                conn.execute(text("DELETE FROM Food_Listings WHERE Food_ID = :fid"), {'fid': food_id})

                            st.success(f"Claim {claim_id_to_update} completed and food listing removed!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"An error occurred: {e}")
                    else:
                        st.error("The entered Claim ID is not a valid pending claim.")

        with col2:
            if st.button("Cancel Claim"):
                if claim_id_to_update:
                    if claim_id_to_update in claims_df['Claim_ID'].values:
                        try:
                            with engine.begin() as conn:
                                food_info_df = pd.read_sql(text(
                                    "SELECT Food_ID, Expiry_Date FROM Food_Listings WHERE Food_ID = (SELECT Food_ID FROM Claims WHERE Claim_ID = :cid)"),
                                                           conn, params={'cid': claim_id_to_update})

                                conn.execute(text("UPDATE Claims SET Status = 'Cancelled' WHERE Claim_ID = :cid"),
                                             {'cid': claim_id_to_update})

                                # Only check expiry and delete if the food item still exists
                                if not food_info_df.empty:
                                    food_id = food_info_df.iloc[0]['Food_ID']
                                    expiry_date_str = food_info_df.iloc[0]['Expiry_Date']
                                    expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()

                                    if expiry_date < date.today():
                                        conn.execute(text("DELETE FROM Food_Listings WHERE Food_ID = :fid"),
                                                     {'fid': food_id})
                                        st.warning(
                                            f"Claim {claim_id_to_update} cancelled. Associated food item was expired and has been removed.")
                                    else:
                                        st.success(f"Claim {claim_id_to_update} has been cancelled!")
                                else:
                                    st.success(
                                        f"Claim {claim_id_to_update} has been cancelled! (Associated food item no longer exists).")

                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"An error occurred: {e}")
                    else:
                        st.error("The entered Claim ID is not a valid pending claim.")
    elif status_filter == 'Pending' and claims_df.empty:
        st.info("No pending claims to manage at this time.")
