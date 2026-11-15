-- Drop tables if they already exist to ensure a clean setup
DROP TABLE IF EXISTS fact_regional_metrics CASCADE;
DROP TABLE IF EXISTS dim_region CASCADE;
DROP TABLE IF EXISTS dim_category CASCADE;

-- 1. Region Dimension Table
CREATE TABLE dim_region (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(100) UNIQUE NOT NULL
);

-- 2. Category Dimension Table
CREATE TABLE dim_category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL
);

-- 3. Fact Table linking dimensions with metrics and time periods
CREATE TABLE fact_regional_metrics (
    metric_id SERIAL PRIMARY KEY,
    region_id INT REFERENCES dim_region(region_id),
    category_id INT REFERENCES dim_category(category_id),
    year_quarter VARCHAR(20) NOT NULL,
    metric_value NUMERIC(12, 2) NOT NULL
);