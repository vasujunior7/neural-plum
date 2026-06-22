import pytest
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from src.models import ClaimSubmission
from src.policy.loader import load_policy
from src.agents.supervisor import Supervisor

def load_test_cases():
    test_cases_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../test_cases.json"))
    with open(test_cases_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["test_cases"]

@pytest.fixture
def policy():
    return load_policy()

@pytest.mark.parametrize("case", load_test_cases(), ids=lambda c: c["case_id"])
def test_case_integration(case, policy):
    input_data = case["input"]
    if "claims_history" not in input_data:
        input_data["claims_history"] = []
    if "simulate_component_failure" not in input_data:
        input_data["simulate_component_failure"] = False
        
    claim = ClaimSubmission(**input_data)
    supervisor = Supervisor(policy)
    output = supervisor.process_claim(claim)
    
    expected = case["expected"]
    
    if expected.get("decision"):
        assert output["decision"] == expected["decision"], f"Expected {expected['decision']} but got {output['decision']}"
    else:
        assert output["decision"] is None
        assert output["final_state"] == "VERIFYING"
        
    if "approved_amount" in expected:
        assert output["approved_amount"] == expected["approved_amount"]
        
    if "rejection_reasons" in expected:
        for reason in expected["rejection_reasons"]:
            assert reason in output["rejection_reasons"], f"Expected reason {reason} not in {output['rejection_reasons']}"
