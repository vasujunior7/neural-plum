from typing import Dict, Any, List
from ..models import (
    ClaimSubmission, PolicyConfig, ClaimState, DecisionType,
    DecisionRationale
)
from .document_verification import DocumentVerificationAgent
from .document_extraction import DocumentExtractionAgent
from .fraud_detector import FraudDetectorAgent
from .decision import DecisionAgent
from .planner import PlannerAgent
from .semantic_fraud import SemanticFraudAgent
from .case_summary import CaseSummaryAgent
from .handler_checklist import generate_handler_checklist
# pyrefly: ignore [missing-import]
from ..policy.loader import get_member

LOW_CONFIDENCE_THRESHOLD = 0.6

class Supervisor:
    def __init__(self, policy: PolicyConfig):
        self.policy = policy
        self.planner = PlannerAgent()
        self.verification = DocumentVerificationAgent()
        self.extraction = DocumentExtractionAgent()
        self.fraud = FraudDetectorAgent()
        self.semantic_fraud = SemanticFraudAgent()
        self.decision = DecisionAgent()
        self.case_summary = CaseSummaryAgent()
        
    def process_claim(self, claim: ClaimSubmission) -> Dict[str, Any]:
        context = {"member": get_member(claim.member_id)}
        traces = []
        overall_confidence = 1.0
        all_rationale: List[Dict] = []
        
        # 0. Planning — classify claim and decide agent routing
        res_plan = self.planner.execute(claim, self.policy, context)
        traces.append({"state": ClaimState.PLANNING.value, "result": res_plan.model_dump()})
        
        plan = context.get("claim_plan", {})
        agents_to_run = plan.get("agents_to_run", [
            "DocVerification", "Extraction", "FraudCheck", "SemanticFraud", "Decision"
        ])
        
        # 1. Verification (always runs)
        res_verify = self.verification.execute(claim, self.policy, context)
        traces.append({"state": ClaimState.VERIFYING.value, "result": res_verify.model_dump()})
        overall_confidence *= res_verify.confidence
        if not res_verify.passed:
            return self._finalize(
                ClaimState.VERIFYING, None,
                res_verify.rejection_reasons, res_verify.notes,
                traces, overall_confidence, context=context,
                rationale=[r.model_dump() for r in res_verify.rationale]
            )
            
        # 2. Extraction (always runs, now with per-field confidence)
        res_extract = self.extraction.execute(claim, self.policy, context)
        traces.append({"state": ClaimState.EXTRACTING.value, "result": res_extract.model_dump()})
        overall_confidence *= res_extract.confidence
        
        if not res_extract.passed:
            return self._finalize(
                ClaimState.EXTRACTING, DecisionType.MANUAL_REVIEW,
                res_extract.rejection_reasons, res_extract.notes,
                traces, overall_confidence, context=context,
                rationale=[r.model_dump() for r in res_extract.rationale]
            )
        
        # 2.5 Confidence routing — check per-field confidence
        field_confidences = context.get("field_confidences", {})
        uncertain_fields = [
            f for f, data in field_confidences.items()
            if data.get("confidence", 1.0) < LOW_CONFIDENCE_THRESHOLD
        ]
        
        if len(uncertain_fields) > 2:
            overall_confidence *= 0.5
            return self._finalize(
                ClaimState.EXTRACTING, DecisionType.MANUAL_REVIEW,
                [f"Low confidence on fields: {', '.join(uncertain_fields)}"],
                ["Multiple fields have uncertain extraction. Please re-upload clearer documents or verify the flagged fields."],
                traces, overall_confidence, context=context
            )
        elif len(uncertain_fields) > 0:
            overall_confidence -= 0.1 * len(uncertain_fields)
            
        # 3. Fraud Check (conditional — based on planner)
        if "FraudCheck" in agents_to_run:
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
                return self._finalize(
                    ClaimState.FRAUD_CHECKING, DecisionType.MANUAL_REVIEW,
                    res_fraud.rejection_reasons, res_fraud.notes,
                    traces, overall_confidence, context=context,
                    rationale=[r.model_dump() for r in res_fraud.rationale]
                )
        else:
            skip_reason = plan.get("agents_to_skip", {}).get("FraudCheck", "Skipped by planner")
            traces.append({"state": ClaimState.FRAUD_CHECKING.value, "result": {
                "passed": True, "confidence": 1.0,
                "notes": [f"Skipped: {skip_reason}"],
                "rejection_reasons": []
            }})
        
        # 3.5 Semantic Fraud (conditional — based on planner)
        if "SemanticFraud" in agents_to_run:
            res_semantic = self.semantic_fraud.execute(claim, self.policy, context)
            traces.append({"state": ClaimState.SEMANTIC_FRAUD.value, "result": res_semantic.model_dump()})
            if not res_semantic.passed:
                # Advisory only — reduce confidence but don't block
                overall_confidence *= res_semantic.confidence
        else:
            skip_reason = plan.get("agents_to_skip", {}).get("SemanticFraud", "Skipped by planner")
            traces.append({"state": ClaimState.SEMANTIC_FRAUD.value, "result": {
                "passed": True, "confidence": 1.0,
                "notes": [f"Skipped: {skip_reason}"],
                "rejection_reasons": []
            }})
            # Set empty semantic fraud result for downstream use
            from ..models import SemanticFraudResult
            context.setdefault("semantic_fraud_result", SemanticFraudResult().model_dump())
            
        # 4. Decision
        res_decide = self.decision.execute(claim, self.policy, context)
        traces.append({"state": ClaimState.DECIDING.value, "result": res_decide.model_dump()})
        overall_confidence *= res_decide.confidence
        all_rationale = [r.model_dump() for r in res_decide.rationale]
            
        decision = res_decide.decision if res_decide.decision else (
            DecisionType.APPROVED if res_decide.passed else DecisionType.REJECTED
        )
        
        if overall_confidence < 0.6 and decision != DecisionType.REJECTED:
            decision = DecisionType.MANUAL_REVIEW
            res_decide.notes.append("Routed to manual review due to low system confidence.")
        
        # 5. Case Summary
        context["final_decision"] = decision.value if isinstance(decision, DecisionType) else decision
        context["approved_amount"] = res_decide.approved_amount
        context["rejection_reasons"] = res_decide.rejection_reasons
        context["rationale"] = all_rationale
        context["decision_notes"] = res_decide.notes
        
        res_summary = self.case_summary.execute(claim, self.policy, context)
        traces.append({"state": ClaimState.SUMMARIZING.value, "result": res_summary.model_dump()})
        
        human_summary = context.get("human_summary", "")
        
        # 6. Handler Checklist (only for MANUAL_REVIEW)
        handler_checklist = None
        if decision == DecisionType.MANUAL_REVIEW:
            checklist = generate_handler_checklist(
                context,
                decision_notes=res_decide.notes,
                rejection_reasons=res_decide.rejection_reasons
            )
            handler_checklist = checklist.model_dump()
            
        return self._finalize(
            ClaimState.DONE, 
            decision, 
            res_decide.rejection_reasons, 
            res_decide.notes, 
            traces, 
            overall_confidence, 
            res_decide.approved_amount,
            context=context,
            rationale=all_rationale,
            human_summary=human_summary,
            handler_checklist=handler_checklist
        )
        
    def _finalize(self, state, decision, reasons, notes, traces, confidence,
                  approved_amount=None, context=None, rationale=None,
                  human_summary=None, handler_checklist=None):
        result = {
            "final_state": state.value,
            "decision": decision.value if decision else None,
            "rejection_reasons": reasons,
            "notes": notes,
            "approved_amount": approved_amount,
            "confidence": max(confidence, 0.15),
            "traces": traces,
            "rationale": rationale or [],
            "field_confidences": (context or {}).get("field_confidences", {}),
            "semantic_fraud_result": (context or {}).get("semantic_fraud_result", {}),
            "claim_plan": (context or {}).get("claim_plan", {}),
            "human_summary": human_summary or "",
            "handler_checklist": handler_checklist,
        }
        return result

