
# This script is responsible for creating the database and all necessary tables.
# It implements best practices like foreign keys, constraints, and indexes
# to ensure data integrity and query performance from the start.

import sqlalchemy
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    CheckConstraint,
    func,
)

# --- Database Engine and Metadata ---
# We create a single engine instance that can be reused throughout the application.
# 'sqlite:///database/food_wastage.db' specifies a file-based SQLite database.
# The 'echo=True' parameter is useful for debugging as it logs all SQL commands.
engine = create_engine('sqlite:///database/food_wastage.db', echo=True)

# MetaData is a container object that keeps together many different features
# of a database (or multiple databases) being described.
meta = MetaData()


# --- Table Definitions ---
# We define our tables using the SQLAlchemy Core Table construct.

# 1. Providers Table
# Stores information about the entities providing the food.
providers = Table(
    'Providers', meta,
    Column('Provider_ID', Integer, primary_key=True),
    Column('Name', String, nullable=False),
    Column('Type', String, nullable=False),
    Column('Address', String),
    # An index on 'City' will speed up filtering operations by location.
    Column('City', String, nullable=False, index=True),
    Column('Contact', String)
)

# 2. Receivers Table
# Stores information about the NGOs or individuals receiving the food.
receivers = Table(
    'Receivers', meta,
    Column('Receiver_ID', Integer, primary_key=True),
    Column('Name', String, nullable=False),
    Column('Type', String, nullable=False),
    # Indexing 'City' is important for location-based searches.
    Column('City', String, nullable=False, index=True),
    Column('Contact', String),
    # NEW: Add a column for the extracted pincode, and index it for filtering.
    Column('Pincode', String, index=True),

)

# 3. Food Listings Table
# This is the central table, tracking all available food items.
food_listings = Table(
    'Food_Listings', meta,
    Column('Food_ID', Integer, primary_key=True),
    Column('Food_Name', String, nullable=False),
    # A CHECK constraint ensures data validity at the database level.
    # Here, we ensure quantity is always a positive number.
    Column('Quantity', Integer, CheckConstraint('Quantity > 0'), nullable=False),
    Column('Expiry_Date', Date, nullable=False, index=True),
    # A ForeignKey constraint creates a link to the 'Providers' table.
    # It ensures that every food listing is associated with a valid provider.
    # 'ondelete="CASCADE"' means if a provider is deleted, their listings are also deleted.
    Column('Provider_ID', Integer, ForeignKey('Providers.Provider_ID', ondelete="CASCADE"), nullable=False, index=True),
    Column('Provider_Type', String, index=True),
    Column('Location', String, index=True),
    Column('Food_Type', String, index=True),
    Column('Meal_Type', String, index=True)
)

# 4. Claims Table
# Tracks which receivers have claimed which food items.
claims = Table(
    'Claims', meta,
    Column('Claim_ID', Integer, primary_key=True),
    # ForeignKeys link this table to both Food_Listings and Receivers.
    Column('Food_ID', Integer, ForeignKey('Food_Listings.Food_ID', ondelete="CASCADE"), nullable=False, index=True),
    Column('Receiver_ID', Integer, ForeignKey('Receivers.Receiver_ID', ondelete="CASCADE"), nullable=False, index=True),
    # A CHECK constraint enforces a specific set of allowed values for 'Status'.
    Column('Status', String, CheckConstraint("Status IN ('Pending', 'Completed', 'Cancelled')"), nullable=False, index=True),
    # 'server_default=func.now()' automatically sets the timestamp to the current time
    # when a new claim is created.
    Column('Timestamp', DateTime, nullable=False, server_default=func.now(), index=True)
)


# --- Create Tables in the Database ---
def create_database():
    """
    Creates all defined tables in the database.
    This function is called to initialize the database schema.
    """
    print("Creating database tables...")
    # The 'create_all' method checks for the existence of each table before creating it.
    meta.create_all(engine)
    print("Database tables created successfully.")

if __name__ == '__main__':
    # This allows the script to be run directly from the command line
    # to set up the database.
    create_database()