from .base import BaseAgent
from ..models import AgentResult, ClaimSubmission, PolicyConfig, DecisionType


class CaseSummaryAgent(BaseAgent):
    """
    Generates a plain-language, claimant-facing summary of the claim decision.
    Mock mode uses template-based generation; live mode uses LLM.
    """
    
    def run(self, claim: ClaimSubmission, policy: PolicyConfig, context: dict) -> AgentResult:
        decision = context.get("final_decision")
        approved_amount = context.get("approved_amount")
        rejection_reasons = context.get("rejection_reasons", [])
        rationale = context.get("rationale", [])
        notes = context.get("decision_notes", [])
        
        summary = self._generate_template_summary(
            claim, decision, approved_amount, rejection_reasons, rationale, notes
        )
        
        context["human_summary"] = summary
        
        return AgentResult(
            passed=True,
            confidence=1.0,
            notes=[summary]
        )
    
    def _generate_template_summary(
        self, claim, decision, approved_amount, rejection_reasons, rationale, notes
    ) -> str:
        """Template-based summary generation — works in mock mode."""
        category = claim.claim_category.value.replace("_", " ").title()
        
        if decision == DecisionType.APPROVED.value or decision == DecisionType.APPROVED:
            summary = (
                f"Your {category} claim for ₹{claim.claimed_amount:,.0f} "
                f"submitted on {claim.treatment_date} has been approved.\n\n"
            )
            if approved_amount is not None:
                summary += f"Approved amount: ₹{approved_amount:,.0f}\n"
            
            # Add rationale explanations for adjustments (copay, discount)
            adjustment_rationale = [r for r in rationale if r.get("rule_triggered") in ("copay_applied", "network_discount_applied")]
            if adjustment_rationale:
                summary += "\nAdjustments applied:\n"
                for r in adjustment_rationale:
                    summary += f"  • {r.get('human_explanation', r.get('computed_value', ''))}\n"
            
            summary += "\nExpected payout within 3–5 business days to your registered bank account."
            
        elif decision == DecisionType.REJECTED.value or decision == DecisionType.REJECTED:
            summary = (
                f"Your {category} claim for ₹{claim.claimed_amount:,.0f} "
                f"submitted on {claim.treatment_date} has been rejected.\n\n"
            )
            
            # Add rationale explanations
            if rationale:
                summary += "Reason(s):\n"
                for r in rationale:
                    explanation = r.get("human_explanation", "")
                    policy_ref = r.get("policy_reference", "")
                    if explanation:
                        summary += f"  • {explanation}\n"
                    elif policy_ref:
                        summary += f"  • Policy reference: {policy_ref}\n"
            elif rejection_reasons:
                summary += "Reason(s):\n"
                for reason in rejection_reasons:
                    summary += f"  • {reason.replace('_', ' ').title()}\n"
            
            summary += "\nIf you believe this is incorrect, please contact your HR or the insurer directly."
            
        elif decision == DecisionType.PARTIAL.value or decision == DecisionType.PARTIAL:
            summary = (
                f"Your {category} claim for ₹{claim.claimed_amount:,.0f} "
                f"submitted on {claim.treatment_date} has been partially approved.\n\n"
            )
            if approved_amount is not None:
                summary += f"Approved amount: ₹{approved_amount:,.0f}\n"
            
            # Show what was approved and what was rejected
            if rationale:
                excluded = [r for r in rationale if r.get("rule_triggered") == "excluded_line_item"]
                adjustments = [r for r in rationale if r.get("rule_triggered") in ("copay_applied", "network_discount_applied")]
                
                if excluded:
                    summary += "\nNot covered:\n"
                    for r in excluded:
                        summary += f"  • {r.get('human_explanation', r.get('computed_value', ''))}\n"
                
                if adjustments:
                    summary += "\nAdjustments applied:\n"
                    for r in adjustments:
                        summary += f"  • {r.get('human_explanation', r.get('computed_value', ''))}\n"
            
            summary += "\nExpected payout within 3–5 business days to your registered bank account."
            
        elif decision == DecisionType.MANUAL_REVIEW.value or decision == DecisionType.MANUAL_REVIEW:
            summary = (
                f"Your {category} claim for ₹{claim.claimed_amount:,.0f} "
                f"submitted on {claim.treatment_date} has been sent for manual review.\n\n"
                f"A claims handler will review your submission and you will be notified "
                f"of the outcome within 2–3 business days.\n\n"
            )
            if notes:
                summary += "What triggered the review:\n"
                for note in notes[:3]:  # Limit to 3 most relevant notes
                    summary += f"  • {note}\n"
        else:
            summary = (
                f"Your {category} claim for ₹{claim.claimed_amount:,.0f} "
                f"submitted on {claim.treatment_date} is being processed. "
                f"You will be notified of the outcome."
            )
        
        return summary.strip()
