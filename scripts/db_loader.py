import os
import pandas as pd
from sqlalchemy import create_engine, text

def load_data_to_postgres():
    cleaned_path = "data/cleaned_public_data.csv"
    if not os.path.exists(cleaned_path):
        print(f"❌ Error: {cleaned_path} not found. Please run your cleaning script first!")
        return

    print("🔌 Connecting to PostgreSQL database...")
    
    # Database connection parameters (Modify if your local setup uses a different password/user)
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "nz_pipeline_db")

    connection_string = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        engine = create_engine(connection_string)
        df = pd.read_csv(cleaned_path)
        
        with engine.begin() as connection:
            # 1. Populate dim_region
            regions = df['Region'].unique()
            for r in regions:
                connection.execute(
                    text("INSERT INTO dim_region (region_name) VALUES (:name) ON CONFLICT (region_name) DO NOTHING"),
                    {"name": r}
                )
            
            # 2. Populate dim_category
            categories = df['Category'].unique()
            for c in categories:
                connection.execute(
                    text("INSERT INTO dim_category (category_name) VALUES (:name) ON CONFLICT (category_name) DO NOTHING"),
                    {"name": c}
                )
            
            # Fetch dimension mappings back into dictionaries
            region_map = {row[1]: row[0] for row in connection.execute(text("SELECT region_id, region_name FROM dim_region")).fetchall()}
            category_map = {row[1]: row[0] for row in connection.execute(text("SELECT category_id, category_name FROM dim_category")).fetchall()}
            
            # 3. Populate fact table
            connection.execute(text("TRUNCATE TABLE fact_regional_metrics RESTART IDENTITY CASCADE"))
            
            fact_records = []
            for _, row in df.iterrows():
                fact_records.append({
                    "region_id": region_map[row['Region']],
                    "category_id": category_map[row['Category']],
                    "year_quarter": row['Year_Quarter'],
                    "metric_value": row['Metric_Value']
                })
            
            for record in fact_records:
                connection.execute(
                    text("""
                        INSERT INTO fact_regional_metrics (region_id, category_id, year_quarter, metric_value)
                        VALUES (:region_id, :category_id, :year_quarter, :metric_value)
                    """),
                    record
                )
                
        print("✅ Data successfully loaded into PostgreSQL Star Schema!")
        
    except Exception as e:
        print(f"⚠️ Database connection note: Ensure your PostgreSQL server is running and database '{db_name}' exists. Error: {e}")

if __name__ == "__main__":
    load_data_to_postgres()