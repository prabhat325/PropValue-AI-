# 🏠 PropValue AI

### AI-Powered Real Estate Price Prediction & Analysis

PropValue AI is an end-to-end machine learning application that predicts residential property prices based on property characteristics such as location, area, bedrooms, bathrooms, year built, garage spaces, and renovation status.

The project combines a **Scikit-learn machine learning pipeline**, **FastAPI backend**, and **interactive web frontend** to demonstrate how a machine learning model can be integrated into a real-world application.

---

## ✨ Features

### 🏠 Property Price Prediction

Enter property details and get an estimated market value using a trained Random Forest regression model.

### 📊 What-If Analysis

Experiment with property characteristics such as:

* Square footage
* Bedrooms
* Bathrooms
* Garage spaces
* Renovation status

and see how changes can affect the estimated property value.

### 💰 Mortgage & ROI Calculator

Calculate:

* Monthly mortgage payment
* Principal & interest
* Property taxes
* Home insurance
* HOA fees
* Rental yield
* Cap rate
* Projected investment returns

### 🗺️ Property & Market Map

Visualize properties and comparable properties using an interactive map.

### ⚖️ Property Comparison

Compare multiple properties based on:

* Estimated price
* Price per square foot
* Living area
* Bedrooms & bathrooms
* Model confidence
* Projected growth

### 📄 Valuation Report

Generate a structured property valuation report containing property information and valuation insights.

### 📁 Bulk Property Valuation

Upload multiple properties through a CSV file and generate predictions for the entire dataset.

### 🤖 Listing Parser

Paste a natural-language property listing and automatically extract relevant information such as:

* ZIP code
* Square footage
* Bedrooms
* Bathrooms
* Year built
* Renovation status

---

## 🧠 Machine Learning

The prediction engine uses a **Scikit-learn Pipeline** with a `ColumnTransformer`.

### Numerical Features

* `square_footage`
* `bedrooms`
* `bathrooms`
* `year_built`
* `lot_size_acres`
* `garage_spaces`

Numerical data is processed using:

```text
Median Imputation
       ↓
StandardScaler
```

### Categorical Features

* `zip_code`
* `property_type`
* `renovation_status`

Categorical data is processed using:

```text
Most-Frequent Imputation
       ↓
OneHotEncoder
```

The processed features are then passed to a **RandomForestRegressor**.

The complete preprocessing + model pipeline is saved using **Joblib**, allowing the same transformations to be applied during prediction.

---

## 📈 Model Performance

The current project documentation reports the following test results:

| Metric        |       Score |
| ------------- | ----------: |
| R² Score      |      0.9799 |
| MAE           |  $67,836.70 |
| RMSE          | $104,064.56 |
| MAPE          |       6.08% |
| API Inference |     < 15 ms |

> These metrics should be considered valid only after reproducing the training and evaluation process on the current dataset.

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │      Frontend       │
                    │   Web Application   │
                    └──────────┬──────────┘
                               │
                               │ REST API
                               ▼
                    ┌─────────────────────┐
                    │       FastAPI       │
                    │      Backend        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  ML Preprocessing   │
                    │  ColumnTransformer  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Random Forest Model │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Predicted Property  │
                    │        Value        │
                    └─────────────────────┘
```

---

## 🛠️ Tech Stack

### Machine Learning

* Python
* Scikit-learn
* Pandas
* NumPy
* Joblib

### Backend

* FastAPI
* Uvicorn
* SQLite
* JWT Authentication

### Frontend

* HTML / CSS / JavaScript or project frontend framework
* Tailwind CSS
* Chart.js
* Leaflet.js

### Development

* Git
* GitHub
* VS Code

---

## 📂 Project Structure

```text
PropValue-AI/
│
├── backend/
│   ├── main.py
│   ├── train.py
│   ├── requirements.txt
│   ├── data/
│   │   └── dataset.csv
│   └── model/
│       └── model.joblib
│
├── frontend/
│   └── ...
│
├── test_e2e.py
├── README.md
└── .gitignore
```

> The exact frontend structure may vary depending on the implementation.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd PropValue-AI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Train the model

```bash
python backend/train.py
```

This generates the trained model:

```text
backend/model/model.joblib
```

### 5. Start the FastAPI server

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
```

### 6. Open the application

```text
http://127.0.0.1:8001
```

---

## 🔌 API Endpoints

| Method   | Endpoint          | Purpose                                 |
| -------- | ----------------- | --------------------------------------- |
| GET      | `/health`         | Check API and model status              |
| POST     | `/predict`        | Predict property value                  |
| POST     | `/predict-whatif` | Perform What-If analysis                |
| POST     | `/mortgage-calc`  | Calculate mortgage & investment metrics |
| POST     | `/predict-batch`  | Process multiple properties             |
| POST     | `/parse-listing`  | Extract property information from text  |
| POST     | `/auth/register`  | Register a user                         |
| POST     | `/auth/login`     | Authenticate a user                     |
| GET      | `/auth/me`        | Get current user information            |
| GET/POST | `/auth/saved`     | Manage saved valuations                 |

---

## 🔐 Authentication

PropValue AI includes user authentication using:

* JWT-based sessions
* PBKDF2-SHA256 password hashing
* SQLite persistence
* Protected API routes

Passwords are stored as hashes rather than plain text.

---

## 🧪 Testing

The project includes an end-to-end test suite covering the major application workflows.

Run:

```bash
python test_e2e.py
```

The tests cover areas including:

* API health
* Model inference
* What-If predictions
* Mortgage calculations
* Listing parsing
* Bulk CSV processing
* Authentication

---

## 📊 ML Workflow

```text
Dataset
   ↓
Data Cleaning
   ↓
Train / Test Split
   ↓
Feature Preprocessing
   ↓
ColumnTransformer
   ├── Numerical → Imputation → Scaling
   └── Categorical → Imputation → One-Hot Encoding
   ↓
Random Forest Regressor
   ↓
Model Evaluation
   ↓
Joblib Serialization
   ↓
FastAPI Prediction API
   ↓
Frontend
```

---

## 🎯 Learning Goals

This project was built to understand how to take a machine learning model beyond a Jupyter Notebook and integrate it into a complete application.

The main concepts demonstrated are:

* Regression
* Feature preprocessing
* Handling numerical and categorical data
* Scikit-learn Pipelines
* Model evaluation
* Model serialization
* REST API development
* Frontend-backend integration
* Authentication
* Data visualization
* ML model deployment concepts

---

## 🔮 Future Improvements

Some possible improvements include:

* Compare additional regression algorithms
* Hyperparameter optimization
* Cross-validation and stronger model validation
* Explainable AI using SHAP
* Better uncertainty / prediction intervals
* Real-world housing datasets
* Cloud deployment
* Database migration from SQLite to PostgreSQL
* Automated model retraining
* More advanced geospatial features

---

## 👨‍💻 Author

**Prabhat Dubey**

PropValue AI was developed as a project to explore the complete workflow of building, evaluating, and deploying a machine learning application.

---

## ⚠️ Disclaimer

PropValue AI provides **machine-learning-based estimates** and should not be treated as a certified property appraisal, financial advice, or an official market valuation.

Actual property prices can vary based on factors that may not be represented in the dataset or model.

