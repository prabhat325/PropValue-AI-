"""
End-to-End Test Suite for PropValue AI.
Tests ML predictions, What-If simulator, Mortgage ROI, listing parser, Batch CSV,
and JWT Authentication with SQLite persistence.
"""

import urllib.request
import urllib.parse
import json
import io

BASE_URL = "http://127.0.0.1:8001"

def test_health():
    url = f"{BASE_URL}/health"
    with urllib.request.urlopen(url) as res:
        assert res.status == 200
        data = json.loads(res.read().decode())
        print(f"[PASS] /health: Model v{data['model_version']}, R² = {data['metrics']['r2_score']}")
        assert data["status"] == "healthy"

def test_what_if():
    url = f"{BASE_URL}/predict-whatif"
    payload = {
        "baseline": {
            "zip_code": "90210",
            "square_footage": 2650,
            "bedrooms": 4,
            "bathrooms": 3.5,
            "year_built": 2008,
            "lot_size_acres": 0.32,
            "property_type": "Single Family",
            "renovation_status": "Minor (Cosmetic)",
            "garage_spaces": 2
        },
        "modified": {
            "zip_code": "90210",
            "square_footage": 3200,
            "bedrooms": 5,
            "bathrooms": 4.5,
            "year_built": 2008,
            "lot_size_acres": 0.32,
            "property_type": "Single Family",
            "renovation_status": "Full Gut Rehab",
            "garage_spaces": 3
        }
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        data = json.loads(res.read().decode())
        print(f"[PASS] /predict-whatif: Baseline = {data['baseline_price_formatted']} -> Modified = {data['modified_price_formatted']}, Delta = {data['delta_formatted']} ({data['delta_percent_formatted']})")
        assert data["delta"] > 0
        assert len(data["contributions"]) > 0

def test_mortgage_calc():
    url = f"{BASE_URL}/mortgage-calc"
    payload = {
        "property_price": 1250000.0,
        "down_payment_percent": 20.0,
        "loan_term_years": 30,
        "interest_rate_percent": 6.85,
        "property_tax_percent": 1.2,
        "home_insurance_annual": 1800.0,
        "hoa_monthly": 150.0
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        data = json.loads(res.read().decode())
        print(f"[PASS] /mortgage-calc: Total Monthly = ${data['monthly_breakdown']['total_monthly']:,.2f}, Gross Yield = {data['investor_metrics']['gross_rental_yield_percent']}%")
        assert data["monthly_breakdown"]["total_monthly"] > 0

def test_parse_listing():
    url = f"{BASE_URL}/parse-listing"
    payload = {
        "text": "Stunning luxury 4 bed 3.5 bath home located in 90210 Beverly Hills with 3400 sqft built in 2012, 3 car garage, minor cosmetic renovations"
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        data = json.loads(res.read().decode())
        feat = data["extracted_features"]
        print(f"[PASS] /parse-listing: Extracted ZIP={feat['zip_code']}, Sqft={feat['square_footage']}, Beds={feat['bedrooms']}")
        assert feat["zip_code"] == "90210"
        assert feat["bedrooms"] == 4

def test_batch_prediction():
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    csv_content = (
        "zip_code,square_footage,bedrooms,bathrooms,year_built\n"
        "90210,3400,4,4.5,2012\n"
        "94102,1850,2,2.0,2005\n"
        "78701,2200,3,2.5,2018\n"
    )
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="test_batch.csv"\r\n'
        f"Content-Type: text/csv\r\n\r\n"
        f"{csv_content}\r\n"
        f"--{boundary}--\r\n"
    ).encode('utf-8')

    url = f"{BASE_URL}/predict-batch"
    req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        data = json.loads(res.read().decode())
        print(f"[PASS] /predict-batch: Processed {data['total_properties']} properties, Avg Price = {data['average_predicted_price_formatted']}")
        assert data["total_properties"] == 3

def test_full_jwt_auth_flow():
    # 1. Login with seeded demo user
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {"email": "prabhat@propvalue.ai", "password": "password123"}
    req = urllib.request.Request(login_url, data=json.dumps(login_payload).encode('utf-8'), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        auth_data = json.loads(res.read().decode())
        token = auth_data["access_token"]
        user = auth_data["user"]
        print(f"[PASS] /auth/login: Authenticated '{user['full_name']}' ({user['role']}) -> JWT Token Issued")
        assert token is not None

    # 2. Get User Profile via Protected GET /auth/me
    me_url = f"{BASE_URL}/auth/me"
    req = urllib.request.Request(me_url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        me_data = json.loads(res.read().decode())
        print(f"[PASS] /auth/me: Verified Protected Session for '{me_data['user']['email']}'")
        assert me_data["user"]["email"] == "prabhat@propvalue.ai"

    # 3. Save Cloud Valuation via POST /auth/saved
    save_url = f"{BASE_URL}/auth/saved"
    save_payload = {
        "title": "Beverly Hills Luxury Estate",
        "property_data": {"zip_code": "90210", "sqft": 3400, "price": 2850000},
        "predicted_price": 2850000.0
    }
    req = urllib.request.Request(save_url, data=json.dumps(save_payload).encode('utf-8'), headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    })
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        save_res = json.loads(res.read().decode())
        saved_id = save_res["id"]
        print(f"[PASS] /auth/saved (POST): Saved Valuation #{saved_id} to Cloud SQLite Database")
        assert saved_id > 0

    # 4. Fetch Cloud Valuations via GET /auth/saved
    get_saved_url = f"{BASE_URL}/auth/saved"
    req = urllib.request.Request(get_saved_url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        list_res = json.loads(res.read().decode())
        print(f"[PASS] /auth/saved (GET): Retrieved {list_res['total']} Cloud-Persisted Valuations")
        assert list_res["total"] >= 1

    # 5. Delete Cloud Valuation via DELETE /auth/saved/{id}
    del_url = f"{BASE_URL}/auth/saved/{saved_id}"
    req = urllib.request.Request(del_url, method="DELETE", headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        del_res = json.loads(res.read().decode())
        print(f"[PASS] /auth/saved (DELETE): Successfully Deleted Valuation #{saved_id}")
        assert del_res["status"] == "success"

if __name__ == "__main__":
    print(f"Running PropValue AI End-to-End Tests on {BASE_URL}...\n")
    test_health()
    test_what_if()
    test_mortgage_calc()
    test_parse_listing()
    test_batch_prediction()
    test_full_jwt_auth_flow()
    print("\nALL TESTS PASSED SUCCESSFULLY!")
