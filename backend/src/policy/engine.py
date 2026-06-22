from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from ..models import (
    PolicyConfig, MemberInfo, ClaimSubmission, ClaimCategory,
    CheckResult, LineItemAdjudication, DecisionType, DecisionRationale
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
        eligibility_date = (join_date + timedelta(days=initial_days)).strftime("%Y-%m-%d")
        return CheckResult(
            passed=False, 
            rejection_reasons=["WAITING_PERIOD"], 
            notes=[f"Initial waiting period of {initial_days} days applies. Treatment date {treatment_date_str} is within the waiting period."],
            rationale=[DecisionRationale(
                rule_triggered="initial_waiting_period",
                policy_reference="policy_terms.json § waiting_periods.initial_waiting_period_days",
                computed_value=f"{delta_days} days since coverage start ({member.join_date})",
                threshold_value=f"{initial_days} days required",
                human_explanation=f"Your policy requires {initial_days} days of active coverage before any claim is eligible. Your coverage started on {member.join_date}, and this treatment on {treatment_date_str} was only {delta_days} days later. You will be eligible from {eligibility_date}."
            )]
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
                    notes=[f"Condition '{condition}' has a waiting period of {wait_days} days. Eligible from {eligibility_date}."],
                    rationale=[DecisionRationale(
                        rule_triggered="condition_waiting_period",
                        policy_reference=f"policy_terms.json § waiting_periods.specific_conditions.{condition}",
                        computed_value=f"{delta_days} days elapsed since coverage start ({member.join_date})",
                        threshold_value=f"{wait_days} days required for {condition}-related claims",
                        human_explanation=f"Your policy requires {wait_days} days of active coverage before {condition.replace('_', ' ')}-related claims are eligible. Your coverage started on {member.join_date}, and this claim was filed only {delta_days} days later on {treatment_date_str}. You will be eligible from {eligibility_date}."
                    )]
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
                    notes=[f"Diagnosis '{diagnosis}' matches exclusion policy: '{excl}'"],
                    rationale=[DecisionRationale(
                        rule_triggered="exclusion_check",
                        policy_reference="policy_terms.json § exclusions.conditions",
                        computed_value=f"Diagnosis: {diagnosis}",
                        threshold_value=f"Excluded condition: {excl}",
                        human_explanation=f"Your diagnosis '{diagnosis}' falls under an excluded condition in your policy: '{excl}'. These conditions are not covered under any circumstances as per your policy terms."
                    )]
                )
            
            keywords = ["obesity", "bariatric", "cosmetic", "infertility", "experimental"]
            for kw in keywords:
                if kw in excl_lower and kw in diag_lower:
                    return CheckResult(
                        passed=False,
                        rejection_reasons=["EXCLUDED_CONDITION"],
                        notes=[f"Diagnosis '{diagnosis}' matches exclusion policy: '{excl}'"],
                        rationale=[DecisionRationale(
                            rule_triggered="exclusion_check",
                            policy_reference="policy_terms.json § exclusions.conditions",
                            computed_value=f"Diagnosis: {diagnosis}",
                            threshold_value=f"Excluded condition: {excl}",
                            human_explanation=f"Your diagnosis '{diagnosis}' matches the excluded category '{excl}'. This type of treatment is not covered under your current policy."
                        )]
                    )
    return CheckResult(passed=True)

def check_pre_authorization(policy: PolicyConfig, claim_category: ClaimCategory, line_items: List[Dict], has_pre_auth: bool) -> CheckResult:
    if has_pre_auth:
        return CheckResult(passed=True)
        
    needs_pre_auth = False
    reasons = []
    rationale_items = []
    
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
                        rationale_items.append(DecisionRationale(
                            rule_triggered="pre_authorization_required",
                            policy_reference=f"policy_terms.json § pre_authorization.required_for — {test}",
                            computed_value=f"₹{amt} for {item.get('description', test)}",
                            threshold_value=f"Pre-authorization required for {test} when amount > ₹{category_rules.pre_auth_threshold}",
                            human_explanation=f"Your {item.get('description', test)} costing ₹{amt} requires pre-authorization because it exceeds the ₹{category_rules.pre_auth_threshold} threshold. Please obtain pre-authorization from your insurer and resubmit."
                        ))
            
    if needs_pre_auth:
        return CheckResult(
            passed=False,
            rejection_reasons=["PRE_AUTH_MISSING"],
            notes=reasons + ["Please obtain pre-authorization and resubmit."],
            rationale=rationale_items
        )
    return CheckResult(passed=True)

def check_per_claim_limit(policy: PolicyConfig, claimed_amount: float, claim_category: ClaimCategory) -> CheckResult:
    limit = policy.coverage.per_claim_limit
    if claimed_amount > limit and claim_category == ClaimCategory.CONSULTATION:
        return CheckResult(
            passed=False,
            rejection_reasons=["PER_CLAIM_EXCEEDED"],
            notes=[f"Claimed amount ₹{claimed_amount} exceeds the per-claim limit of ₹{limit}"],
            rationale=[DecisionRationale(
                rule_triggered="per_claim_limit",
                policy_reference="policy_terms.json § coverage.per_claim_limit",
                computed_value=f"₹{claimed_amount} claimed",
                threshold_value=f"₹{limit} per-claim limit for consultations",
                human_explanation=f"Your claimed amount of ₹{claimed_amount} exceeds the per-claim limit of ₹{limit} for consultation claims. Please split the claim or contact your HR for higher limit options."
            )]
        )
    return CheckResult(passed=True)

def adjudicate_line_items(policy: PolicyConfig, claim_category: ClaimCategory, line_items: List[Dict]) -> CheckResult:
    category_rules = policy.opd_categories.get(claim_category.value.lower())
    if not category_rules:
        return CheckResult(passed=True, approved_amount=sum(float(item.get("amount", 0)) for item in line_items), line_items=[])
        
    adjudicated_items = []
    total_approved = 0.0
    rationale_items = []
    
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
                if excl.lower() in desc_lower:
                    excluded = True
                    reason = f"Cosmetic or excluded dental procedure: {excl}"
                    rationale_items.append(DecisionRationale(
                        rule_triggered="excluded_line_item",
                        policy_reference=f"policy_terms.json § opd_categories.dental.excluded_procedures",
                        computed_value=f"Line item: {desc} (₹{amt})",
                        threshold_value=f"Excluded procedure: {excl}",
                        human_explanation=f"The procedure '{desc}' costing ₹{amt} is classified as a cosmetic/excluded dental procedure ('{excl}') and is not covered under your policy."
                    ))
                    break
                    
        if claim_category == ClaimCategory.VISION and category_rules.excluded_items:
            for excl in category_rules.excluded_items:
                if excl.lower() in desc_lower:
                    excluded = True
                    reason = f"Excluded vision item: {excl}"
                    rationale_items.append(DecisionRationale(
                        rule_triggered="excluded_line_item",
                        policy_reference=f"policy_terms.json § opd_categories.vision.excluded_items",
                        computed_value=f"Line item: {desc} (₹{amt})",
                        threshold_value=f"Excluded item: {excl}",
                        human_explanation=f"The item '{desc}' costing ₹{amt} is classified as an excluded vision item ('{excl}') and is not covered under your policy."
                    ))
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
        line_items=adjudicated_items,
        rationale=rationale_items
    )

