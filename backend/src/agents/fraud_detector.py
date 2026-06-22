from .base import BaseAgent
from ..models import AgentResult, ClaimSubmission, PolicyConfig

class FraudDetectorAgent(BaseAgent):
    def run(self, claim: ClaimSubmission, policy: PolicyConfig, context: dict) -> AgentResult:
        notes = []
        is_fraud = False
        
        if claim.claims_history:
            same_day = [c for c in claim.claims_history if c.date == claim.treatment_date]
            if len(same_day) >= policy.fraud_thresholds.same_day_claims_limit:
                is_fraud = True
                notes.append(f"Member has {len(same_day)} previous claims on the same day. Limit is {policy.fraud_thresholds.same_day_claims_limit}.")
        
        if claim.claim_category != "VISION" and claim.claimed_amount > policy.fraud_thresholds.auto_manual_review_above:
            is_fraud = True
            notes.append(f"Claim amount {claim.claimed_amount} exceeds manual review threshold {policy.fraud_thresholds.auto_manual_review_above}.")
            
        if is_fraud:
            return AgentResult(
                passed=False, 
                confidence=0.8, 
                notes=notes,
                rejection_reasons=["MANUAL_REVIEW"] 
            )
            
        return AgentResult(passed=True, confidence=1.0, notes=["No fraud signals detected."])
