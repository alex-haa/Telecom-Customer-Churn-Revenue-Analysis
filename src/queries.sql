-- =====================================================
-- 1. CUSTOMER LIFETIME VALUE (CLV) CALCULATION
-- =====================================================

-- Basic CLV calculation using average monthly charges and tenure
WITH customer_clv AS (
    SELECT 
        customerID,
        gender,
        SeniorCitizen,
        Partner,
        Dependents,
        tenure,
        MonthlyCharges,
        TotalCharges,
        Contract,
        InternetService,
        Churn,
        -- Calculate CLV as monthly charges * tenure (simplified)
        MonthlyCharges * tenure AS calculated_clv,
        -- Alternative CLV: Total charges if available, otherwise calculated
        CASE 
            WHEN TotalCharges IS NOT NULL AND TotalCharges != '' 
            THEN CAST(TotalCharges AS FLOAT)
            ELSE MonthlyCharges * tenure 
        END AS clv,
        -- Churn risk score based on tenure and contract
        CASE 
            WHEN Contract = 'Month-to-month' AND tenure < 12 THEN 'High Risk'
            WHEN Contract = 'Month-to-month' AND tenure < 24 THEN 'Medium Risk'
            WHEN Contract = 'One year' AND tenure < 6 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS churn_risk
    FROM telecom_customers
)
SELECT 
    'CLV Analysis' AS analysis_type,
    COUNT(*) AS total_customers,
    ROUND(AVG(clv), 2) AS avg_clv,
    ROUND(MIN(clv), 2) AS min_clv,
    ROUND(MAX(clv), 2) AS max_clv,
    ROUND(STDDEV(clv), 2) AS clv_std_dev
FROM customer_clv;

-- CLV by customer segments
WITH customer_clv AS (
    SELECT 
        customerID,
        gender,
        SeniorCitizen,
        Partner,
        Dependents,
        tenure,
        MonthlyCharges,
        Contract,
        InternetService,
        Churn,
        CASE 
            WHEN TotalCharges IS NOT NULL AND TotalCharges != '' 
            THEN CAST(TotalCharges AS FLOAT)
            ELSE MonthlyCharges * tenure 
        END AS clv
    FROM telecom_customers
)
SELECT 
    Contract,
    InternetService,
    CASE 
        WHEN SeniorCitizen = 1 THEN 'Senior'
        ELSE 'Non-Senior'
    END AS age_group,
    CASE 
        WHEN Partner = 'Yes' AND Dependents = 'Yes' THEN 'Family'
        WHEN Partner = 'Yes' OR Dependents = 'Yes' THEN 'Couple/Single Parent'
        ELSE 'Single'
    END AS household_type,
    COUNT(*) AS customer_count,
    ROUND(AVG(clv), 2) AS avg_clv,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    ROUND(AVG(tenure), 1) AS avg_tenure_months,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_percent
FROM customer_clv
GROUP BY Contract, InternetService, age_group, household_type
ORDER BY avg_clv DESC;

-- =====================================================
-- 2. CHURN DRIVERS ANALYSIS
-- =====================================================

-- Overall churn rate and key drivers
SELECT 
    'Overall Churn Analysis' AS analysis_type,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_percent
FROM telecom_customers;

-- Churn rate by contract type
SELECT 
    Contract,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_percent,
    ROUND(AVG(tenure), 1) AS avg_tenure_months,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges
FROM telecom_customers
GROUP BY Contract
ORDER BY churn_rate_percent DESC;

-- Churn rate by internet service type
SELECT 
    InternetService,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_percent,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges
FROM telecom_customers
GROUP BY InternetService
ORDER BY churn_rate_percent DESC;

-- Churn rate by tenure segments
SELECT 
    CASE 
        WHEN tenure <= 12 THEN '0-12 months'
        WHEN tenure <= 24 THEN '13-24 months'
        WHEN tenure <= 36 THEN '25-36 months'
        WHEN tenure <= 48 THEN '37-48 months'
        WHEN tenure <= 60 THEN '49-60 months'
        ELSE '60+ months'
    END AS tenure_segment,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_percent,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges
FROM telecom_customers
GROUP BY tenure_segment
ORDER BY 
    CASE 
        WHEN tenure_segment = '0-12 months' THEN 1
        WHEN tenure_segment = '13-24 months' THEN 2
        WHEN tenure_segment = '25-36 months' THEN 3
        WHEN tenure_segment = '37-48 months' THEN 4
        WHEN tenure_segment = '49-60 months' THEN 5
        ELSE 6
    END;

-- Churn rate by payment method
SELECT 
    PaymentMethod,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_percent,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges
FROM telecom_customers
GROUP BY PaymentMethod
ORDER BY churn_rate_percent DESC;

-- High-risk customer identification
SELECT 
    customerID,
    Contract,
    InternetService,
    tenure,
    MonthlyCharges,
    CASE 
        WHEN TotalCharges IS NOT NULL AND TotalCharges != '' 
        THEN CAST(TotalCharges AS FLOAT)
        ELSE MonthlyCharges * tenure 
    END AS clv,
    CASE 
        WHEN Contract = 'Month-to-month' AND tenure < 12 THEN 'High Risk'
        WHEN Contract = 'Month-to-month' AND tenure < 24 THEN 'Medium Risk'
        WHEN Contract = 'One year' AND tenure < 6 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS churn_risk,
    Churn
FROM telecom_customers
WHERE Churn = 'No'  -- Focus on current customers
ORDER BY 
    CASE 
        WHEN Contract = 'Month-to-month' AND tenure < 12 THEN 1
        WHEN Contract = 'Month-to-month' AND tenure < 24 THEN 2
        WHEN Contract = 'One year' AND tenure < 6 THEN 3
        ELSE 4
    END,
    MonthlyCharges DESC;

