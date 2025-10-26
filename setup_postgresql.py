"""
PostgreSQL Data Loader for Telecom Customer Churn Analysis
==========================================================

This script loads the telecom customer churn dataset into PostgreSQL
and sets up the database for analysis.
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

class TelecomPostgresLoader:
    def __init__(self, host='localhost', port=5432, database='telecom_churn', 
                 user='postgres', password='Alex4305'):
        """Initialize PostgreSQL connection parameters"""
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.engine = None
        
    def create_connection(self):
        """Create PostgreSQL connection"""
        try:
            # Create connection string
            conn_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            
            # Create SQLAlchemy engine
            self.engine = create_engine(conn_string)
            
            # Test connection
            self.connection = self.engine.connect()
            print(f"✅ Successfully connected to PostgreSQL database: {self.database}")
            return True
            
        except Exception as e:
            print(f"❌ Error connecting to PostgreSQL: {e}")
            print("\n📋 Setup Instructions:")
            print("1. Install PostgreSQL: https://www.postgresql.org/download/")
            print("2. Create database: createdb telecom_churn")
            print("3. Update connection parameters in this script")
            return False
    
    def create_database(self):
        """Create the telecom_churn database if it doesn't exist"""
        try:
            # Connect to default postgres database to create new database
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database='postgres',  # Connect to default database
                user=self.user,
                password=self.password
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.database,))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f"CREATE DATABASE {self.database}")
                print(f"✅ Created database: {self.database}")
            else:
                print(f"✅ Database {self.database} already exists")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            return False
    
    def load_data_from_csv(self, csv_path):
        """Load data from CSV file into PostgreSQL"""
        try:
            print("📊 Loading telecom customer data from CSV...")
            
            # Read CSV file
            df = pd.read_csv(csv_path)
            
            # Clean the data
            df = self.clean_data(df)
            
            # Check if table exists and drop views first if they exist
            from sqlalchemy import text
            with self.engine.connect() as conn:
                # Drop views first to avoid dependency issues
                try:
                    conn.execute(text("DROP VIEW IF EXISTS customer_segments CASCADE"))
                    conn.execute(text("DROP VIEW IF EXISTS churn_summary CASCADE"))
                    conn.commit()
                except:
                    pass  # Views might not exist yet
                
                # Drop table if it exists
                try:
                    conn.execute(text("DROP TABLE IF EXISTS telecom_customers CASCADE"))
                    conn.commit()
                except:
                    pass
            
            # Load into PostgreSQL
            df.to_sql('telecom_customers', self.engine, if_exists='append', index=False)
            
            print(f"✅ Successfully loaded {len(df)} records into telecom_customers table")
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def clean_data(self, df):
        """Clean and prepare data for PostgreSQL"""
        print("🧹 Cleaning data...")
        
        # Clean TotalCharges column
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        df['TotalCharges'].fillna(0, inplace=True)
        
        # Ensure proper data types
        df['SeniorCitizen'] = df['SeniorCitizen'].astype(int)
        df['tenure'] = df['tenure'].astype(int)
        df['MonthlyCharges'] = df['MonthlyCharges'].astype(float)
        df['TotalCharges'] = df['TotalCharges'].astype(float)
        
        print("✅ Data cleaning completed")
        return df
    
    def create_analysis_views(self):
        """Create useful views for analysis"""
        try:
            print("📈 Creating analysis views...")
            
            # Create customer segments view
            create_segments_view = """
            CREATE OR REPLACE VIEW customer_segments AS
            SELECT 
                "customerID",
                gender,
                "SeniorCitizen",
                "Partner",
                "Dependents",
                tenure,
                "MonthlyCharges",
                "TotalCharges",
                "Contract",
                "InternetService",
                "Churn",
                CASE 
                    WHEN "Contract" = 'Month-to-month' AND tenure < 12 THEN 'High Risk - New Month-to-Month'
                    WHEN "Contract" = 'Month-to-month' AND tenure >= 12 THEN 'Medium Risk - Established Month-to-Month'
                    WHEN "Contract" = 'One year' AND tenure < 6 THEN 'Medium Risk - New Annual'
                    WHEN "Contract" = 'Two year' THEN 'Low Risk - Long-term'
                    ELSE 'Stable - Established Annual'
                END AS customer_segment,
                CASE 
                    WHEN "Contract" = 'Month-to-month' AND tenure < 12 THEN 'High Risk'
                    WHEN "Contract" = 'Month-to-month' AND tenure < 24 THEN 'Medium Risk'
                    WHEN "Contract" = 'One year' AND tenure < 6 THEN 'Medium Risk'
                    ELSE 'Low Risk'
                END AS churn_risk,
                CASE 
                    WHEN "TotalCharges" > 0 THEN "TotalCharges"
                    ELSE "MonthlyCharges" * tenure 
                END AS clv
            FROM telecom_customers;
            """
            
            # Create churn summary view
            create_churn_summary_view = """
            CREATE OR REPLACE VIEW churn_summary AS
            SELECT 
                "Contract",
                "InternetService",
                CASE 
                    WHEN "SeniorCitizen" = 1 THEN 'Senior'
                    ELSE 'Non-Senior'
                END AS age_group,
                CASE 
                    WHEN "Partner" = 'Yes' AND "Dependents" = 'Yes' THEN 'Family'
                    WHEN "Partner" = 'Yes' OR "Dependents" = 'Yes' THEN 'Couple/Single Parent'
                    ELSE 'Single'
                END AS household_type,
                COUNT(*) AS customer_count,
                ROUND(AVG("MonthlyCharges")::numeric, 2) AS avg_monthly_charges,
                ROUND(AVG(tenure)::numeric, 1) AS avg_tenure_months,
                SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
                ROUND((SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*))::numeric, 2) AS churn_rate_percent
            FROM telecom_customers
            GROUP BY "Contract", "InternetService", age_group, household_type;
            """
            
            # Execute view creation
            from sqlalchemy import text
            with self.engine.connect() as conn:
                conn.execute(text(create_segments_view))
                conn.execute(text(create_churn_summary_view))
                conn.commit()
            
            print("✅ Analysis views created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating views: {e}")
            return False
    
    def verify_setup(self):
        """Verify the database setup"""
        try:
            print("🔍 Verifying database setup...")
            
            from sqlalchemy import text
            with self.engine.connect() as conn:
                # Check table exists
                result = conn.execute(text("""
                    SELECT COUNT(*) as total_customers,
                           SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) as churned_customers,
                           ROUND((SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*))::numeric, 2) as churn_rate
                    FROM telecom_customers;
                """))
                
                row = result.fetchone()
                print(f"✅ Database verification:")
                print(f"   - Total customers: {row[0]:,}")
                print(f"   - Churned customers: {row[1]:,}")
                print(f"   - Churn rate: {row[2]}%")
                
                # Check views exist
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM customer_segments;
                """))
                view_count = result.fetchone()[0]
                print(f"   - Customer segments view: {view_count:,} records")
                
            return True
            
        except Exception as e:
            print(f"❌ Error verifying setup: {e}")
            return False
    
    def run_sample_queries(self):
        """Run sample queries to test the setup"""
        try:
            print("🧪 Running sample queries...")
            
            from sqlalchemy import text
            with self.engine.connect() as conn:
                # Sample query 1: Churn by contract
                print("\n📊 Sample Query 1: Churn Rate by Contract Type")
                result = conn.execute(text("""
                    SELECT "Contract",
                           COUNT(*) as total_customers,
                           SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) as churned_customers,
                           ROUND((SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*))::numeric, 2) as churn_rate_percent
                    FROM telecom_customers
                    GROUP BY "Contract"
                    ORDER BY churn_rate_percent DESC;
                """))
                
                for row in result:
                    print(f"   {row[0]}: {row[3]}% churn rate ({row[2]}/{row[1]} customers)")
                
                # Sample query 2: Revenue impact
                print("\n💰 Sample Query 2: Revenue Impact")
                result = conn.execute(text("""
                    SELECT 
                        SUM(CASE WHEN "Churn" = 'Yes' THEN "MonthlyCharges" ELSE 0 END) as monthly_revenue_lost,
                        SUM(CASE WHEN "Churn" = 'Yes' THEN "MonthlyCharges" * 12 ELSE 0 END) as annual_revenue_lost
                    FROM telecom_customers;
                """))
                
                row = result.fetchone()
                print(f"   Monthly revenue lost: ${row[0]:,.2f}")
                print(f"   Annual revenue lost: ${row[1]:,.2f}")
                
            return True
            
        except Exception as e:
            print(f"❌ Error running sample queries: {e}")
            return False
    
    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        print("🔌 Database connection closed")

def main():
    """Main function to set up PostgreSQL database"""
    print("=" * 60)
    print("POSTGRESQL SETUP FOR TELECOM CHURN ANALYSIS")
    print("=" * 60)
    
    # Try to load configuration, otherwise use defaults
    try:
        from config import DB_CONFIG
        print("📋 Using configuration from config.py")
        loader = TelecomPostgresLoader(**DB_CONFIG)
    except ImportError:
        print("⚠️  config.py not found, using default settings")
        print("💡 To avoid password prompts, create config.py with your database credentials")
        loader = TelecomPostgresLoader()
    
    try:
        # Step 1: Create database
        if not loader.create_database():
            return
        
        # Step 2: Create connection
        if not loader.create_connection():
            return
        
        # Step 3: Load data
        csv_path = 'data/WA_Fn-UseC_-Telco-Customer-Churn.csv'
        if not os.path.exists(csv_path):
            print(f"❌ CSV file not found: {csv_path}")
            return
        
        if not loader.load_data_from_csv(csv_path):
            return
        
        # Step 4: Create views
        if not loader.create_analysis_views():
            return
        
        # Step 5: Verify setup
        if not loader.verify_setup():
            return
        
        # Step 6: Run sample queries
        if not loader.run_sample_queries():
            return
        
        print("\n" + "=" * 60)
        print("✅ POSTGRESQL SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("1. Run SQL queries from src/queries.sql")
        print("2. Use the database connection in your analysis")
        print("3. Connect Tableau to PostgreSQL for dashboard creation")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
    
    finally:
        loader.close_connection()

if __name__ == "__main__":
    main()
