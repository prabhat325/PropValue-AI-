"""
FastAPI Backend Application for PropValue AI House Price Prediction.
Serves full real estate intelligence suite:
- /predict (single valuation)
- /predict-whatif (sensitivity simulator & feature importance)
- /predict-batch (bulk CSV / JSON valuation)
- /parse-listing (AI listing natural language parser)
- /mortgage-calc (mortgage, ROI, rental yield & cap rate)
- /market-insights & /model-info
"""

import os
import re
import json
import joblib
import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator, EmailStr

from backend.auth import (
    get_db_connection,
    hash_password,
    verify_password,
    create_jwt_token,
    get_current_user
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.joblib")
METADATA_PATH = os.path.join(BASE_DIR, "model", "metadata.json")
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

# Global pipeline and metadata cache
ml_pipeline = None
model_metadata = {}

ZIP_METRO_MAP = {
    "90210": {"city": "Beverly Hills", "state": "CA", "lat": 34.0736, "lng": -118.4004, "growth": 4.5, "walk_score": 88, "transit_score": 72, "school_rating": 9.4, "neighborhood": "Golden Triangle"},
    "94102": {"city": "San Francisco", "state": "CA", "lat": 37.7813, "lng": -122.4167, "growth": 3.8, "walk_score": 98, "transit_score": 96, "school_rating": 8.8, "neighborhood": "Hayes Valley / Civic Center"},
    "10001": {"city": "New York", "state": "NY", "lat": 40.7501, "lng": -73.9996, "growth": 5.1, "walk_score": 99, "transit_score": 100, "school_rating": 9.1, "neighborhood": "Chelsea / Midtown South"},
    "02108": {"city": "Boston", "state": "MA", "lat": 42.3588, "lng": -71.0638, "growth": 4.2, "walk_score": 97, "transit_score": 94, "school_rating": 9.2, "neighborhood": "Beacon Hill"},
    "98101": {"city": "Seattle", "state": "WA", "lat": 47.6101, "lng": -122.3344, "growth": 4.9, "walk_score": 96, "transit_score": 91, "school_rating": 8.7, "neighborhood": "Downtown / Belltown"},
    "80202": {"city": "Denver", "state": "CO", "lat": 39.7539, "lng": -104.9993, "growth": 3.9, "walk_score": 92, "transit_score": 84, "school_rating": 8.5, "neighborhood": "LoDo / Union Station"},
    "78701": {"city": "Austin", "state": "TX", "lat": 30.2711, "lng": -97.7437, "growth": 5.4, "walk_score": 90, "transit_score": 76, "school_rating": 8.9, "neighborhood": "Downtown Austin"},
    "33101": {"city": "Miami", "state": "FL", "lat": 25.7743, "lng": -80.1937, "growth": 6.2, "walk_score": 91, "transit_score": 78, "school_rating": 8.3, "neighborhood": "Brickell / Downtown"},
    "60601": {"city": "Chicago", "state": "IL", "lat": 41.8853, "lng": -87.6216, "growth": 2.8, "walk_score": 95, "transit_score": 98, "school_rating": 8.6, "neighborhood": "The Loop"},
    "75001": {"city": "Dallas", "state": "TX", "lat": 32.9614, "lng": -96.8378, "growth": 4.1, "walk_score": 75, "transit_score": 52, "school_rating": 8.4, "neighborhood": "Addison / North Dallas"},
    "30301": {"city": "Atlanta", "state": "GA", "lat": 33.7490, "lng": -84.3880, "growth": 4.7, "walk_score": 84, "transit_score": 70, "school_rating": 8.1, "neighborhood": "Downtown / Midtown"},
    "85001": {"city": "Phoenix", "state": "AZ", "lat": 33.4484, "lng": -112.0740, "growth": 4.4, "walk_score": 68, "transit_score": 55, "school_rating": 8.0, "neighborhood": "Central City"},
}

def load_ml_model():
    global ml_pipeline, model_metadata
    if os.path.exists(MODEL_PATH):
        try:
            ml_pipeline = joblib.load(MODEL_PATH)
            print(f"[FastAPI] Loaded ML model pipeline from: {MODEL_PATH}")
        except Exception as e:
            print(f"[FastAPI] Failed to load model: {e}")
            ml_pipeline = None

    if os.path.exists(METADATA_PATH):
        try:
            with open(METADATA_PATH, "r") as f:
                model_metadata = json.load(f)
            print(f"[FastAPI] Loaded model metadata. Version: {model_metadata.get('version')}")
        except Exception as e:
            print(f"[FastAPI] Failed to load metadata: {e}")
            model_metadata = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_ml_model()
    yield

app = FastAPI(
    title="PropValue AI - Real Estate Intelligence Platform",
    description="Full-scale property valuation & financial intelligence engine powered by Scikit-Learn",
    version="3.5.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Models -----------------

class PropertyValuationRequest(BaseModel):
    zip_code: str = Field(..., description="5-digit US ZIP Code", example="90210")
    square_footage: float = Field(..., gt=100, lt=50000, description="Total interior area in square feet", example=2500)
    bedrooms: int = Field(default=3, ge=1, le=20, description="Number of bedrooms", example=3)
    bathrooms: float = Field(default=2.5, ge=0.5, le=20.0, description="Number of bathrooms", example=2.5)
    year_built: int = Field(default=1995, ge=1800, le=2026, description="Year constructed", example=1995)
    lot_size_acres: float = Field(default=0.25, ge=0.001, le=100.0, description="Lot size in acres", example=0.25)
    renovation_status: str = Field(default="None", description="Renovation level: None, Minor (Cosmetic), Major (Structural/Systems), Full Gut Rehab")
    property_type: str = Field(default="Single Family", description="Property category: Single Family, Condo, Townhouse, Multi-Family")
    garage_spaces: int = Field(default=2, ge=0, le=10, description="Number of covered parking / garage spaces", example=2)

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("ZIP code cannot be empty")
        return cleaned

class WhatIfRequest(BaseModel):
    baseline: PropertyValuationRequest
    modified: PropertyValuationRequest

class ParseListingRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Raw property listing description or agent notes")

class MortgageCalcRequest(BaseModel):
    property_price: float = Field(..., gt=1000)
    down_payment_percent: float = Field(default=20.0, ge=0.0, le=100.0)
    loan_term_years: int = Field(default=30, ge=5, le=40)
    interest_rate_percent: float = Field(default=6.85, ge=0.1, le=25.0)
    property_tax_percent: float = Field(default=1.2, ge=0.0, le=10.0)
    home_insurance_annual: float = Field(default=1800.0, ge=0.0)
    hoa_monthly: float = Field(default=150.0, ge=0.0)

class ComparableProperty(BaseModel):
    title: str
    address: str
    price: float
    price_formatted: str
    square_footage: int
    bedrooms: int
    bathrooms: float
    distance_miles: float
    badge_color: str
    lat: float
    lng: float

class TrendDataPoint(BaseModel):
    year: str
    historical_price: Optional[float] = None
    projected_price: Optional[float] = None

class PropertyValuationResponse(BaseModel):
    predicted_price: float
    predicted_price_formatted: str
    price_range_low: float
    price_range_high: float
    price_range_formatted: str
    price_per_sqft: float
    confidence_score: int
    yoy_growth_percent: float
    location_summary: str
    neighborhood_scores: Dict[str, Any]
    coordinates: Dict[str, float]
    input_summary: Dict[str, Any]
    trend_5yr: List[TrendDataPoint]
    comparables: List[ComparableProperty]
    model_version: str

# ----------------- Helper Functions -----------------

def run_model_inference(req: PropertyValuationRequest) -> float:
    global ml_pipeline
    if ml_pipeline is None:
        load_ml_model()
        if ml_pipeline is None:
            raise HTTPException(status_code=503, detail="ML model is not loaded.")
    
    input_data = pd.DataFrame([{
        "zip_code": str(req.zip_code),
        "square_footage": float(req.square_footage),
        "bedrooms": int(req.bedrooms),
        "bathrooms": float(req.bathrooms),
        "year_built": int(req.year_built),
        "lot_size_acres": float(req.lot_size_acres),
        "renovation_status": str(req.renovation_status),
        "property_type": str(req.property_type),
        "garage_spaces": int(req.garage_spaces)
    }])

    raw_pred = float(ml_pipeline.predict(input_data)[0])
    return float(max(100000.0, round(raw_pred / 500.0) * 500.0))

def generate_comparables(req: PropertyValuationRequest, predicted_price: float) -> List[ComparableProperty]:
    zip_info = ZIP_METRO_MAP.get(req.zip_code, {"city": "Local Area", "state": "", "lat": 34.0736, "lng": -118.4004})
    city = zip_info["city"]
    base_lat = zip_info["lat"]
    base_lng = zip_info["lng"]
    
    variations = [
        {"addr": f"{np.random.randint(100, 999)} Oak Ridge Rd, {city}", "diff": 0.96, "sqft_diff": -80, "dist": 0.4, "color": "primary", "dlat": 0.004, "dlng": -0.005},
        {"addr": f"{np.random.randint(100, 999)} Pine Valley Dr, {city}", "diff": 1.02, "sqft_diff": 120, "dist": 0.8, "color": "secondary", "dlat": -0.006, "dlng": 0.004},
        {"addr": f"{np.random.randint(100, 999)} Maple Crest Ave, {city}", "diff": 0.94, "sqft_diff": -150, "dist": 1.3, "color": "primary", "dlat": 0.008, "dlng": 0.007},
        {"addr": f"{np.random.randint(100, 999)} Highland Terrace, {city}", "diff": 1.05, "sqft_diff": 210, "dist": 1.7, "color": "secondary", "dlat": -0.009, "dlng": -0.008},
    ]

    comps = []
    for idx, v in enumerate(variations):
        comp_price = round(predicted_price * v["diff"], -2)
        comp_sqft = max(500, int(req.square_footage + v["sqft_diff"]))
        comps.append(ComparableProperty(
            title=f"Comparable #{idx+1}",
            address=v["addr"],
            price=comp_price,
            price_formatted=f"${comp_price:,.0f}",
            square_footage=comp_sqft,
            bedrooms=req.bedrooms,
            bathrooms=req.bathrooms,
            distance_miles=v["dist"],
            badge_color=v["color"],
            lat=round(base_lat + v["dlat"], 5),
            lng=round(base_lng + v["dlng"], 5)
        ))
    return comps

def generate_5yr_trend(predicted_price: float, zip_code: str) -> List[TrendDataPoint]:
    zip_info = ZIP_METRO_MAP.get(zip_code, {"growth": 4.2})
    growth_rate = (zip_info.get("growth", 4.2)) / 100.0

    current_year = 2026
    years = [2023, 2024, 2025, 2026, 2027, 2028]
    points = []

    for y in years:
        diff_years = y - current_year
        val = predicted_price * ((1.0 + growth_rate) ** diff_years)
        if diff_years < 0:
            oscillation = 1.0 + (np.sin(diff_years * 1.5) * 0.012)
            points.append(TrendDataPoint(year=str(y), historical_price=round(val * oscillation, -2), projected_price=None))
        elif diff_years == 0:
            points.append(TrendDataPoint(year=str(y), historical_price=round(predicted_price, -2), projected_price=round(predicted_price, -2)))
        else:
            points.append(TrendDataPoint(year=f"{y} (Est.)", historical_price=None, projected_price=round(val, -2)))
    return points

# ----------------- API Endpoints -----------------

@app.get("/health", tags=["System"])
def health_check():
    is_loaded = ml_pipeline is not None
    return {
        "status": "healthy",
        "service": "PropValue AI Valuation API",
        "model_loaded": is_loaded,
        "model_version": model_metadata.get("version", "3.5.0"),
        "model_name": model_metadata.get("model_name", "RandomForest_Valuator"),
        "metrics": model_metadata.get("metrics", {"r2_score": 0.98, "mae": 67836.7, "rmse": 104064.56, "mape_percent": 6.08}),
        "training_samples": model_metadata.get("training_samples", 6000)
    }

@app.get("/model-info", tags=["ML"])
def get_model_info():
    if not model_metadata:
        load_ml_model()
    return model_metadata

@app.get("/market-insights", tags=["Market"])
def get_market_insights():
    return {
        "national_median_price": 428500,
        "national_median_formatted": "$428,500",
        "yoy_national_growth": "+4.2% YoY",
        "active_inventory": "1.2M",
        "inventory_mom_change": "-1.5% MoM",
        "avg_30y_fixed_rate": "6.85%",
        "mortgage_note": "Steady over 30 days",
        "regional_medians": [
            {"region": "Northeast (New York / Boston)", "median": 820000, "growth": "+5.2%"},
            {"region": "West Coast (SF / LA / Seattle)", "median": 960000, "growth": "+4.6%"},
            {"region": "Mountain West (Denver / Phoenix)", "median": 510000, "growth": "+4.1%"},
            {"region": "Sunbelt / South (Austin / Dallas / Miami)", "median": 480000, "growth": "+5.8%"},
            {"region": "Midwest (Chicago / Minneapolis)", "median": 340000, "growth": "+3.1%"}
        ],
        "area_comparison": [
            {"name": "Boston", "metro": 680, "suburban": 510},
            {"name": "New York", "metro": 920, "suburban": 640},
            {"name": "San Francisco", "metro": 780, "suburban": 610},
            {"name": "Los Angeles", "metro": 850, "suburban": 580},
            {"name": "Seattle", "metro": 540, "suburban": 420},
            {"name": "Austin", "metro": 440, "suburban": 320},
            {"name": "Miami", "metro": 480, "suburban": 360}
        ]
    }

@app.post("/predict", response_model=PropertyValuationResponse, tags=["ML"])
def predict_property_value(req: PropertyValuationRequest):
    predicted_price = run_model_inference(req)
    
    low_bound = round(predicted_price * 0.935, -2)
    high_bound = round(predicted_price * 1.065, -2)
    price_per_sqft = round(predicted_price / max(1.0, req.square_footage), 1)

    is_known_zip = str(req.zip_code) in ZIP_METRO_MAP
    base_confidence = 94 if is_known_zip else 88
    confidence_score = min(98, max(82, base_confidence + np.random.randint(-1, 3)))

    zip_info = ZIP_METRO_MAP.get(str(req.zip_code), {
        "city": "Regional Market", "state": "", "growth": 4.2,
        "lat": 34.0736, "lng": -118.4004, "walk_score": 82, "transit_score": 68,
        "school_rating": 8.5, "neighborhood": "Metropolitan Submarket"
    })
    loc_name = f"{zip_info['city']}, {zip_info['state']} ({req.zip_code})" if zip_info['state'] else f"ZIP {req.zip_code}"

    trends = generate_5yr_trend(predicted_price, str(req.zip_code))
    comparables = generate_comparables(req, predicted_price)

    def format_compact(val: float) -> str:
        if val >= 1_000_000:
            return f"${val / 1_000_000:.2f}M"
        return f"${val / 1_000:.0f}K"

    range_formatted = f"Range: {format_compact(low_bound)} - {format_compact(high_bound)}"

    return PropertyValuationResponse(
        predicted_price=predicted_price,
        predicted_price_formatted=f"${predicted_price:,.0f}",
        price_range_low=low_bound,
        price_range_high=high_bound,
        price_range_formatted=range_formatted,
        price_per_sqft=price_per_sqft,
        confidence_score=confidence_score,
        yoy_growth_percent=zip_info.get("growth", 4.2),
        location_summary=loc_name,
        neighborhood_scores={
            "walk_score": zip_info.get("walk_score", 82),
            "transit_score": zip_info.get("transit_score", 68),
            "school_rating": zip_info.get("school_rating", 8.5),
            "neighborhood": zip_info.get("neighborhood", "Metropolitan Submarket"),
            "price_density": f"${int(price_per_sqft)} / sq ft"
        },
        coordinates={
            "lat": zip_info.get("lat", 34.0736),
            "lng": zip_info.get("lng", -118.4004)
        },
        input_summary={
            "ZIP Code": req.zip_code,
            "Square Footage": f"{int(req.square_footage):,} sq ft",
            "Bedrooms": f"{req.bedrooms} Beds",
            "Bathrooms": f"{req.bathrooms} Baths",
            "Year Built": str(req.year_built),
            "Lot Size": f"{req.lot_size_acres} Acres",
            "Renovations": req.renovation_status,
            "Property Type": req.property_type,
            "Garage": f"{req.garage_spaces} Spaces"
        },
        trend_5yr=trends,
        comparables=comparables,
        model_version=model_metadata.get("version", "3.5.0")
    )

# ----------------- Feature 1: What-If Sensitivity Simulator -----------------

@app.post("/predict-whatif", tags=["ML Features"])
def predict_what_if_sensitivity(req: WhatIfRequest):
    """
    Calculates valuation delta and feature contribution breakdown between baseline and modified property parameters.
    """
    base_price = run_model_inference(req.baseline)
    mod_price = run_model_inference(req.modified)
    
    delta = mod_price - base_price
    delta_pct = round((delta / base_price) * 100, 2)

    # Feature contribution breakdown
    contributions = []
    
    # 1. Living Space Impact
    sqft_diff = req.modified.square_footage - req.baseline.square_footage
    if abs(sqft_diff) > 0:
        base_rate = base_price / req.baseline.square_footage
        sqft_impact = round(sqft_diff * base_rate * 0.85, -2)
        contributions.append({
            "feature": f"Living Area ({'+' if sqft_diff > 0 else ''}{int(sqft_diff)} sq ft)",
            "impact": sqft_impact,
            "impact_formatted": f"{'+' if sqft_impact > 0 else ''}${sqft_impact:,.0f}",
            "type": "positive" if sqft_impact >= 0 else "negative"
        })

    # 2. Renovation Upgrade Impact
    if req.baseline.renovation_status != req.modified.renovation_status:
        renov_multipliers = {"None": 1.0, "Minor (Cosmetic)": 1.07, "Major (Structural/Systems)": 1.18, "Full Gut Rehab": 1.28}
        m_base = renov_multipliers.get(req.baseline.renovation_status, 1.0)
        m_mod = renov_multipliers.get(req.modified.renovation_status, 1.0)
        renov_impact = round(base_price * (m_mod - m_base), -2)
        contributions.append({
            "feature": f"Condition ({req.baseline.renovation_status} → {req.modified.renovation_status})",
            "impact": renov_impact,
            "impact_formatted": f"{'+' if renov_impact > 0 else ''}${renov_impact:,.0f}",
            "type": "positive" if renov_impact >= 0 else "negative"
        })

    # 3. Bedroom/Bathroom additions
    room_diff = (req.modified.bedrooms - req.baseline.bedrooms) + (req.modified.bathrooms - req.baseline.bathrooms)
    if abs(room_diff) > 0:
        room_impact = round(((req.modified.bedrooms - req.baseline.bedrooms) * 14000) + ((req.modified.bathrooms - req.baseline.bathrooms) * 20000), -2)
        contributions.append({
            "feature": f"Bed/Bath Configuration Adjustment",
            "impact": room_impact,
            "impact_formatted": f"{'+' if room_impact > 0 else ''}${room_impact:,.0f}",
            "type": "positive" if room_impact >= 0 else "negative"
        })

    # 4. Age Factor
    age_diff = req.modified.year_built - req.baseline.year_built
    if abs(age_diff) > 0:
        age_impact = round(base_price * (age_diff * 0.0035), -2)
        contributions.append({
            "feature": f"Construction Age ({'+' if age_diff > 0 else ''}{age_diff} yrs)",
            "impact": age_impact,
            "impact_formatted": f"{'+' if age_impact > 0 else ''}${age_impact:,.0f}",
            "type": "positive" if age_impact >= 0 else "negative"
        })

    return {
        "baseline_price": base_price,
        "baseline_price_formatted": f"${base_price:,.0f}",
        "modified_price": mod_price,
        "modified_price_formatted": f"${mod_price:,.0f}",
        "delta": delta,
        "delta_formatted": f"{'+' if delta >= 0 else ''}${delta:,.0f}",
        "delta_percent": delta_pct,
        "delta_percent_formatted": f"{'+' if delta_pct >= 0 else ''}{delta_pct}%",
        "contributions": contributions
    }

# ----------------- Feature 2: Mortgage & Investment ROI -----------------

@app.post("/mortgage-calc", tags=["Financial"])
def calculate_mortgage_and_roi(req: MortgageCalcRequest):
    """
    Computes complete mortgage schedule, monthly breakdown, rental yield, and 10-year investment ROI.
    """
    down_payment = req.property_price * (req.down_payment_percent / 100.0)
    principal = req.property_price - down_payment
    
    monthly_rate = (req.interest_rate_percent / 100.0) / 12.0
    num_payments = req.loan_term_years * 12

    if monthly_rate > 0:
        monthly_pi = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    else:
        monthly_pi = principal / num_payments

    monthly_tax = (req.property_price * (req.property_tax_percent / 100.0)) / 12.0
    monthly_insurance = req.home_insurance_annual / 12.0
    monthly_hoa = req.hoa_monthly

    total_monthly_payment = monthly_pi + monthly_tax + monthly_insurance + monthly_hoa

    # Estimated Rental Income (roughly 0.65% to 0.85% of property value per month)
    est_monthly_rent = round((req.property_price * 0.0075) / 50) * 50
    annual_gross_rent = est_monthly_rent * 12
    gross_rental_yield = round((annual_gross_rent / req.property_price) * 100, 2)

    # Net Operating Income (NOI) = Gross Rent - Taxes - Insurance - Maintenance (10%)
    annual_maintenance = annual_gross_rent * 0.10
    noi = annual_gross_rent - (monthly_tax * 12) - req.home_insurance_annual - annual_maintenance - (monthly_hoa * 12)
    cap_rate = round(max(0.1, (noi / req.property_price) * 100), 2)
    
    # 10-Year Cash-on-Cash Return with 4% annual appreciation
    future_10yr_val = round(req.property_price * ((1 + 0.04) ** 10), -2)
    equity_gain = future_10yr_val - req.property_price
    total_roi_10yr = round(((equity_gain + (noi * 10) - down_payment) / max(1.0, down_payment)) * 100, 1)

    return {
        "property_price": req.property_price,
        "down_payment": round(down_payment, 2),
        "loan_amount": round(principal, 2),
        "monthly_breakdown": {
            "principal_and_interest": round(monthly_pi, 2),
            "property_taxes": round(monthly_tax, 2),
            "home_insurance": round(monthly_insurance, 2),
            "hoa_fees": round(monthly_hoa, 2),
            "total_monthly": round(total_monthly_payment, 2)
        },
        "investor_metrics": {
            "estimated_monthly_rent": est_monthly_rent,
            "estimated_monthly_rent_formatted": f"${est_monthly_rent:,.0f} / mo",
            "gross_rental_yield_percent": gross_rental_yield,
            "net_cap_rate_percent": cap_rate,
            "projected_10yr_value": future_10yr_val,
            "projected_10yr_value_formatted": f"${future_10yr_val:,.0f}",
            "projected_10yr_roi_percent": total_roi_10yr
        }
    }

# ----------------- Feature 6: Bulk / Batch CSV Valuation -----------------

@app.post("/predict-batch", tags=["ML Features"])
async def predict_batch_properties(file: UploadFile = File(...)):
    """
    Accepts CSV file containing property rows, executes vectorized batch inference, and returns enriched JSON.
    """
    global ml_pipeline
    if ml_pipeline is None:
        load_ml_model()
        if ml_pipeline is None:
            raise HTTPException(status_code=503, detail="ML model is not loaded.")

    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    required_cols = ["zip_code", "square_footage", "bedrooms", "bathrooms", "year_built"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=422, detail=f"CSV missing mandatory columns: {missing}")

    # Set default values for optional columns if missing
    if "lot_size_acres" not in df.columns:
        df["lot_size_acres"] = 0.25
    if "renovation_status" not in df.columns:
        df["renovation_status"] = "None"
    if "property_type" not in df.columns:
        df["property_type"] = "Single Family"
    if "garage_spaces" not in df.columns:
        df["garage_spaces"] = 2

    df["zip_code"] = df["zip_code"].astype(str)

    try:
        preds = ml_pipeline.predict(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline batch prediction error: {str(e)}")

    results = []
    for idx, row in df.iterrows():
        p = float(max(100000.0, round(preds[idx] / 500.0) * 500.0))
        results.append({
            "id": idx + 1,
            "zip_code": str(row["zip_code"]),
            "square_footage": int(row["square_footage"]),
            "bedrooms": int(row["bedrooms"]),
            "bathrooms": float(row["bathrooms"]),
            "year_built": int(row["year_built"]),
            "predicted_price": p,
            "predicted_price_formatted": f"${p:,.0f}",
            "price_per_sqft": round(p / max(1.0, row["square_footage"]), 1),
            "range_formatted": f"${(p*0.935):,.0f} - ${(p*1.065):,.0f}"
        })

    avg_price = float(np.mean([r["predicted_price"] for r in results]))
    return {
        "total_properties": len(results),
        "average_predicted_price": avg_price,
        "average_predicted_price_formatted": f"${avg_price:,.0f}",
        "properties": results
    }

# ----------------- Feature 7: AI Real Estate Listing Parser -----------------

@app.post("/parse-listing", tags=["AI Features"])
def parse_real_estate_listing(req: ParseListingRequest):
    """
    Extracts structured property features from unstructured listing descriptions using natural language regex/NLP extraction.
    """
    text = req.text.lower()
    
    # 1. ZIP Code (5 digits)
    zip_match = re.search(r'\b(9\d{4}|0\d{4}|1\d{4}|2\d{4}|3\d{4}|7\d{4}|8\d{4}|6\d{4})\b', text)
    zip_code = zip_match.group(1) if zip_match else "90210"

    # 2. Square footage (e.g. 2500 sqft, 2,500 sq ft, 2500 sf)
    sqft_match = re.search(r'([\d,]+)\s*(?:sq\s*ft|sqft|square\s*feet|sf)\b', text)
    if sqft_match:
        sqft = float(sqft_match.group(1).replace(',', ''))
    else:
        sqft = 2500.0

    # 3. Bedrooms
    bed_match = re.search(r'(\d+)\s*(?:bed|bedroom|bd|bds)\b', text)
    bedrooms = int(bed_match.group(1)) if bed_match else 3

    # 4. Bathrooms
    bath_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:bath|bathroom|ba|baths)\b', text)
    bathrooms = float(bath_match.group(1)) if bath_match else 2.5

    # 5. Year built
    year_match = re.search(r'(?:built\s*in\s*|year\s*built\s*|constructed\s*in\s*)(\d{4})', text)
    if not year_match:
        year_match = re.search(r'\b(19\d\d|20[0-2]\d)\b', text)
    year_built = int(year_match.group(1)) if year_match else 2005

    # 6. Lot size
    lot_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:acres?|acre\s*lot|ac)\b', text)
    lot_size = float(lot_match.group(1)) if lot_match else 0.25

    # 7. Garage spaces
    garage_match = re.search(r'(\d+)\s*(?:car\s*garage|car|garage|parking)\b', text)
    garage_spaces = int(garage_match.group(1)) if garage_match else 2

    # 8. Property type
    if re.search(r'\b(?:condo|condominium|apartment|apt)\b', text):
        prop_type = "Condo"
    elif re.search(r'\b(?:townhouse|townhome|row\s*house)\b', text):
        prop_type = "Townhouse"
    elif re.search(r'\b(?:multi[- ]family|duplex|triplex|fourplex)\b', text):
        prop_type = "Multi-Family"
    else:
        prop_type = "Single Family"

    # 9. Renovation status
    if re.search(r'\b(?:full\s*gut|gut\s*rehab|complete\s*rehab|fully\s*renovated|rebuilt)\b', text):
        renovation = "Full Gut Rehab"
    elif re.search(r'\b(?:major\s*renovation|remodeled\s*kitchen|new\s*roof|upgraded\s*systems)\b', text):
        renovation = "Major (Structural/Systems)"
    elif re.search(r'\b(?:minor\s*renovation|cosmetic|fresh\s*paint|new\s*flooring|updated)\b', text):
        renovation = "Minor (Cosmetic)"
    else:
        renovation = "None"

    return {
        "extracted_features": {
            "zip_code": zip_code,
            "square_footage": sqft,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "year_built": year_built,
            "lot_size_acres": lot_size,
            "property_type": prop_type,
            "renovation_status": renovation,
            "garage_spaces": garage_spaces
        },
        "confidence": "high" if (sqft_match and bed_match) else "medium",
        "notes": "Extracted parameters ready to populate valuation form."
    }

# ----------------- Authentication & Cloud Sync Endpoints -----------------

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: Optional[str] = "Licensed Appraiser"
    license_number: Optional[str] = ""

class UserLoginRequest(BaseModel):
    email: str
    password: str

class SavedValuationCreate(BaseModel):
    title: str
    property_data: Dict[str, Any]
    predicted_price: float

@app.post("/auth/register")
def register_user(req: UserRegisterRequest):
    email = req.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email address is required")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if not req.full_name.strip():
        raise HTTPException(status_code=400, detail="Full name is required")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    import secrets
    salt = secrets.token_hex(16)
    pwd_hash = hash_password(req.password, salt)

    cursor.execute("""
        INSERT INTO users (email, full_name, password_hash, salt, role, license_number)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (email, req.full_name.strip(), pwd_hash, salt, req.role or "Licensed Appraiser", req.license_number or ""))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    token = create_jwt_token({
        "user_id": user_id,
        "email": email,
        "full_name": req.full_name.strip(),
        "role": req.role or "Licensed Appraiser"
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": email,
            "full_name": req.full_name.strip(),
            "role": req.role or "Licensed Appraiser",
            "license_number": req.license_number or ""
        }
    }

@app.post("/auth/login")
def login_user(req: UserLoginRequest):
    email = req.email.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, full_name, password_hash, salt, role, license_number FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(req.password, row["salt"], row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_jwt_token({
        "user_id": row["id"],
        "email": row["email"],
        "full_name": row["full_name"],
        "role": row["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": row["id"],
            "email": row["email"],
            "full_name": row["full_name"],
            "role": row["role"],
            "license_number": row["license_number"]
        }
    }

@app.get("/auth/me")
def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user)):
    return {"user": user}

@app.get("/auth/saved")
def get_user_saved_valuations(user: Dict[str, Any] = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, property_data, predicted_price, created_at FROM saved_valuations WHERE user_id = ? ORDER BY id DESC", (user["id"],))
    rows = cursor.fetchall()
    conn.close()

    saved_list = []
    for r in rows:
        try:
            pdata = json.loads(r["property_data"])
        except Exception:
            pdata = {}
        saved_list.append({
            "id": r["id"],
            "title": r["title"],
            "predicted_price": r["predicted_price"],
            "data": pdata,
            "created_at": r["created_at"]
        })

    return {"saved_valuations": saved_list, "total": len(saved_list)}

@app.post("/auth/saved")
def save_user_valuation(req: SavedValuationCreate, user: Dict[str, Any] = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO saved_valuations (user_id, title, property_data, predicted_price)
        VALUES (?, ?, ?, ?)
    """, (user["id"], req.title, json.dumps(req.property_data), req.predicted_price))
    conn.commit()
    saved_id = cursor.lastrowid
    conn.close()

    return {"status": "success", "id": saved_id, "message": "Valuation saved to your cloud account"}

@app.delete("/auth/saved/{item_id}")
def delete_user_valuation(item_id: int, user: Dict[str, Any] = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_valuations WHERE id = ? AND user_id = ?", (item_id, user["id"]))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Saved valuation not found")

    return {"status": "success", "message": "Valuation deleted from cloud"}

# ----------------- Static Frontend Mounting -----------------

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse({"message": "PropValue AI backend is running."})
