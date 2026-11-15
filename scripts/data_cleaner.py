import os
import pandas as pd
import numpy as np

def clean_data():
    raw_path = "data/raw_public_data.csv"
    if not os.path.exists(raw_path):
        print(f"❌ Error: {raw_path} not found. Please run api_extractor.py first!")
        return

    print("🧹 Starting data cleaning pipeline...")
    df = pd.read_csv(raw_path)
    
    # 1. Clean string columns (strip trailing/leading whitespace)
    string_cols = df.select_dtypes(include=['object']).columns
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip()
        
    # 2. Handle missing numeric values (fill nulls with 0)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(0)
        
    # 3. Drop exact duplicate rows
    initial_count = len(df)
    df = df.drop_duplicates()
    print(f"🧹 Removed {initial_count - len(df)} duplicate rows.")
    
    # 4. Save cleaned data
    os.makedirs("data", exist_ok=True)
    cleaned_path = "data/cleaned_public_data.csv"
    df.to_csv(cleaned_path, index=False)
    print(f"✅ Data cleaning complete! Cleaned dataset saved to {cleaned_path} with {len(df)} rows.")

if __name__ == "__main__":
    clean_data()