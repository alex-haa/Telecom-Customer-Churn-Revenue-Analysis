import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class TelecomChurnAnalyzer:
    def __init__(self, data_path):
        """Initialize the analyzer with data path"""
        self.data_path = data_path
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Load and preprocess the telecom data"""
        print("Loading telecom customer data...")
        self.df = pd.read_csv(self.data_path)
        
        # Clean TotalCharges column (convert to numeric)
        self.df['TotalCharges'] = pd.to_numeric(self.df['TotalCharges'], errors='coerce')
        
        # Fill missing values in TotalCharges with 0 (new customers)
        self.df['TotalCharges'].fillna(0, inplace=True)
        
        print(f"Data loaded successfully: {self.df.shape[0]} customers, {self.df.shape[1]} features")
        
    def cohort_analysis(self):
        """Perform cohort analysis to understand customer retention patterns"""
        print("\n=== COHORT ANALYSIS ===")
        
        # Create cohorts based on contract start (simulated using tenure)
        # Assuming customers start at different times, we'll use tenure as a proxy
        self.df['cohort_month'] = self.df['tenure'].apply(lambda x: max(0, 72 - x))  # Simulate start month
        
        # Create cohort groups
        self.df['cohort_group'] = pd.cut(self.df['cohort_month'], 
                                       bins=[0, 12, 24, 36, 48, 60, 72], 
                                       labels=['0-12', '13-24', '25-36', '37-48', '49-60', '60+'])
        
        # Calculate retention rates by cohort
        cohort_analysis = self.df.groupby(['cohort_group', 'tenure']).agg({
            'customerID': 'count',
            'Churn': lambda x: (x == 'Yes').sum()
        }).reset_index()
        
        cohort_analysis.columns = ['cohort_group', 'tenure', 'total_customers', 'churned_customers']
        cohort_analysis['retention_rate'] = 1 - (cohort_analysis['churned_customers'] / cohort_analysis['total_customers'])
        
        print("Cohort Retention Analysis:")
        print(cohort_analysis.pivot(index='cohort_group', columns='tenure', values='retention_rate').fillna(0))
        
        return cohort_analysis
    
    def customer_segmentation(self):
        """Perform customer segmentation based on behavior and demographics"""
        print("\n=== CUSTOMER SEGMENTATION ===")
        
        # Create customer segments
        def create_segments(row):
            if row['Contract'] == 'Month-to-month' and row['tenure'] < 12:
                return 'High Risk - New Month-to-Month'
            elif row['Contract'] == 'Month-to-month' and row['tenure'] >= 12:
                return 'Medium Risk - Established Month-to-Month'
            elif row['Contract'] == 'One year' and row['tenure'] < 6:
                return 'Medium Risk - New Annual'
            elif row['Contract'] == 'Two year':
                return 'Low Risk - Long-term'
            else:
                return 'Stable - Established Annual'
        
        self.df['customer_segment'] = self.df.apply(create_segments, axis=1)
        
        # Analyze segments
        segment_analysis = self.df.groupby('customer_segment').agg({
            'customerID': 'count',
            'MonthlyCharges': 'mean',
            'tenure': 'mean',
            'TotalCharges': 'mean',
            'Churn': lambda x: (x == 'Yes').sum()
        }).round(2)
        
        segment_analysis['churn_rate'] = (segment_analysis['Churn'] / segment_analysis['customerID'] * 100).round(2)
        segment_analysis.columns = ['customer_count', 'avg_monthly_charges', 'avg_tenure', 
                                  'avg_total_charges', 'churned_customers', 'churn_rate']
        
        print("Customer Segment Analysis:")
        print(segment_analysis.sort_values('churn_rate', ascending=False))
        
        return segment_analysis
    
    def predictive_modeling(self):
        """Build predictive models for churn prediction"""
        print("\n=== PREDICTIVE MODELING ===")
        
        # Prepare features for modeling
        df_model = self.df.copy()
        
        # Encode categorical variables
        categorical_cols = ['gender', 'Partner', 'Dependents', 'PhoneService', 'MultipleLines',
                           'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
                           'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract',
                           'PaperlessBilling', 'PaymentMethod']
        
        le_dict = {}
        for col in categorical_cols:
            le = LabelEncoder()
            df_model[col + '_encoded'] = le.fit_transform(df_model[col])
            le_dict[col] = le
        
        # Select features for modeling
        feature_cols = ['SeniorCitizen', 'tenure', 'MonthlyCharges', 'TotalCharges'] + \
                      [col + '_encoded' for col in categorical_cols]
        
        X = df_model[feature_cols]
        y = df_model['Churn'].map({'Yes': 1, 'No': 0})
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Train Random Forest model
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        
        # Train Logistic Regression model
        lr_model = LogisticRegression(random_state=42, max_iter=1000)
        lr_model.fit(X_train, y_train)
        
        # Evaluate models
        models = {'Random Forest': rf_model, 'Logistic Regression': lr_model}
        
        print("Model Performance:")
        for name, model in models.items():
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            auc_score = roc_auc_score(y_test, y_pred_proba)
            print(f"\n{name}:")
            print(f"AUC Score: {auc_score:.3f}")
            print(classification_report(y_test, y_pred))
        
        # Feature importance (Random Forest)
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Most Important Features:")
        print(feature_importance.head(10))
        
        return models, feature_importance
    
    def revenue_impact_analysis(self):
        """Analyze revenue impact of churn"""
        print("\n=== REVENUE IMPACT ANALYSIS ===")
        
        # Calculate revenue lost due to churn
        churned_customers = self.df[self.df['Churn'] == 'Yes']
        
        # Monthly revenue lost
        monthly_revenue_lost = churned_customers['MonthlyCharges'].sum()
        
        # Annual revenue lost
        annual_revenue_lost = monthly_revenue_lost * 12
        
        # Lifetime value lost (simplified calculation)
        churned_customers['estimated_lifetime_value'] = churned_customers['MonthlyCharges'] * churned_customers['tenure']
        lifetime_value_lost = churned_customers['estimated_lifetime_value'].sum()
        
        print(f"Monthly Revenue Lost: ${monthly_revenue_lost:,.2f}")
        print(f"Annual Revenue Lost: ${annual_revenue_lost:,.2f}")
        print(f"Estimated Lifetime Value Lost: ${lifetime_value_lost:,.2f}")
        
        # Revenue impact by segment
        revenue_by_segment = churned_customers.groupby('customer_segment').agg({
            'customerID': 'count',
            'MonthlyCharges': 'sum',
            'estimated_lifetime_value': 'sum'
        }).round(2)
        
        revenue_by_segment.columns = ['churned_customers', 'monthly_revenue_lost', 'lifetime_value_lost']
        revenue_by_segment['annual_revenue_lost'] = revenue_by_segment['monthly_revenue_lost'] * 12
        
        print("\nRevenue Impact by Customer Segment:")
        print(revenue_by_segment.sort_values('annual_revenue_lost', ascending=False))
        
        return revenue_by_segment
    
    def generate_insights_and_recommendations(self):
        """Generate business insights and recommendations"""
        print("\n=== BUSINESS INSIGHTS & RECOMMENDATIONS ===")
        
        # Overall churn rate
        overall_churn_rate = (self.df['Churn'] == 'Yes').sum() / len(self.df) * 100
        
        print(f"Overall Churn Rate: {overall_churn_rate:.2f}%")
        
        # Key insights
        insights = []
        
        # Contract type insight
        contract_churn = self.df.groupby('Contract')['Churn'].apply(lambda x: (x == 'Yes').sum() / len(x) * 100)
        highest_churn_contract = contract_churn.idxmax()
        insights.append(f"Highest churn rate is among {highest_churn_contract} customers ({contract_churn[highest_churn_contract]:.1f}%)")
        
        # Internet service insight
        internet_churn = self.df.groupby('InternetService')['Churn'].apply(lambda x: (x == 'Yes').sum() / len(x) * 100)
        highest_churn_internet = internet_churn.idxmax()
        insights.append(f"Highest churn rate is among {highest_churn_internet} customers ({internet_churn[highest_churn_internet]:.1f}%)")
        
        # Tenure insight
        tenure_churn = self.df.groupby(pd.cut(self.df['tenure'], bins=[0, 12, 24, 36, 72]))['Churn'].apply(lambda x: (x == 'Yes').sum() / len(x) * 100)
        highest_churn_tenure = tenure_churn.idxmax()
        insights.append(f"Highest churn rate is among customers with tenure {highest_churn_tenure} ({tenure_churn[highest_churn_tenure]:.1f}%)")
        
        print("\nKey Insights:")
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
        
        # Recommendations
        recommendations = [
            "Focus retention efforts on Month-to-month contract customers, especially those with tenure < 12 months",
            "Implement loyalty programs for customers approaching contract renewal",
            "Offer incentives for customers to switch from Month-to-month to annual contracts",
            "Investigate service quality issues for Fiber optic customers",
            "Develop targeted retention campaigns for high-value customers at risk of churning",
            "Consider pricing adjustments for services with high churn rates",
            "Implement early warning systems to identify at-risk customers",
            "Create personalized retention offers based on customer segment and usage patterns"
        ]
        
        print("\nStrategic Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        return insights, recommendations
    
    def create_visualizations(self):
        """Create key visualizations for the analysis"""
        print("\n=== CREATING VISUALIZATIONS ===")
        
        # Set up the plotting area
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Telecom Customer Churn Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Churn rate by contract type
        contract_churn = self.df.groupby('Contract')['Churn'].apply(lambda x: (x == 'Yes').sum() / len(x) * 100)
        axes[0, 0].bar(contract_churn.index, contract_churn.values, color=['#ff6b6b', '#4ecdc4', '#45b7d1'])
        axes[0, 0].set_title('Churn Rate by Contract Type')
        axes[0, 0].set_ylabel('Churn Rate (%)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Churn rate by internet service
        internet_churn = self.df.groupby('InternetService')['Churn'].apply(lambda x: (x == 'Yes').sum() / len(x) * 100)
        axes[0, 1].bar(internet_churn.index, internet_churn.values, color=['#96ceb4', '#feca57', '#ff9ff3'])
        axes[0, 1].set_title('Churn Rate by Internet Service')
        axes[0, 1].set_ylabel('Churn Rate (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Monthly charges distribution by churn status
        sns.boxplot(data=self.df, x='Churn', y='MonthlyCharges', ax=axes[0, 2])
        axes[0, 2].set_title('Monthly Charges Distribution by Churn Status')
        
        # 4. Tenure distribution by churn status
        sns.boxplot(data=self.df, x='Churn', y='tenure', ax=axes[1, 0])
        axes[1, 0].set_title('Tenure Distribution by Churn Status')
        
        # 5. Customer segment analysis
        if 'customer_segment' in self.df.columns:
            segment_churn = self.df.groupby('customer_segment')['Churn'].apply(lambda x: (x == 'Yes').sum() / len(x) * 100)
            axes[1, 1].barh(range(len(segment_churn)), segment_churn.values, color='#a8e6cf')
            axes[1, 1].set_yticks(range(len(segment_churn)))
            axes[1, 1].set_yticklabels(segment_churn.index)
            axes[1, 1].set_title('Churn Rate by Customer Segment')
            axes[1, 1].set_xlabel('Churn Rate (%)')
        
        # 6. Revenue impact by segment
        if 'customer_segment' in self.df.columns:
            churned_customers = self.df[self.df['Churn'] == 'Yes']
            revenue_by_segment = churned_customers.groupby('customer_segment')['MonthlyCharges'].sum()
            axes[1, 2].pie(revenue_by_segment.values, labels=revenue_by_segment.index, autopct='%1.1f%%')
            axes[1, 2].set_title('Revenue Lost by Customer Segment')
        
        plt.tight_layout()
        plt.savefig('telecom_churn_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("Visualizations saved as 'telecom_churn_analysis.png'")
    
    def run_complete_analysis(self):
        """Run the complete analysis pipeline"""
        print("=" * 60)
        print("TELECOM CUSTOMER CHURN & REVENUE ANALYSIS")
        print("=" * 60)
        
        # Run all analyses
        cohort_results = self.cohort_analysis()
        segmentation_results = self.customer_segmentation()
        models, feature_importance = self.predictive_modeling()
        revenue_impact = self.revenue_impact_analysis()
        insights, recommendations = self.generate_insights_and_recommendations()
        
        # Create visualizations
        self.create_visualizations()
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        
        return {
            'cohort_analysis': cohort_results,
            'segmentation': segmentation_results,
            'models': models,
            'feature_importance': feature_importance,
            'revenue_impact': revenue_impact,
            'insights': insights,
            'recommendations': recommendations
        }

# Main execution
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = TelecomChurnAnalyzer('data/WA_Fn-UseC_-Telco-Customer-Churn.csv')
    
    # Run complete analysis
    results = analyzer.run_complete_analysis()
    
    print("\nAnalysis completed successfully!")
    print("Key files generated:")
    print("- telecom_churn_analysis.png (visualizations)")
    print("- All analysis results stored in 'results' variable")