-- =====================================================
-- 3. PRICING PLAN PROFITABILITY ANALYSIS
-- =====================================================

-- Revenue analysis by service combinations
SELECT 
    PhoneService,
    InternetService,
    CASE 
        WHEN StreamingTV = 'Yes' AND StreamingMovies = 'Yes' THEN 'Both Streaming'
        WHEN StreamingTV = 'Yes' OR StreamingMovies = 'Yes' THEN 'One Streaming'
        ELSE 'No Streaming'
    END AS streaming_services,
    COUNT(*) AS customer_count,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_revenue,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_percent,
    ROUND(AVG(tenure), 1) AS avg_tenure_months
FROM telecom_customers
GROUP BY PhoneService, InternetService, streaming_services
ORDER BY total_monthly_revenue DESC;

-- Contract profitability analysis
SELECT 
    Contract,
    COUNT(*) AS customer_count,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_revenue,
    ROUND(AVG(tenure), 1) AS avg_tenure_months,
    ROUND(AVG(MonthlyCharges) * AVG(tenure), 2) AS estimated_lifetime_value,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_percent
FROM telecom_customers
GROUP BY Contract
ORDER BY estimated_lifetime_value DESC;

-- Add-on services profitability
SELECT 
    OnlineSecurity,
    OnlineBackup,
    DeviceProtection,
    TechSupport,
    StreamingTV,
    StreamingMovies,
    COUNT(*) AS customer_count,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_percent
FROM telecom_customers
WHERE InternetService != 'No'  -- Only customers with internet service
GROUP BY OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies
HAVING COUNT(*) >= 10  -- Only show combinations with at least 10 customers
ORDER BY avg_monthly_charges DESC;

-- =====================================================
-- 4. REVENUE IMPACT ANALYSIS
-- =====================================================

-- Revenue lost due to churn
WITH churn_revenue_impact AS (
    SELECT 
        Contract,
        InternetService,
        COUNT(*) AS churned_customers,
        ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
        ROUND(AVG(tenure), 1) AS avg_tenure_at_churn,
        ROUND(COUNT(*) * AVG(MonthlyCharges), 2) AS monthly_revenue_lost,
        ROUND(COUNT(*) * AVG(MonthlyCharges) * 12, 2) AS annual_revenue_lost
    FROM telecom_customers
    WHERE Churn = 'Yes'
    GROUP BY Contract, InternetService
)
SELECT 
    Contract,
    InternetService,
    churned_customers,
    avg_monthly_charges,
    avg_tenure_at_churn,
    monthly_revenue_lost,
    annual_revenue_lost,
    ROUND(annual_revenue_lost / SUM(annual_revenue_lost) OVER() * 100, 2) AS revenue_loss_percentage
FROM churn_revenue_impact
ORDER BY annual_revenue_lost DESC;

-- Customer acquisition cost vs lifetime value by segment
SELECT 
    CASE 
        WHEN SeniorCitizen = 1 THEN 'Senior'
        ELSE 'Non-Senior'
    END AS age_group,
    CASE 
        WHEN Partner = 'Yes' AND Dependents = 'Yes' THEN 'Family'
        WHEN Partner = 'Yes' OR Dependents = 'Yes' THEN 'Couple/Single Parent'
        ELSE 'Single'
    END AS household_type,
    Contract,
    COUNT(*) AS customer_count,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    ROUND(AVG(tenure), 1) AS avg_tenure_months,
    ROUND(AVG(MonthlyCharges) * AVG(tenure), 2) AS avg_lifetime_value,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_percent
FROM telecom_customers
GROUP BY age_group, household_type, Contract
ORDER BY avg_lifetime_value DESC;

-- =====================================================
-- 5. PRICING OPTIMIZATION RECOMMENDATIONS
-- =====================================================

-- Price sensitivity analysis
SELECT 
    CASE 
        WHEN MonthlyCharges <= 30 THEN 'Low Price ($0-30)'
        WHEN MonthlyCharges <= 60 THEN 'Medium Price ($31-60)'
        WHEN MonthlyCharges <= 90 THEN 'High Price ($61-90)'
        ELSE 'Premium Price ($90+)'
    END AS price_segment,
    COUNT(*) AS customer_count,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_percent,
    ROUND(AVG(tenure), 1) AS avg_tenure_months,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges
FROM telecom_customers
GROUP BY price_segment
ORDER BY 
    CASE 
        WHEN price_segment = 'Low Price ($0-30)' THEN 1
        WHEN price_segment = 'Medium Price ($31-60)' THEN 2
        WHEN price_segment = 'High Price ($61-90)' THEN 3
        ELSE 4
    END;

-- Optimal pricing recommendations by service type
SELECT 
    InternetService,
    Contract,
    COUNT(*) AS customer_count,
    ROUND(AVG(MonthlyCharges), 2) AS current_avg_price,
    ROUND(AVG(tenure), 1) AS avg_tenure_months,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_percent,
    -- Recommendation logic
    CASE 
        WHEN AVG(MonthlyCharges) > 80 AND SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) > 30 
        THEN 'Consider Price Reduction'
        WHEN AVG(MonthlyCharges) < 50 AND SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) < 20 
        THEN 'Consider Price Increase'
        ELSE 'Maintain Current Pricing'
    END AS pricing_recommendation
FROM telecom_customers
GROUP BY InternetService, Contract
ORDER BY churn_rate_percent DESC;