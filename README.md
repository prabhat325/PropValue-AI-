# PropValue AI - Precision Real Estate Intelligence Suite

A complete, production-grade Real Estate Valuation and Financial Intelligence Platform built with a **Scikit-Learn Machine Learning Pipeline**, **FastAPI Backend**, and a modern **Google Stitch UI/UX Design System** ("Precision Estate Narrative").

---

## 🌟 Complete Feature Suite (7 Advanced Capabilities)

### 1. 🧠 Interactive "What-If" Sensitivity Simulator & Feature Drivers
- Real-time sensitivity sliders to adjust living space ($\pm \text{sq ft}$), bedrooms, bathrooms, and garage capacity.
- 1-click **Renovation Upgrade Toggles** (`None` $\rightarrow$ `Minor` $\rightarrow$ `Major` $\rightarrow$ `Full Gut Rehab`).
- Live $+\Delta$ and $-\Delta$ valuation impact and **Feature Contribution Waterfall** breakdown.

### 2. 💰 Integrated Mortgage & Investor ROI / Rental Yield Calculator
- Amortization and monthly payment breakdown ($P\&I$, Property Taxes, Insurance, and HOA) with interactive **Chart.js Donut Chart**.
- **Investor Metrics**: Estimated Monthly Rental Income, Gross Rental Yield %, Net Cap Rate %, and 10-Year Projected Cash-on-Cash Return.

### 3. 🗺️ Interactive Leaflet.js Geospatial Mapping & Amenity Scoring
- Real interactive Leaflet/OpenStreetMap integration centered on the property with street/satellite tiles.
- Custom styled markers for Subject Property and nearby Comparable properties with clickable popups.
- **Neighborhood Amenity Scorecard**: Walk Score (0–100), Transit Score (0–100), School District Rating (0–10), and Price Density ($/sqft).

### 4. ⚖️ Side-by-Side Property Comparison Matrix
- Compare 2 to 4 saved valuations side-by-side in a responsive matrix.
- Metric comparison (Valuation, Price/SqFt, Living Area, Beds/Baths, Year Built, Lot Size, Confidence Score, Estimated 5-Yr Appreciation).

### 5. 📄 Official Client-Ready PDF / Printable Appraisal Dossier
- Generates a branded, multi-page property valuation dossier with official PropValue AI verification seal, specification matrix, comparable market analysis (CMA) table, and analyst signature block.
- 1-click print and PDF save.

### 6. 📁 Bulk / Batch CSV Valuation Engine
- Upload a CSV containing hundreds of properties.
- Vectorized Scikit-Learn pipeline processing in $< 100\text{ms}$.
- Interactive results table with instant **"Download Enriched CSV"** export.
- Downloadable sample CSV template provided.

### 7. 🤖 AI Real Estate Listing Copilot (Natural Language Parser)
- Paste raw listing descriptions from Zillow, Redfin, or MLS agent notes into the smart prompt box.
- AI natural language parser automatically extracts ZIP code, living area, bed/bath counts, build year, garage spaces, and renovation condition, auto-filling the form with field pulse animations.

---

## Architecture Overview

```
House-Price-Predictor/
├── backend/
│   ├── main.py                     # FastAPI backend application (Single, Batch, What-If, AI Parser, Mortgage)
│   ├── train.py                    # Scikit-Learn ColumnTransformer + RandomForest pipeline
│   ├── data/
│   │   ├── dataset.csv             # Housing data (6,000 samples across 12 metro markets)
│   │   └── generate_dataset.py     # Script to generate benchmark dataset
│   ├── model/
│   │   ├── model.joblib            # Serialized fitted pipeline
│   │   └── metadata.json           # Model metadata, version, features, & test metrics
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── index.html                  # Multi-view SPA with all 7 intelligence views & modals
│   ├── styles.css                  # Stitch design tokens, Leaflet styles, and print stylesheet
│   └── app.js                      # Client controller, Chart.js, Leaflet, What-If, & LocalStorage
├── test_e2e.py                     # Automated end-to-end test suite
├── DESIGN.md                       # Google Stitch design system specification
└── README.md                       # Complete documentation & quickstart guide
```

---

## Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Train Model
```bash
python backend/train.py
```

### 3. Start Application
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
```

### 4. Open in Browser
👉 **[http://127.0.0.1:8001](http://127.0.0.1:8001)**

---

## Running Automated Tests

Run the full end-to-end verification suite:
```bash
python test_e2e.py
```
