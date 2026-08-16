"""
Dataset generation script for House Price Prediction Model.
Generates a realistic, statistically grounded real estate dataset matching
the features from the Google Stitch design system.
"""

import os
import numpy as np
import pandas as pd

def generate_housing_dataset(n_samples: int = 6000, random_state: int = 42) -> pd.DataFrame:
    np.random.seed(random_state)

    zip_codes_info = {
        "90210": {"base_price_sqft": 850, "metro": "Los Angeles, CA", "premium": 1.45},
        "94102": {"base_price_sqft": 780, "metro": "San Francisco, CA", "premium": 1.35},
        "10001": {"base_price_sqft": 920, "metro": "New York, NY", "premium": 1.55},
        "02108": {"base_price_sqft": 680, "metro": "Boston, MA", "premium": 1.25},
        "98101": {"base_price_sqft": 540, "metro": "Seattle, WA", "premium": 1.15},
        "80202": {"base_price_sqft": 420, "metro": "Denver, CO", "premium": 1.05},
        "78701": {"base_price_sqft": 440, "metro": "Austin, TX", "premium": 1.08},
        "33101": {"base_price_sqft": 480, "metro": "Miami, FL", "premium": 1.12},
        "60601": {"base_price_sqft": 360, "metro": "Chicago, IL", "premium": 0.95},
        "75001": {"base_price_sqft": 260, "metro": "Dallas, TX", "premium": 0.85},
        "30301": {"base_price_sqft": 280, "metro": "Atlanta, GA", "premium": 0.88},
        "85001": {"base_price_sqft": 290, "metro": "Phoenix, AZ", "premium": 0.90},
    }

    zip_keys = list(zip_codes_info.keys())
    zip_probs = [0.08, 0.08, 0.09, 0.07, 0.09, 0.08, 0.10, 0.09, 0.09, 0.08, 0.08, 0.07]
    
    zip_code = np.random.choice(zip_keys, size=n_samples, p=zip_probs)

    property_types = ["Single Family", "Condo", "Townhouse", "Multi-Family"]
    prop_type = np.random.choice(property_types, size=n_samples, p=[0.55, 0.25, 0.15, 0.05])

    # Square footage based on property type
    sqft = np.zeros(n_samples)
    for i in range(n_samples):
        if prop_type[i] == "Condo":
            sqft[i] = int(np.random.normal(1100, 350))
            sqft[i] = max(550, min(sqft[i], 3200))
        elif prop_type[i] == "Townhouse":
            sqft[i] = int(np.random.normal(1800, 450))
            sqft[i] = max(900, min(sqft[i], 3800))
        elif prop_type[i] == "Multi-Family":
            sqft[i] = int(np.random.normal(3200, 800))
            sqft[i] = max(1600, min(sqft[i], 6500))
        else: # Single Family
            sqft[i] = int(np.random.normal(2500, 750))
            sqft[i] = max(800, min(sqft[i], 7500))

    # Bedrooms correlated with sqft
    bedrooms = np.clip(np.round(sqft / 650 + np.random.normal(0, 0.5, n_samples)), 1, 7).astype(int)

    # Bathrooms correlated with bedrooms and sqft
    bathrooms = np.clip(np.round((bedrooms * 0.75 + sqft / 1200 + np.random.normal(0, 0.3, n_samples)) * 2) / 2, 1.0, 6.0)

    # Year built (1930 to 2024)
    year_built = np.random.randint(1940, 2025, size=n_samples)

    # Lot size (acres) based on property type
    lot_size_acres = np.zeros(n_samples)
    for i in range(n_samples):
        if prop_type[i] == "Condo":
            lot_size_acres[i] = round(np.random.uniform(0.01, 0.05), 3)
        elif prop_type[i] == "Townhouse":
            lot_size_acres[i] = round(np.random.uniform(0.04, 0.12), 3)
        else:
            lot_size_acres[i] = round(max(0.08, np.random.exponential(0.35)), 2)
            lot_size_acres[i] = min(lot_size_acres[i], 4.5)

    # Renovation status
    renovations = np.random.choice(
        ["None", "Minor (Cosmetic)", "Major (Structural/Systems)", "Full Gut Rehab"],
        size=n_samples,
        p=[0.40, 0.32, 0.20, 0.08]
    )

    # Garage spaces
    garage_spaces = np.zeros(n_samples, dtype=int)
    for i in range(n_samples):
        if prop_type[i] == "Condo":
            garage_spaces[i] = np.random.choice([0, 1, 2], p=[0.3, 0.5, 0.2])
        else:
            garage_spaces[i] = np.random.choice([0, 1, 2, 3, 4], p=[0.05, 0.25, 0.50, 0.15, 0.05])

    # Renovation multiplier
    renovation_multipliers = {
        "None": 1.0,
        "Minor (Cosmetic)": 1.07,
        "Major (Structural/Systems)": 1.18,
        "Full Gut Rehab": 1.28
    }

    # Property type multiplier
    prop_multipliers = {
        "Single Family": 1.05,
        "Condo": 0.95,
        "Townhouse": 1.00,
        "Multi-Family": 1.15
    }

    current_year = 2026
    prices = np.zeros(n_samples)

    for i in range(n_samples):
        zc = zip_code[i]
        base_rate = zip_codes_info[zc]["base_price_sqft"]
        
        # Base value by area
        base_val = sqft[i] * base_rate
        
        # Bedroom & Bathroom adjustments
        room_adj = (bedrooms[i] * 12000) + (bathrooms[i] * 18000)
        
        # Age depreciation factor (0.2% per year of age up to 40 years, older homes with character stabilize)
        age = current_year - year_built[i]
        age_factor = max(0.75, 1.0 - (min(age, 45) * 0.0055))
        
        # Lot value
        lot_val = lot_size_acres[i] * 45000 * zip_codes_info[zc]["premium"]
        
        # Garage bonus
        garage_val = garage_spaces[i] * 15000
        
        # Renovation factor
        renov_factor = renovation_multipliers[renovations[i]]
        
        # Property type factor
        p_type_factor = prop_multipliers[prop_type[i]]
        
        # Combine
        estimated = (base_val * age_factor * renov_factor * p_type_factor) + room_adj + lot_val + garage_val
        
        # Add realistic market variance (+/- 3.5%)
        noise = np.random.normal(1.0, 0.035)
        final_price = round(estimated * noise, -2) # round to nearest 100
        prices[i] = max(120000, final_price)

    df = pd.DataFrame({
        "zip_code": zip_code,
        "square_footage": sqft.astype(int),
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "year_built": year_built,
        "lot_size_acres": lot_size_acres,
        "renovation_status": renovations,
        "property_type": prop_type,
        "garage_spaces": garage_spaces,
        "price": prices
    })

    return df

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__))
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "dataset.csv")
    
    print(f"Generating housing dataset with 6,000 samples...")
    df = generate_housing_dataset()
    df.to_csv(csv_path, index=False)
    print(f"Dataset generated successfully at: {csv_path}")
    print(f"Shape: {df.shape}")
    print(df.head())
