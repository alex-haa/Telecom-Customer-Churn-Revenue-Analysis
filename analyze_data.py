import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('data/WA_Fn-UseC_-Telco-Customer-Churn.csv')

print("=== TELECOM CUSTOMER CHURN DATASET ANALYSIS ===")
print(f"Dataset Shape: {df.shape}")
print(f"Total Records: {df.shape[0]}")
print(f"Total Columns: {df.shape[1]}")

print("\n=== COLUMN INFORMATION ===")
print("Column Names:")
for i, col in enumerate(df.columns, 1):
    print(f"{i:2d}. {col}")

print("\n=== DATA TYPES ===")
print(df.dtypes)

print("\n=== MISSING VALUES ===")
missing_values = df.isnull().sum()
print(missing_values[missing_values > 0])

print("\n=== BASIC STATISTICS ===")
print(df.describe())

print("\n=== CHURN DISTRIBUTION ===")
print(df['Churn'].value_counts())
print(f"Churn Rate: {df['Churn'].value_counts()['Yes'] / len(df) * 100:.2f}%")

print("\n=== CONTRACT DISTRIBUTION ===")
print(df['Contract'].value_counts())

print("\n=== INTERNET SERVICE DISTRIBUTION ===")
print(df['InternetService'].value_counts())

print("\n=== MONTHLY CHARGES BY CHURN STATUS ===")
print(df.groupby('Churn')['MonthlyCharges'].describe())

print("\n=== TENURE BY CHURN STATUS ===")
print(df.groupby('Churn')['tenure'].describe())
