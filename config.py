# Database Configuration for Telecom Churn Analysis
# ================================================

# PostgreSQL Connection Settings
# Update these values with your actual PostgreSQL credentials

DB_CONFIG = {
    'host': 'localhost',           # PostgreSQL server host
    'port': 5432,                  # PostgreSQL server port
    'database': 'telecom_churn',   # Database name
    'user': 'postgres',            # PostgreSQL username
    'password': 'Alex4305'         # PostgreSQL password - CHANGE THIS!
}

# Instructions:
# 1. Replace 'password' above with your actual PostgreSQL password
# 2. If you're using a different username, update 'user' as well
# 3. If PostgreSQL is running on a different host/port, update those values
# 4. Save this file and run the setup scripts

# Example usage in Python:
# from config import DB_CONFIG
# loader = TelecomPostgresLoader(**DB_CONFIG)
