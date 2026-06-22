import requests
import json
import os

# Load test cases
test_cases_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../test_cases.json"))
with open(test_cases_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Pick TC004 (Clean Approval)
test_case = next(tc for tc in data["test_cases"] if tc["case_id"] == "TC004")
payload = test_case["input"]
if "claims_history" not in payload:
    payload["claims_history"] = []

url = "http://localhost:8000/v1/claims"
headers = {
    "X-API-Key": "super-secret-plum-key",
    "Content-Type": "application/json"
}

print(f"Submitting TC004 to {url}...")
response = requests.post(url, json=payload, headers=headers)

print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(json.dumps(response.json(), indent=2))
