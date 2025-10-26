# Telecom Customer Churn & Revenue Analysis

## Project Overview

This project provides a comprehensive analysis of telecom customer churn patterns and revenue impact using SQL, Python, and Tableau. The analysis identifies key churn drivers, calculates customer lifetime value (CLV), and provides actionable recommendations for reducing churn and optimizing revenue.

## 📊 Key Findings

### Overall Metrics
- **Total Customers**: 7,043
- **Overall Churn Rate**: 26.54%
- **Monthly Revenue Lost**: $139,130.85
- **Annual Revenue Lost**: $1,669,570.20
- **Estimated Lifetime Value Lost**: $2,862,576.90

### Critical Insights
1. **Month-to-month contracts** have the highest churn rate (42.7%)
2. **Fiber optic customers** show highest churn (41.9%)
3. **New customers** (0-12 months tenure) have 47.7% churn rate
4. **High-risk segment** (New Month-to-Month) represents 51.94% churn rate

## 🎯 Customer Segmentation Analysis

| Customer Segment | Count | Churn Rate | Avg Monthly Charges | Avg Tenure |
|------------------|-------|------------|-------------------|------------|
| High Risk - New Month-to-Month | 1,908 | 51.94% | $74.41 | 8.2 months |
| Medium Risk - Established Month-to-Month | 1,967 | 33.76% | $73.89 | 25.1 months |
| Medium Risk - New Annual | 32 | 12.50% | $64.38 | 3.8 months |
| Stable - Established Annual | 1,441 | 11.24% | $61.27 | 45.2 months |
| Low Risk - Long-term | 1,695 | 2.83% | $60.12 | 55.8 months |

## 🔍 Predictive Modeling Results

### Model Performance
- **Random Forest AUC**: 0.823
- **Logistic Regression AUC**: 0.841

### Top Predictive Features
1. Total Charges (18.7% importance)
2. Monthly Charges (17.7% importance)
3. Tenure (16.0% importance)
4. Contract Type (7.7% importance)
5. Payment Method (5.2% importance)

## 💰 Revenue Impact Analysis

### Revenue Lost by Segment
- **High Risk - New Month-to-Month**: $788,067.60 annually
- **Medium Risk - Established Month-to-Month**: $662,097.60 annually
- **Stable - Established Annual**: $166,843.80 annually
- **Low Risk - Long-term**: $49,983.60 annually
- **Medium Risk - New Annual**: $2,577.60 annually

## 📈 Strategic Recommendations

### Immediate Actions (0-3 months)
1. **Target High-Risk Customers**: Focus retention efforts on Month-to-month customers with tenure < 12 months
2. **Implement Early Warning System**: Deploy predictive models to identify at-risk customers
3. **Service Quality Investigation**: Investigate Fiber optic service issues causing high churn

### Medium-term Initiatives (3-6 months)
1. **Contract Migration Program**: Offer incentives for Month-to-month customers to switch to annual contracts
2. **Loyalty Programs**: Implement retention programs for customers approaching contract renewal
3. **Pricing Optimization**: Adjust pricing for services with high churn rates

### Long-term Strategy (6-12 months)
1. **Personalized Retention**: Create targeted campaigns based on customer segments
2. **Service Improvement**: Address root causes of Fiber optic service dissatisfaction
3. **Customer Experience Enhancement**: Improve overall customer experience to reduce churn

## 🚀 **How to Run the Project**

### **Option 1: PostgreSQL Setup (Recommended)**

#### **Prerequisites**
1. **Install PostgreSQL**: Download from https://www.postgresql.org/download/windows/
2. **Remember the password** you set for the `postgres` user

#### **Quick Start (3 Steps)**
```bash
# Step 1: Install Python dependencies
cd "c:\Users\jluon\data vis\Telecom-Customer-Churn-Revenue-Analysis"
pip install -r requirements.txt

# Step 2: Set up PostgreSQL database and load data
python setup_postgresql.py

# Step 3: Run the complete analysis
python run_postgresql_analysis.py
```

#### **What You'll Get**
- ✅ PostgreSQL database `telecom_churn` with 7,043 customer records
- ✅ Comprehensive SQL analysis with CLV, churn drivers, revenue impact
- ✅ Automated visualizations (`telecom_churn_postgresql_analysis.png`)
- ✅ Business insights and strategic recommendations
- ✅ Database ready for Tableau connection

#### **Expected Output**
```
============================================================
POSTGRESQL SETUP FOR TELECOM CHURN ANALYSIS
============================================================
✅ Created database: telecom_churn
✅ Successfully loaded 7043 records into telecom_customers table
✅ Analysis views created successfully
✅ Database verification: 26.54% churn rate

============================================================
TELECOM CUSTOMER CHURN ANALYSIS - POSTGRESQL
============================================================
✅ Connected to PostgreSQL database: telecom_churn
📊 CLV Analysis by Contract and Service
💰 Revenue Impact: $1,669,570.20 annual revenue lost
🎯 Strategic Recommendations provided
✅ POSTGRESQL ANALYSIS COMPLETED SUCCESSFULLY!
```

