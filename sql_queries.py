# sql_queries.py
# This file centralizes all the SQL queries used in the Streamlit application.
# Keeping queries here makes the main app.py file cleaner and easier to manage.
# Each query is stored in a multi-line string variable for readability.

# --- Food Providers & Receivers Analysis ---

# Q1: How many food providers and receivers are there in each city?
q1_providers_receivers_by_city = """
SELECT 
    p.City, 
    COUNT(DISTINCT p.Provider_ID) AS NumberOfProviders,
    (SELECT COUNT(DISTINCT r.Receiver_ID) FROM Receivers r WHERE r.City = p.City) AS NumberOfReceivers
FROM 
    Providers p
GROUP BY 
    p.City
ORDER BY
    NumberOfProviders DESC, NumberOfReceivers DESC;
"""

# Q2: Which type of food provider (restaurant, grocery store, etc.) contributes the most food?
q2_top_provider_type_by_quantity = """
SELECT 
    Provider_Type, 
    SUM(Quantity) AS TotalQuantityDonated
FROM 
    Food_Listings
GROUP BY 
    Provider_Type
ORDER BY 
    TotalQuantityDonated DESC;
"""

# Q3: What is the contact information of food providers in a specific city?
# This query is a template; the city will be injected safely as a parameter.
q3_provider_contacts_by_city = """
SELECT 
    Name, 
    Type, 
    Address, 
    Contact
FROM 
    Providers
WHERE 
    City = :city_name;
"""

# Q4: Which receivers have claimed the most food quantity?
q4_top_receivers_by_claimed_quantity = """
SELECT
    r.Name AS ReceiverName,
    r.Type AS ReceiverType,
    SUM(fl.Quantity) AS TotalQuantityClaimed
FROM Claims c
JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
WHERE c.Status = 'Completed'
GROUP BY r.Receiver_ID
ORDER BY TotalQuantityClaimed DESC
LIMIT 10;
"""

# --- Food Listings & Availability Analysis ---

# Q5: What is the total quantity of available (non-expired) food?
q5_total_available_food_quantity = """
SELECT 
    SUM(Quantity) AS TotalAvailableQuantity
FROM 
    Food_Listings
WHERE 
    Expiry_Date >= DATE('now');
"""

# Q6: Which city has the highest number of active food listings?
q6_city_with_most_listings = """
SELECT 
    Location, 
    COUNT(Food_ID) AS NumberOfListings
FROM 
    Food_Listings
WHERE
    Expiry_Date >= DATE('now') AND Quantity > 0
GROUP BY 
    Location
ORDER BY 
    NumberOfListings DESC;
"""

# Q7: What are the most commonly available food types?
q7_most_common_food_types = """
SELECT 
    Food_Type, 
    COUNT(Food_ID) AS NumberOfListings
FROM 
    Food_Listings
WHERE
    Expiry_Date >= DATE('now') AND Quantity > 0
GROUP BY 
    Food_Type
ORDER BY 
    NumberOfListings DESC;
"""

# Q14 (Bonus): Which food items are nearing their expiry date (e.g., within 3 days)?

q14_nearing_expiry_items = """
SELECT 
    fl.Food_Name, 
    fl.Quantity, 
    fl.Expiry_Date, 
    fl.Location,
    p.Name as Provider_Name,
    p.Pincode,
    p.Contact
FROM 
    Food_Listings fl
JOIN 
    Providers p ON fl.Provider_ID = p.Provider_ID
WHERE 
    fl.Expiry_Date BETWEEN DATE('now') AND DATE('now', '+3 days')
    AND fl.Quantity > 0
ORDER BY 
    fl.Expiry_Date ASC;
"""

# --- Claims & Distribution Analysis ---

# Q8: How many food claims have been made for each food item?
q8_claims_per_food_item = """
SELECT 
    fl.Food_Name, 
    COUNT(c.Claim_ID) AS NumberOfClaims
FROM 
    Claims c
JOIN 
    Food_Listings fl ON c.Food_ID = fl.Food_ID
GROUP BY 
    fl.Food_Name
ORDER BY 
    NumberOfClaims DESC;
"""

# Q9: Which provider has had the highest number of successful (completed) food claims?
q9_provider_with_most_completed_claims = """
SELECT
    p.Name AS ProviderName,
    COUNT(c.Claim_ID) AS SuccessfulClaims
FROM Claims c
JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
JOIN Providers p ON fl.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Name
ORDER BY SuccessfulClaims DESC
LIMIT 10;
"""

# Q10: What percentage of food claims are completed vs. pending vs. cancelled?
q10_claim_status_distribution = """
SELECT
    Status,
    COUNT(Claim_ID) AS TotalClaims,
    ROUND((COUNT(Claim_ID) * 100.0 / (SELECT COUNT(*) FROM Claims)), 2) AS Percentage
FROM Claims
GROUP BY Status;
"""

# Q11: What is the average quantity of food claimed per receiver?
q11_avg_quantity_per_receiver = """
SELECT
    AVG(TotalQuantity) as AverageQuantityPerReceiver
FROM (
    SELECT
        r.Receiver_ID,
        SUM(fl.Quantity) as TotalQuantity
    FROM Claims c
    JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
    JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
    WHERE c.Status = 'Completed'
    GROUP BY r.Receiver_ID
);
"""

# Q12: Which meal type (breakfast, lunch, dinner, snacks) is claimed the most?
q12_most_claimed_meal_type = """
SELECT
    fl.Meal_Type,
    COUNT(c.Claim_ID) AS NumberOfClaims
FROM Claims c
JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
WHERE c.Status = 'Completed'
GROUP BY fl.Meal_Type
ORDER BY NumberOfClaims DESC;
"""

# Q13: What is the total quantity of food donated by each provider?
q13_total_donated_by_provider = """
SELECT
    p.Name,
    p.Type,
    SUM(fl.Quantity) AS TotalQuantityDonated
FROM Providers p
JOIN Food_Listings fl ON p.Provider_ID = fl.Provider_ID
GROUP BY p.Provider_ID
ORDER BY TotalQuantityDonated DESC;
"""

# Q15 (Bonus): What is the trend of claims over time?
q15_claims_trend_over_time = """
SELECT
    STRFTIME('%Y-%m', Timestamp) AS Month,
    COUNT(Claim_ID) AS NumberOfClaims
FROM Claims
GROUP BY Month
ORDER BY Month ASC;
"""

# --- Queries for App KPIs and Filters ---

# Query for main dashboard KPIs
kpi_query = """
SELECT
    (SELECT COUNT(*) FROM Providers) AS total_providers,
    (SELECT COUNT(*) FROM Receivers) AS total_receivers,
    (SELECT SUM(Quantity) FROM Food_Listings WHERE Expiry_Date >= DATE('now')) AS available_quantity,
    (SELECT ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Claims), 2) FROM Claims WHERE Status = 'Completed') AS completion_rate
"""
