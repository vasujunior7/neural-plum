from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from ..models import (
    PolicyConfig, MemberInfo, ClaimSubmission, ClaimCategory,
    CheckResult, LineItemAdjudication, DecisionType
)

def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")

def check_initial_waiting_period(policy: PolicyConfig, member: MemberInfo, treatment_date_str: str) -> CheckResult:
    if not member.join_date:
        return CheckResult(passed=True)
    
    join_date = parse_date(member.join_date)
    treatment_date = parse_date(treatment_date_str)
    delta_days = (treatment_date - join_date).days
    
    initial_days = policy.waiting_periods.initial_waiting_period_days
    
    if delta_days < initial_days:
        return CheckResult(
            passed=False, 
            rejection_reasons=["WAITING_PERIOD"], 
            notes=[f"Initial waiting period of {initial_days} days applies. Treatment date {treatment_date_str} is within the waiting period."]
        )
    return CheckResult(passed=True)

def check_condition_waiting_period(policy: PolicyConfig, member: MemberInfo, treatment_date_str: str, diagnosis: str) -> CheckResult:
    if not member.join_date or not diagnosis:
        return CheckResult(passed=True)
        
    join_date = parse_date(member.join_date)
    treatment_date = parse_date(treatment_date_str)
    delta_days = (treatment_date - join_date).days
    
    diag_lower = diagnosis.lower()
    import re
    for condition, wait_days in policy.waiting_periods.specific_conditions.items():
        cond_keyword = condition.replace("_", " ")
        if re.search(r'\b' + re.escape(cond_keyword) + r'\b', diag_lower) or (condition == 'diabetes' and 'diabetes' in diag_lower):
            if delta_days < wait_days:
                eligibility_date = (join_date + timedelta(days=wait_days)).strftime("%Y-%m-%d")
                return CheckResult(
                    passed=False,
                    rejection_reasons=["WAITING_PERIOD"],
                    notes=[f"Condition '{condition}' has a waiting period of {wait_days} days. Eligible from {eligibility_date}."]
                )
    return CheckResult(passed=True)

def check_exclusions(policy: PolicyConfig, claim_category: ClaimCategory, diagnosis: str) -> CheckResult:
    if diagnosis:
        diag_lower = diagnosis.lower()
        for excl in policy.exclusions.conditions:
            excl_lower = excl.lower()
            if excl_lower in diag_lower:
                return CheckResult(
                    passed=False,
                    rejection_reasons=["EXCLUDED_CONDITION"],
                    notes=[f"Diagnosis '{diagnosis}' matches exclusion policy: '{excl}'"]
                )
            
            keywords = ["obesity", "bariatric", "cosmetic", "infertility", "experimental"]
            for kw in keywords:
                if kw in excl_lower and kw in diag_lower:
                    return CheckResult(
                        passed=False,
                        rejection_reasons=["EXCLUDED_CONDITION"],
                        notes=[f"Diagnosis '{diagnosis}' matches exclusion policy: '{excl}'"]
                    )
    return CheckResult(passed=True)

def check_pre_authorization(policy: PolicyConfig, claim_category: ClaimCategory, line_items: List[Dict], has_pre_auth: bool) -> CheckResult:
    if has_pre_auth:
        return CheckResult(passed=True)
        
    needs_pre_auth = False
    reasons = []
    
    category_rules = policy.opd_categories.get(claim_category.value.lower())
    if category_rules and category_rules.high_value_tests_requiring_pre_auth:
        for item in line_items:
            desc = item.get("description", "").lower()
            amt = float(item.get("amount", 0))
            
            for test in category_rules.high_value_tests_requiring_pre_auth:
                if test.lower() in desc:
                    if category_rules.pre_auth_threshold and amt > category_rules.pre_auth_threshold:
                        needs_pre_auth = True
                        reasons.append(f"{test} requires pre-authorization when amount > {category_rules.pre_auth_threshold}")
            
    if needs_pre_auth:
        return CheckResult(
            passed=False,
            rejection_reasons=["PRE_AUTH_MISSING"],
            notes=reasons + ["Please obtain pre-authorization and resubmit."]
        )
    return CheckResult(passed=True)

def check_per_claim_limit(policy: PolicyConfig, claimed_amount: float, claim_category: ClaimCategory) -> CheckResult:
    limit = policy.coverage.per_claim_limit
    if claimed_amount > limit and claim_category == ClaimCategory.CONSULTATION:
        return CheckResult(
            passed=False,
            rejection_reasons=["PER_CLAIM_EXCEEDED"],
            notes=[f"Claimed amount ₹{claimed_amount} exceeds the per-claim limit of ₹{limit}"]
        )
    return CheckResult(passed=True)