### **Option 2: Python-Only Analysis**

#### **Quick Start**
```bash
# Install dependencies
pip install pandas numpy matplotlib seaborn scikit-learn

# Run Python analysis
python src/advanced_analysis.py
```

#### **What You'll Get**
- ✅ Cohort analysis and customer segmentation
- ✅ Predictive modeling (Random Forest & Logistic Regression)
- ✅ Revenue impact analysis
- ✅ Visualizations (`telecom_churn_analysis.png`)
- ✅ Business insights and recommendations

### **Option 3: SQL Queries Only**

#### **For PostgreSQL**
```bash
# Connect to PostgreSQL
psql -U postgres -d telecom_churn

# Run queries
\i src/queries_postgresql.sql
```

#### **For Other SQL Databases**
```bash
# Run queries from src/queries.sql
# Compatible with MySQL, SQL Server, Oracle, etc.
```

## 🛠️ Technical Implementation

### Files Structure
```
Telecom-Customer-Churn-Revenue-Analysis/
├── data/
│   └── WA_Fn-UseC_-Telco-Customer-Churn.csv
├── src/
│   ├── queries.sql                    # SQL analysis queries
│   ├── queries_postgresql.sql         # PostgreSQL-specific queries
│   ├── advanced_analysis.py           # Python analytics & ML models
│   └── analyze_data.py                # Data exploration script
├── setup_postgresql.py                # PostgreSQL database setup
├── run_postgresql_analysis.py         # PostgreSQL analysis runner
├── requirements.txt                   # Python dependencies
├── tab/
│   └── dashboard.twbx                 # Tableau dashboard
├── telecom_churn_analysis.png         # Python-generated visualizations
├── telecom_churn_postgresql_analysis.png # PostgreSQL-generated visualizations
└── README.md                          # This documentation
```

### SQL Queries (`src/queries.sql`)
- Customer Lifetime Value (CLV) calculations
- Churn drivers analysis by demographics and services
- Pricing plan profitability analysis
- Revenue impact calculations
- Pricing optimization recommendations

### Python Analysis (`src/advanced_analysis.py`)
- Cohort analysis for retention patterns
- Customer segmentation based on risk levels
- Predictive modeling with Random Forest and Logistic Regression
- Revenue impact analysis by segments
- Automated visualization generation

## 📊 Tableau Dashboard Design

### Dashboard Sections
1. **Executive Summary**
   - Overall churn rate and revenue impact
   - Key performance indicators (KPIs)

2. **Churn Analysis**
   - Churn rate by contract type, internet service, tenure
   - Customer segment analysis
   - Geographic distribution (if available)

3. **Revenue Impact**
   - Monthly/annual revenue lost due to churn
   - Revenue impact by customer segments
   - Customer lifetime value analysis

4. **Predictive Insights**
   - At-risk customer identification
   - Churn probability scores
   - Retention opportunity analysis

5. **Recommendations**
   - Actionable insights and next steps
   - ROI projections for retention initiatives

## 🔧 Technical Requirements

### Software Dependencies
- **Python**: pandas, numpy, matplotlib, seaborn, scikit-learn
- **SQL**: Compatible with most SQL databases
- **Tableau**: Desktop or Server for dashboard creation

### Data Requirements
- Customer demographic information
- Service usage and billing data
- Contract and tenure information
- Churn status (historical and current)

## 📊 **Tableau Integration**

### **Connect Tableau to PostgreSQL**
1. Open Tableau Desktop
2. Connect → PostgreSQL
3. Server: `localhost`
4. Port: `5432`
5. Database: `telecom_churn`
6. Username: `postgres`
7. Password: `your_password`

### **Available Tables & Views**
- `telecom_customers` - Main customer data
- `customer_segments` - Customer segmentation view
- `churn_summary` - Churn analysis summary

### **Custom Analysis**
```python
# Example: Run custom queries
from run_postgresql_analysis import TelecomPostgresAnalyzer

analyzer = TelecomPostgresAnalyzer()
analyzer.connect()

custom_query = """
SELECT Contract, AVG(MonthlyCharges) as avg_charges
FROM telecom_customers
WHERE Churn = 'No'
GROUP BY Contract;
"""

result = analyzer.run_sql_query(custom_query, "Custom Analysis")
print(result)
```

### **Export Results**
```python
# Export to CSV
result.to_csv('analysis_results.csv', index=False)

# Export to Excel
result.to_excel('analysis_results.xlsx', index=False)
```

**Analysis Completed**: January 2025  
**Data Source**: Telco Customer Churn Dataset (Kaggle)  
**Methodology**: SQL Analytics + Python ML + Tableau Visualization + PostgreSQL Integration