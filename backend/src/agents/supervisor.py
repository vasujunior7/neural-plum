from typing import Dict, Any
from ..models import ClaimSubmission, PolicyConfig, ClaimState, DecisionType
from .document_verification import DocumentVerificationAgent
from .document_extraction import DocumentExtractionAgent
from .fraud_detector import FraudDetectorAgent
from .decision import DecisionAgent
# pyrefly: ignore [missing-import]
from ..policy.loader import get_member
# pyrefly: ignore [missing-import]
from langfuse.decorators import observe, langfuse_context

class Supervisor:
    def __init__(self, policy: PolicyConfig):
        self.policy = policy
        self.verification = DocumentVerificationAgent()
        self.extraction = DocumentExtractionAgent()
        self.fraud = FraudDetectorAgent()
        self.decision = DecisionAgent()
        
    @observe(name="supervisor_process_claim")
    def process_claim(self, claim: ClaimSubmission) -> Dict[str, Any]:
        langfuse_context.update_current_observation(
            input=claim.model_dump(),
            metadata={"member_id": claim.member_id}
        )
        context = {"member": get_member(claim.member_id)}
        traces = []
        overall_confidence = 1.0
        
        # 1. Verification
        res_verify = self.verification.execute(claim, self.policy, context)
        traces.append({"state": ClaimState.VERIFYING.value, "result": res_verify.model_dump()})
        overall_confidence *= res_verify.confidence
        if not res_verify.passed:
            return self._finalize(ClaimState.VERIFYING, None, res_verify.rejection_reasons, res_verify.notes, traces, overall_confidence)
            
        # 2. Extraction
        res_extract = self.extraction.execute(claim, self.policy, context)
        traces.append({"state": ClaimState.EXTRACTING.value, "result": res_extract.model_dump()})
        overall_confidence *= res_extract.confidence
        if not res_extract.passed:
            return self._finalize(ClaimState.EXTRACTING, DecisionType.MANUAL_REVIEW, res_extract.rejection_reasons, res_extract.notes, traces, overall_confidence)
            
        # 3. Fraud Check
        try:
            if getattr(claim, "simulate_component_failure", False):
                raise Exception("Simulated Fraud API timeout")
            res_fraud = self.fraud.execute(claim, self.policy, context)
            traces.append({"state": ClaimState.FRAUD_CHECKING.value, "result": res_fraud.model_dump()})
            overall_confidence *= res_fraud.confidence
        except Exception as e:
            from ..models import AgentResult
            import logging
            logging.error(f"Fraud component failed: {e}")
            res_fraud = AgentResult(
                passed=True, 
                confidence=0.8, 
                notes=[f"Fraud checking bypassed due to failure: {e}"]
            )
            traces.append({"state": ClaimState.FRAUD_CHECKING.value, "result": res_fraud.model_dump()})
            overall_confidence *= res_fraud.confidence
            
        if not res_fraud.passed and "MANUAL_REVIEW" in res_fraud.rejection_reasons:
            return self._finalize(ClaimState.FRAUD_CHECKING, DecisionType.MANUAL_REVIEW, res_fraud.rejection_reasons, res_fraud.notes, traces, overall_confidence)
            
        # 4. Decision
        res_decide = self.decision.execute(claim, self.policy, context)
        traces.append({"state": ClaimState.DECIDING.value, "result": res_decide.model_dump()})
        overall_confidence *= res_decide.confidence
            
        decision = res_decide.decision if res_decide.decision else (DecisionType.APPROVED if res_decide.passed else DecisionType.REJECTED)
        
        if overall_confidence < 0.6 and decision != DecisionType.REJECTED:
            decision = DecisionType.MANUAL_REVIEW
            res_decide.notes.append("Routed to manual review due to low system confidence.")
            
        return self._finalize(
            ClaimState.DONE, 
            decision, 
            res_decide.rejection_reasons, 
            res_decide.notes, 
            traces, 
            overall_confidence, 
            res_decide.approved_amount
        )
        
    def _finalize(self, state, decision, reasons, notes, traces, confidence, approved_amount=None):
        result = {
            "final_state": state.value,
            "decision": decision.value if decision else None,
            "rejection_reasons": reasons,
            "notes": notes,
            "approved_amount": approved_amount,
            "confidence": max(confidence, 0.15),
            "traces": traces
        }
        langfuse_context.update_current_observation(
            output=result,
            level="ERROR" if decision == DecisionType.REJECTED else "DEFAULT"
        )
        return result
