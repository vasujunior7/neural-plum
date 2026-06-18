from .base import BaseAgent
from ..models import AgentResult, ClaimSubmission, PolicyConfig, DecisionType
from ..policy.engine import evaluate_claim_deterministic

class DecisionAgent(BaseAgent):
    def run(self, claim: ClaimSubmission, policy: PolicyConfig, context: dict) -> AgentResult:
        member = context.get("member")
        extracted_data = context.get("extracted_data", {})
        
        res = evaluate_claim_deterministic(
            policy=policy,
            request=claim,
            member=member,
            diagnosis=extracted_data.get("diagnosis"),
            line_items=extracted_data.get("line_items", []),
            has_pre_auth=extracted_data.get("has_pre_auth", False)
        )
        
        decision = DecisionType.REJECTED
        if res.passed:
            any_rejected = any(item.rejected_amount > 0 for item in res.line_items)
            if any_rejected:
                decision = DecisionType.PARTIAL
            else:
                decision = DecisionType.APPROVED
                
        return AgentResult(
            passed=res.passed,
            confidence=1.0,
            notes=res.notes,
            rejection_reasons=res.rejection_reasons,
            decision=decision,
            approved_amount=res.approved_amount
        )
