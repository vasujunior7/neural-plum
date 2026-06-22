import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from src.models import ClaimSubmission, ClaimCategory, MemberInfo
from src.policy.loader import load_policy
from src.policy.engine import (
    evaluate_claim_deterministic
)

@pytest.fixture
def policy():
    return load_policy()

def test_tc004_clean_consultation(policy):
    member = MemberInfo(member_id="EMP001", name="Rajesh Kumar", date_of_birth="1985-03-15", gender="M", relationship="SELF", join_date="2024-04-01")
    request = ClaimSubmission(
        member_id="EMP001", policy_id="PLUM_GHI_2024", claim_category=ClaimCategory.CONSULTATION,
        treatment_date="2024-11-01", claimed_amount=1500, documents=[]
    )
    line_items = [
        {"description": "Consultation Fee", "amount": 1000},
        {"description": "CBC Test", "amount": 300},
        {"description": "Dengue NS1 Test", "amount": 200}
    ]
    res = evaluate_claim_deterministic(policy, request, member, "Viral Fever", line_items, False)
    assert res.passed
    assert res.approved_amount == 1350.0 
    assert any("Co-pay" in n for n in res.notes)

def test_tc005_waiting_period_diabetes(policy):
    member = MemberInfo(member_id="EMP005", name="Vikram Joshi", date_of_birth="1979-09-10", gender="M", relationship="SELF", join_date="2024-09-01")
    request = ClaimSubmission(
        member_id="EMP005", policy_id="PLUM_GHI_2024", claim_category=ClaimCategory.CONSULTATION,
        treatment_date="2024-10-15", claimed_amount=3000, documents=[]
    )
    res = evaluate_claim_deterministic(policy, request, member, "Type 2 Diabetes Mellitus", [], False)
    assert not res.passed
    assert "WAITING_PERIOD" in res.rejection_reasons

def test_tc006_dental_partial_approval(policy):
    member = MemberInfo(member_id="EMP002", name="Priya Singh", date_of_birth="1990-07-22", gender="F", relationship="SELF", join_date="2024-04-01")
    request = ClaimSubmission(
        member_id="EMP002", policy_id="PLUM_GHI_2024", claim_category=ClaimCategory.DENTAL,
        treatment_date="2024-10-15", claimed_amount=12000, documents=[]
    )
    line_items = [
        {"description": "Root Canal Treatment", "amount": 8000},
        {"description": "Teeth Whitening", "amount": 4000}
    ]
    res = evaluate_claim_deterministic(policy, request, member, "Dental pain", line_items, False)
    assert res.passed
    assert res.approved_amount == 8000.0
    assert len(res.line_items) == 2
    assert res.line_items[1].rejected_amount == 4000.0

def test_tc007_mri_without_pre_auth(policy):
    member = MemberInfo(member_id="EMP007", name="Suresh Patil", date_of_birth="1975-12-30", gender="M", relationship="SELF", join_date="2024-04-01")
    request = ClaimSubmission(
        member_id="EMP007", policy_id="PLUM_GHI_2024", claim_category=ClaimCategory.DIAGNOSTIC,
        treatment_date="2024-11-02", claimed_amount=15000, documents=[]
    )
    line_items = [
        {"description": "MRI Lumbar Spine", "amount": 15000}
    ]
    res = evaluate_claim_deterministic(policy, request, member, "Suspected Lumbar Disc Herniation", line_items, False)
    assert not res.passed
    assert "PRE_AUTH_MISSING" in res.rejection_reasons

def test_tc008_per_claim_limit(policy):
    member = MemberInfo(member_id="EMP003", name="Amit Verma", date_of_birth="1988-11-05", gender="M", relationship="SELF", join_date="2024-04-01")
    request = ClaimSubmission(
        member_id="EMP003", policy_id="PLUM_GHI_2024", claim_category=ClaimCategory.CONSULTATION,
        treatment_date="2024-10-20", claimed_amount=7500, documents=[]
    )
    res = evaluate_claim_deterministic(policy, request, member, "Gastroenteritis", [], False)
    assert not res.passed
    assert "PER_CLAIM_EXCEEDED" in res.rejection_reasons

def test_tc010_network_discount(policy):
    member = MemberInfo(member_id="EMP010", name="Deepak Shah", date_of_birth="1980-01-07", gender="M", relationship="SELF", join_date="2024-04-01")
    request = ClaimSubmission(
        member_id="EMP010", policy_id="PLUM_GHI_2024", claim_category=ClaimCategory.CONSULTATION,
        treatment_date="2024-11-03", claimed_amount=4500, hospital_name="Apollo Hospitals", documents=[]
    )
    line_items = [
        {"description": "Consultation Fee", "amount": 1500},
        {"description": "Medicines", "amount": 3000}
    ]
    res = evaluate_claim_deterministic(policy, request, member, "Acute Bronchitis", line_items, False)
    assert res.passed
    assert res.approved_amount == 3240.0

def test_tc012_excluded_treatment(policy):
    member = MemberInfo(member_id="EMP009", name="Anita Desai", date_of_birth="1993-08-25", gender="F", relationship="SELF", join_date="2024-04-01")
    request = ClaimSubmission(
        member_id="EMP009", policy_id="PLUM_GHI_2024", claim_category=ClaimCategory.CONSULTATION,
        treatment_date="2024-10-18", claimed_amount=8000, documents=[]
    )
    res = evaluate_claim_deterministic(policy, request, member, "Morbid Obesity - BMI 37", [], False)
    assert not res.passed
    assert "EXCLUDED_CONDITION" in res.rejection_reasons