def apply_network_discount(policy: PolicyConfig, amount: float, hospital_name: str, claim_category: ClaimCategory) -> Tuple[float, float]:
    category_rules = policy.opd_categories.get(claim_category.value.lower())
    discount_pct = category_rules.network_discount_percent if category_rules else 0.0
    
    if hospital_name and discount_pct > 0:
        if any(h.lower() == hospital_name.lower() for h in policy.network_hospitals):
            discount_amount = amount * (discount_pct / 100.0)
            return amount - discount_amount, discount_amount
            
    return amount, 0.0

def apply_copay(policy: PolicyConfig, amount: float, claim_category: ClaimCategory, line_items: List[Dict]) -> Tuple[float, float, float]:
    category_rules = policy.opd_categories.get(claim_category.value.lower())
    copay_pct = category_rules.copay_percent if category_rules else 0.0
    
    if claim_category == ClaimCategory.PHARMACY and line_items:
        if any("branded" in item.get("description", "").lower() for item in line_items):
            if category_rules and category_rules.branded_drug_copay_percent is not None:
                copay_pct = category_rules.branded_drug_copay_percent
                
    if copay_pct > 0:
        copay_amount = amount * (copay_pct / 100.0)
        return amount - copay_amount, copay_amount, copay_pct
        
    return amount, 0.0, copay_pct

