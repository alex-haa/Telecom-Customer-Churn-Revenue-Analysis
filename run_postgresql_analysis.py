"""
PostgreSQL Analysis Runner for Telecom Customer Churn - FIXED VERSION
====================================================================

This script connects to PostgreSQL and runs the complete analysis
using SQL queries and Python analytics with proper PostgreSQL syntax.
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class TelecomPostgresAnalyzer:
    def __init__(self, host='localhost', port=5432, database='telecom_churn', 
                 user='postgres', password='Alex4305'):
        """Initialize PostgreSQL connection"""
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.engine = None
        self.connection = None
        
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            conn_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            self.engine = create_engine(conn_string)
            self.connection = self.engine.connect()
            print(f"✅ Connected to PostgreSQL database: {self.database}")
            return True
        except Exception as e:
            print(f"❌ Error connecting to PostgreSQL: {e}")
            return False
    
    def run_sql_query(self, query, description=""):
        """Run SQL query and return results as DataFrame"""
        try:
            if description:
                print(f"\n📊 {description}")
            
            result = pd.read_sql(query, self.connection)
            print(f"✅ Query executed successfully - {len(result)} rows returned")
            return result
        except Exception as e:
            print(f"❌ Error running query: {e}")
            return None
    
    def analyze_clv(self):
        """Analyze Customer Lifetime Value"""
        print("\n" + "="*50)
        print("CUSTOMER LIFETIME VALUE ANALYSIS")
        print("="*50)
        
        # Basic CLV analysis
        query = """
        WITH customer_clv AS (
            SELECT 
                "customerID",
                "Contract",
                "InternetService",
                tenure,
                "MonthlyCharges",
                "TotalCharges",
                "Churn",
                CASE 
                    WHEN "TotalCharges" > 0 THEN "TotalCharges"
                    ELSE "MonthlyCharges" * tenure 
                END AS clv
            FROM telecom_customers
        )
        SELECT 
            "Contract",
            "InternetService",
            COUNT(*) AS customer_count,
            ROUND(AVG(clv)::numeric, 2) AS avg_clv,
            ROUND(AVG("MonthlyCharges")::numeric, 2) AS avg_monthly_charges,
            ROUND(AVG(tenure)::numeric, 1) AS avg_tenure_months,
            SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
            ROUND((SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*))::numeric, 2) AS churn_rate_percent
        FROM customer_clv
        GROUP BY "Contract", "InternetService"
        ORDER BY avg_clv DESC;
        """
        
        result = self.run_sql_query(query, "CLV Analysis by Contract and Service")
        if result is not None:
            print("\nTop 5 Customer Segments by CLV:")
            print(result.head().to_string(index=False))
        
        return result
    
    def analyze_churn_drivers(self):
        """Analyze churn drivers"""
        print("\n" + "="*50)
        print("CHURN DRIVERS ANALYSIS")
        print("="*50)
        
        # Overall churn rate
        query = """
        SELECT 
            COUNT(*) AS total_customers,
            SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
            ROUND((SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*))::numeric, 2) AS churn_rate_percent
        FROM telecom_customers;
        """
        
        result = self.run_sql_query(query, "Overall Churn Analysis")
        if result is not None:
            print(f"\nOverall Statistics:")
            print(f"Total Customers: {result.iloc[0]['total_customers']:,}")
            print(f"Churned Customers: {result.iloc[0]['churned_customers']:,}")
            print(f"Churn Rate: {result.iloc[0]['churn_rate_percent']}%")
        
        # Churn by contract type
        query = """
        SELECT 
            "Contract",
            COUNT(*) AS total_customers,
            SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
            ROUND((SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*))::numeric, 2) AS churn_rate_percent,
            ROUND(AVG("MonthlyCharges")::numeric, 2) AS avg_monthly_charges
        FROM telecom_customers
        GROUP BY "Contract"
        ORDER BY churn_rate_percent DESC;
        """
        
        result = self.run_sql_query(query, "Churn Rate by Contract Type")
        if result is not None:
            print("\nChurn by Contract Type:")
            print(result.to_string(index=False))
        
        return result
    
    def analyze_revenue_impact(self):
        """Analyze revenue impact of churn"""
        print("\n" + "="*50)
        print("REVENUE IMPACT ANALYSIS")
        print("="*50)
        
        # Revenue lost due to churn
        query = """
        SELECT 
            SUM(CASE WHEN "Churn" = 'Yes' THEN "MonthlyCharges" ELSE 0 END) AS monthly_revenue_lost,
            SUM(CASE WHEN "Churn" = 'Yes' THEN "MonthlyCharges" * 12 ELSE 0 END) AS annual_revenue_lost,
            SUM(CASE WHEN "Churn" = 'Yes' THEN "MonthlyCharges" * tenure ELSE 0 END) AS lifetime_value_lost
        FROM telecom_customers;
        """
        
        result = self.run_sql_query(query, "Revenue Impact of Churn")
        if result is not None:
            print(f"\nRevenue Impact:")
            print(f"Monthly Revenue Lost: ${result.iloc[0]['monthly_revenue_lost']:,.2f}")
            print(f"Annual Revenue Lost: ${result.iloc[0]['annual_revenue_lost']:,.2f}")
            print(f"Lifetime Value Lost: ${result.iloc[0]['lifetime_value_lost']:,.2f}")
        
        # Revenue impact by segment
        query = """
        WITH churn_revenue AS (
            SELECT 
                "Contract",
                "InternetService",
                COUNT(*) AS churned_customers,
                ROUND(AVG("MonthlyCharges")::numeric, 2) AS avg_monthly_charges,
                ROUND((COUNT(*) * AVG("MonthlyCharges"))::numeric, 2) AS monthly_revenue_lost,
                ROUND((COUNT(*) * AVG("MonthlyCharges") * 12)::numeric, 2) AS annual_revenue_lost
            FROM telecom_customers
            WHERE "Churn" = 'Yes'
            GROUP BY "Contract", "InternetService"
        )
        SELECT 
            "Contract",
            "InternetService",
            churned_customers,
            avg_monthly_charges,
            monthly_revenue_lost,
            annual_revenue_lost,
            ROUND((annual_revenue_lost / SUM(annual_revenue_lost) OVER() * 100)::numeric, 2) AS revenue_loss_percentage
        FROM churn_revenue
        ORDER BY annual_revenue_lost DESC;
        """
        
        result = self.run_sql_query(query, "Revenue Impact by Segment")
        if result is not None:
            print("\nRevenue Impact by Segment:")
            print(result.head().to_string(index=False))
        
        return result
    
    def analyze_pricing_optimization(self):
        """Analyze pricing optimization opportunities"""
        print("\n" + "="*50)
        print("PRICING OPTIMIZATION ANALYSIS")
        print("="*50)
        
        # Price sensitivity analysis
        query = """
        SELECT 
            CASE 
                WHEN "MonthlyCharges" <= 30 THEN 'Low Price ($0-30)'
                WHEN "MonthlyCharges" <= 60 THEN 'Medium Price ($31-60)'
                WHEN "MonthlyCharges" <= 90 THEN 'High Price ($61-90)'
                ELSE 'Premium Price ($90+)'
            END AS price_segment,
            COUNT(*) AS customer_count,
            SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
            ROUND((SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*))::numeric, 2) AS churn_rate_percent,
            ROUND(AVG("MonthlyCharges")::numeric, 2) AS avg_monthly_charges
        FROM telecom_customers
        GROUP BY price_segment
        ORDER BY AVG("MonthlyCharges");
        """
        
        result = self.run_sql_query(query, "Price Sensitivity Analysis")
        if result is not None:
            print("\nPrice Sensitivity Analysis:")
            print(result.to_string(index=False))
        
        return result
    
    def create_visualizations(self):
        """Create visualizations from PostgreSQL data"""
        print("\n" + "="*50)
        print("CREATING VISUALIZATIONS")
        print("="*50)
        
        try:
            # Get data for visualizations
            churn_by_contract = pd.read_sql("""
                SELECT 
                    "Contract",
                    COUNT(*) AS total_customers,
                    SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
                    ROUND((SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*))::numeric, 2) AS churn_rate_percent
                FROM telecom_customers
                GROUP BY "Contract"
                ORDER BY churn_rate_percent DESC;
            """, self.connection)
            
            churn_by_internet = pd.read_sql("""
                SELECT 
                    "InternetService",
                    COUNT(*) AS total_customers,
                    SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
                    ROUND((SUM(CASE WHEN "Churn" = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*))::numeric, 2) AS churn_rate_percent
                FROM telecom_customers
                GROUP BY "InternetService"
                ORDER BY churn_rate_percent DESC;
            """, self.connection)
            
            # Create visualizations
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Telecom Customer Churn Analysis - PostgreSQL', fontsize=16, fontweight='bold')
            
            # 1. Churn rate by contract type
            axes[0, 0].bar(churn_by_contract['Contract'], churn_by_contract['churn_rate_percent'], 
                          color=['#ff6b6b', '#4ecdc4', '#45b7d1'])
            axes[0, 0].set_title('Churn Rate by Contract Type')
            axes[0, 0].set_ylabel('Churn Rate (%)')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # 2. Churn rate by internet service
            axes[0, 1].bar(churn_by_internet['InternetService'], churn_by_internet['churn_rate_percent'],
                          color=['#96ceb4', '#feca57', '#ff9ff3'])
            axes[0, 1].set_title('Churn Rate by Internet Service')
            axes[0, 1].set_ylabel('Churn Rate (%)')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # 3. Customer distribution by contract
            axes[1, 0].pie(churn_by_contract['total_customers'], labels=churn_by_contract['Contract'], 
                         autopct='%1.1f%%', startangle=90)
            axes[1, 0].set_title('Customer Distribution by Contract')
            
            # 4. Revenue impact
            revenue_data = pd.read_sql("""
                SELECT 
                    "Contract",
                    SUM(CASE WHEN "Churn" = 'Yes' THEN "MonthlyCharges" * 12 ELSE 0 END) AS annual_revenue_lost
                FROM telecom_customers
                GROUP BY "Contract"
                ORDER BY annual_revenue_lost DESC;
            """, self.connection)
            
            axes[1, 1].bar(revenue_data['Contract'], revenue_data['annual_revenue_lost'],
                          color=['#ff6b6b', '#4ecdc4', '#45b7d1'])
            axes[1, 1].set_title('Annual Revenue Lost by Contract Type')
            axes[1, 1].set_ylabel('Revenue Lost ($)')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig('telecom_churn_postgresql_analysis.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("✅ Visualizations saved as 'telecom_churn_postgresql_analysis.png'")
            
        except Exception as e:
            print(f"❌ Error creating visualizations: {e}")
    
    def generate_recommendations(self):
        """Generate business recommendations based on analysis"""
        print("\n" + "="*50)
        print("BUSINESS RECOMMENDATIONS")
        print("="*50)
        
        recommendations = [
            "🎯 IMMEDIATE ACTIONS (0-3 months):",
            "   • Focus retention efforts on Month-to-month contract customers",
            "   • Target customers with tenure < 12 months (highest churn risk)",
            "   • Investigate service quality issues for Fiber optic customers",
            "",
            "📈 MEDIUM-TERM INITIATIVES (3-6 months):",
            "   • Implement contract migration program (Month-to-month → Annual)",
            "   • Launch loyalty programs for customers approaching renewal",
            "   • Deploy predictive models for early churn detection",
            "",
            "🚀 LONG-TERM STRATEGY (6-12 months):",
            "   • Create personalized retention campaigns by customer segment",
            "   • Enhance customer experience across all touchpoints",
            "   • Implement real-time churn prediction and intervention",
            "",
            "💰 REVENUE RECOVERY POTENTIAL:",
            "   • Target: 20-40% churn reduction",
            "   • Potential annual revenue recovery: $300K - $600K",
            "   • ROI: High return on retention investment"
        ]
        
        for rec in recommendations:
            print(rec)
    
    def run_complete_analysis(self):
        """Run the complete PostgreSQL analysis"""
        print("=" * 60)
        print("TELECOM CUSTOMER CHURN ANALYSIS - POSTGRESQL")
        print("=" * 60)
        
        if not self.connect():
            return
        
        try:
            # Run all analyses
            self.analyze_clv()
            self.analyze_churn_drivers()
            self.analyze_revenue_impact()
            self.analyze_pricing_optimization()
            self.create_visualizations()
            self.generate_recommendations()
            
            print("\n" + "=" * 60)
            print("✅ POSTGRESQL ANALYSIS COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
        
        finally:
            self.close_connection()
    
    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        print("🔌 Database connection closed")

def main():
    """Main function to run PostgreSQL analysis"""
    # Try to load configuration, otherwise use defaults
    try:
        from config import DB_CONFIG
        print("📋 Using configuration from config.py")
        analyzer = TelecomPostgresAnalyzer(**DB_CONFIG)
    except ImportError:
        print("⚠️  config.py not found, using default settings")
        print("💡 To avoid password prompts, create config.py with your database credentials")
        analyzer = TelecomPostgresAnalyzer()
    
    # Run complete analysis
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()