def adjudicate_line_items(policy: PolicyConfig, claim_category: ClaimCategory, line_items: List[Dict]) -> CheckResult:
    category_rules = policy.opd_categories.get(claim_category.value.lower())
    if not category_rules:
        return CheckResult(passed=True, approved_amount=sum(float(item.get("amount", 0)) for item in line_items), line_items=[])
        
    adjudicated_items = []
    total_approved = 0.0
    
    for item in line_items:
        desc = item.get("description", "")
        amt = float(item.get("amount", 0))
        
        approved = amt
        rejected = 0.0
        reason = None
        
        desc_lower = desc.lower()
        excluded = False
        
        if claim_category == ClaimCategory.DENTAL and category_rules.excluded_procedures:
            for excl in category_rules.excluded_procedures:
                # "teeth whitening" matches "teeth whitening"
                # Handle spaces and parts properly, or simple substring
                if excl.lower() in desc_lower:
                    excluded = True
                    reason = f"Cosmetic or excluded dental procedure: {excl}"
                    break
                    
        if excluded:
            approved = 0.0
            rejected = amt
        else:
            total_approved += approved
            
        adjudicated_items.append(LineItemAdjudication(
            description=desc,
            claimed_amount=amt,
            approved_amount=approved,
            rejected_amount=rejected,
            rejection_reason=reason
        ))
        
    return CheckResult(
        passed=True,
        approved_amount=total_approved,
        line_items=adjudicated_items
    )

def apply_network_discount(policy: PolicyConfig, amount: float, hospital_name: str, claim_category: ClaimCategory) -> Tuple[float, float]:
    category_rules = policy.opd_categories.get(claim_category.value.lower())
    discount_pct = category_rules.network_discount_percent if category_rules else 0.0
    
    if hospital_name and discount_pct > 0:
        if any(h.lower() == hospital_name.lower() for h in policy.network_hospitals):
            discount_amount = amount * (discount_pct / 100.0)
            return amount - discount_amount, discount_amount
            
    return amount, 0.0

def apply_copay(policy: PolicyConfig, amount: float, claim_category: ClaimCategory) -> Tuple[float, float]:
    category_rules = policy.opd_categories.get(claim_category.value.lower())
    copay_pct = category_rules.copay_percent if category_rules else 0.0
    
    if copay_pct > 0:
        copay_amount = amount * (copay_pct / 100.0)
        return amount - copay_amount, copay_amount
        
    return amount, 0.0

def evaluate_claim_deterministic(policy: PolicyConfig, request: ClaimSubmission, member: MemberInfo, diagnosis: str, line_items: List[Dict], has_pre_auth: bool = False) -> CheckResult:
    notes = []
    
    if not member:
        return CheckResult(
            passed=False,
            rejection_reasons=["MEMBER_NOT_FOUND"],
            notes=[f"Member ID {request.member_id} could not be found in the active policy records."]
        )
    
    # 1. Waiting Periods
    res = check_initial_waiting_period(policy, member, request.treatment_date)
    if not res.passed: return res
    
    res = check_condition_waiting_period(policy, member, request.treatment_date, diagnosis)
    if not res.passed: return res
    
    # 2. Exclusions
    res = check_exclusions(policy, request.claim_category, diagnosis)
    if not res.passed: return res
    
    # 3. Pre-auth
    res = check_pre_authorization(policy, request.claim_category, line_items, has_pre_auth)
    if not res.passed: return res
    
    # 4. Per claim limit
    res = check_per_claim_limit(policy, request.claimed_amount, request.claim_category)
    if not res.passed: return res
    
    # 5. Adjudicate line items
    res = adjudicate_line_items(policy, request.claim_category, line_items)
    adj_items = res.line_items
    approved_amt = res.approved_amount
    
    if approved_amt == 0:
        return CheckResult(
            passed=False,
            rejection_reasons=["ALL_ITEMS_EXCLUDED"],
            notes=["All submitted line items were excluded under the policy terms."],
            line_items=adj_items
        )
        
    # 6. Apply Network Discount
    amt_after_discount, discount_amt = apply_network_discount(policy, approved_amt, request.hospital_name, request.claim_category)
    if discount_amt > 0:
        notes.append(f"Network discount ({policy.opd_categories[request.claim_category.value.lower()].network_discount_percent}%) applied first on ₹{approved_amt} = ₹{amt_after_discount}.")
        
    # 7. Apply Copay
    final_amt, copay_amt = apply_copay(policy, amt_after_discount, request.claim_category)
    if copay_amt > 0:
        notes.append(f"Co-pay ({policy.opd_categories[request.claim_category.value.lower()].copay_percent}%) applied on ₹{amt_after_discount} = ₹{copay_amt} deducted. Final: ₹{final_amt}.")
        
    return CheckResult(
        passed=True,
        approved_amount=final_amt,
        line_items=adj_items,
        notes=notes
    )