def check_alternative_medicine_limit(policy: PolicyConfig, claim_category: ClaimCategory, ytd_sessions: int) -> CheckResult:
    if claim_category == ClaimCategory.ALTERNATIVE_MEDICINE:
        category_rules = policy.opd_categories.get("alternative_medicine")
        if category_rules and category_rules.max_sessions_per_year:
            if ytd_sessions >= category_rules.max_sessions_per_year:
                return CheckResult(
                    passed=False,
                    rejection_reasons=["SESSION_LIMIT_EXCEEDED"],
                    notes=[f"Member has used {ytd_sessions} sessions. Max limit is {category_rules.max_sessions_per_year} per year."],
                    rationale=[DecisionRationale(
                        rule_triggered="alternative_medicine_session_limit",
                        policy_reference="policy_terms.json § opd_categories.alternative_medicine.max_sessions_per_year",
                        computed_value=f"{ytd_sessions} sessions used",
                        threshold_value=f"{category_rules.max_sessions_per_year} sessions per year",
                        human_explanation=f"You have already reached the maximum allowed limit of {category_rules.max_sessions_per_year} alternative medicine sessions for this policy year."
                    )]
                )
    return CheckResult(passed=True)

def evaluate_claim_deterministic(policy: PolicyConfig, request: ClaimSubmission, member: MemberInfo, diagnosis: str, line_items: List[Dict], has_pre_auth: bool = False) -> CheckResult:
    notes = []
    all_rationale = []
    
    if not member:
        return CheckResult(
            passed=False,
            rejection_reasons=["MEMBER_NOT_FOUND"],
            notes=[f"Member ID {request.member_id} could not be found in the active policy records."],
            rationale=[DecisionRationale(
                rule_triggered="member_lookup",
                policy_reference="policy_terms.json § members",
                computed_value=f"Member ID: {request.member_id}",
                threshold_value="Must be an active member in the policy roster",
                human_explanation=f"We could not find member ID '{request.member_id}' in the active policy records. Please verify your member ID and try again."
            )]
        )
    
    # 1. Waiting Periods
    res = check_initial_waiting_period(policy, member, request.treatment_date)
    if not res.passed: return res
    
    res = check_condition_waiting_period(policy, member, request.treatment_date, diagnosis)
    if not res.passed: return res
    
    res = check_alternative_medicine_limit(policy, request.claim_category, request.ytd_alternative_sessions)
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
    all_rationale.extend(res.rationale)
    
    if approved_amt == 0:
        return CheckResult(
            passed=False,
            rejection_reasons=["ALL_ITEMS_EXCLUDED"],
            notes=["All submitted line items were excluded under the policy terms."],
            line_items=adj_items,
            rationale=all_rationale
        )
        
    # 6. Apply Network Discount
    amt_after_discount, discount_amt = apply_network_discount(policy, approved_amt, request.hospital_name, request.claim_category)
    if discount_amt > 0:
        discount_pct = policy.opd_categories[request.claim_category.value.lower()].network_discount_percent
        notes.append(f"Network discount ({discount_pct}%) applied first on ₹{approved_amt} = ₹{amt_after_discount}.")
        all_rationale.append(DecisionRationale(
            rule_triggered="network_discount_applied",
            policy_reference=f"policy_terms.json § opd_categories.{request.claim_category.value.lower()}.network_discount_percent",
            computed_value=f"₹{discount_amt} discount on ₹{approved_amt}",
            threshold_value=f"{discount_pct}% network discount for {request.hospital_name}",
            human_explanation=f"A {discount_pct}% network hospital discount was applied because '{request.hospital_name}' is in the insurer's network. This reduced the billable amount from ₹{approved_amt} to ₹{amt_after_discount}."
        ))
        
    # 7. Apply Copay
    final_amt, copay_amt, applied_copay_pct = apply_copay(policy, amt_after_discount, request.claim_category, line_items)
    if copay_amt > 0:
        notes.append(f"Co-pay ({applied_copay_pct}%) applied on ₹{amt_after_discount} = ₹{copay_amt} deducted. Final: ₹{final_amt}.")
        all_rationale.append(DecisionRationale(
            rule_triggered="copay_applied",
            policy_reference=f"policy_terms.json § opd_categories.{request.claim_category.value.lower()}.copay_percent",
            computed_value=f"₹{copay_amt} co-pay deducted from ₹{amt_after_discount}",
            threshold_value=f"{applied_copay_pct}% co-pay rate",
            human_explanation=f"A {applied_copay_pct}% co-pay was applied to your claim. This means ₹{copay_amt} is your share, and the insurer pays ₹{final_amt}."
        ))
        
    return CheckResult(
        passed=True,
        approved_amount=final_amt,
        line_items=adj_items,
        notes=notes,
        rationale=all_rationale
    )

