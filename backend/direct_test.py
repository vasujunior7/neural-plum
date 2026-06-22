import json
import os
import sys

# Ensure backend directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import settings
from src.agents.supervisor import Supervisor
from src.models import ClaimSubmission, PolicyConfig

def main():
    test_cases_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../test_cases.json"))
    policy_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../policy_terms.json"))
    
    with open(test_cases_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    with open(policy_path, "r", encoding="utf-8") as f:
        policy_data = json.load(f)

    # Pick TC004 (Clean Approval)
    test_case = next(tc for tc in data["test_cases"] if tc["case_id"] == "TC004")
    payload = test_case["input"]
    if "claims_history" not in payload:
        payload["claims_history"] = []

    print("Running fully integrated backend test on TC004 with REAL Gemini LLM...")
    
    policy_config = PolicyConfig(**policy_data)
    supervisor = Supervisor(policy_config)
    
    # Process the claim
    claim = ClaimSubmission(**payload)
    result = supervisor.process_claim(claim)
    
    print("\n--- FINAL OUTPUT ---")
    print(json.dumps(result, indent=2))
    print("--------------------")
    print(f"\nFinal Decision: {result.get('decision')}")
    print(f"Approved Amount: {result.get('approved_amount')}")
    print(f"Confidence: {result.get('confidence')}")

if __name__ == "__main__":
    main()
