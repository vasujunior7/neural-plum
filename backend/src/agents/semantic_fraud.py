from .base import BaseAgent
from ..models import (
    AgentResult, ClaimSubmission, PolicyConfig,
    SemanticFraudResult, FraudFlag
)
from ..config import settings


# Typical procedure costs in INR for Indian hospitals (Tier 1/2 cities)
TYPICAL_COSTS = {
    "consultation": (300, 2000),
    "mri": (5000, 20000),
    "ct scan": (3000, 15000),
    "x-ray": (300, 2000),
    "blood test": (200, 2000),
    "cbc": (200, 800),
    "ultrasound": (800, 3000),
    "ecg": (300, 1000),
    "root canal": (3000, 15000),
    "tooth extraction": (500, 3000),
    "dental filling": (500, 3000),
}

# Diagnosis-procedure compatibility mapping
DIAGNOSIS_PROCEDURE_MAP = {
    "cold": ["consultation", "blood test", "cbc"],
    "common cold": ["consultation", "blood test", "cbc"],
    "fever": ["consultation", "blood test", "cbc", "x-ray"],
    "viral fever": ["consultation", "blood test", "cbc", "x-ray"],
    "pneumonia": ["consultation", "x-ray", "blood test", "ct scan"],
    "fracture": ["x-ray", "consultation", "ct scan", "mri"],
    "dental pain": ["root canal", "tooth extraction", "dental filling", "x-ray"],
    "back pain": ["consultation", "mri", "x-ray", "physiotherapy"],
    "headache": ["consultation", "ct scan", "mri"],
}


class SemanticFraudAgent(BaseAgent):
    """
    Advisory-only semantic fraud reasoning agent.
    Analyzes extracted claim data for cross-field inconsistencies.
    Never auto-rejects — only raises MANUAL_REVIEW probability.
    """
    
    def run(self, claim: ClaimSubmission, policy: PolicyConfig, context: dict) -> AgentResult:
        extracted_data = context.get("extracted_data", {})
        
        if not settings.MOCK_EXTRACTION:
            return self._run_llm_analysis(claim, extracted_data, context)
        
        return self._run_deterministic_analysis(claim, extracted_data, policy, context)
    
    def _run_deterministic_analysis(
        self, claim: ClaimSubmission, extracted_data: dict, policy: PolicyConfig, context: dict
    ) -> AgentResult:
        """Mock-mode deterministic fraud analysis using rules."""
        flags = []
        fraud_score = 0.0
        
        diagnosis = (extracted_data.get("diagnosis") or "").lower()
        line_items = extracted_data.get("line_items", [])
        
        # Check 1: Procedure-diagnosis mismatch
        if diagnosis:
            compatible_procedures = set()
            for diag_key, procs in DIAGNOSIS_PROCEDURE_MAP.items():
                if diag_key in diagnosis:
                    compatible_procedures.update(procs)
            
            if compatible_procedures:
                for item in line_items:
                    desc_lower = item.get("description", "").lower()
                    is_compatible = any(proc in desc_lower for proc in compatible_procedures)
                    if not is_compatible and desc_lower:
                        # Check if it's a high-cost procedure mismatched with a minor diagnosis
                        high_cost_procs = ["mri", "ct scan", "pet scan", "surgery"]
                        is_high_cost = any(p in desc_lower for p in high_cost_procs)
                        minor_diagnoses = ["cold", "common cold", "headache", "viral fever"]
                        is_minor = any(d in diagnosis for d in minor_diagnoses)
                        
                        if is_high_cost and is_minor:
                            fraud_score += 0.3
                            flags.append(FraudFlag(
                                signal=f"High-cost procedure '{item.get('description')}' is inconsistent with minor diagnosis '{diagnosis}'",
                                severity="high",
                                fields_involved=["diagnosis", "line_items"]
                            ))
        
        # Check 2: Amount outlier detection
        for item in line_items:
            desc_lower = item.get("description", "").lower()
            amt = float(item.get("amount", 0))
            
            for proc_name, (low, high) in TYPICAL_COSTS.items():
                if proc_name in desc_lower:
                    if amt > high * 2:
                        fraud_score += 0.2
                        flags.append(FraudFlag(
                            signal=f"Amount ₹{amt} for '{item.get('description')}' is significantly above typical range (₹{low}-₹{high})",
                            severity="medium",
                            fields_involved=["line_items"]
                        ))
                    break
        
        # Check 3: Weekend/holiday admission for elective procedures
        from datetime import datetime
        try:
            treatment_date = datetime.strptime(claim.treatment_date, "%Y-%m-%d")
            if treatment_date.weekday() >= 5:  # Saturday or Sunday
                elective_keywords = ["mri", "ct scan", "pet scan", "elective", "cosmetic"]
                for item in line_items:
                    desc_lower = item.get("description", "").lower()
                    if any(kw in desc_lower for kw in elective_keywords):
                        fraud_score += 0.1
                        flags.append(FraudFlag(
                            signal=f"Elective procedure '{item.get('description')}' on a weekend ({treatment_date.strftime('%A')}) is unusual",
                            severity="low",
                            fields_involved=["treatment_date", "line_items"]
                        ))
                        break
        except ValueError:
            pass
        
        # Cap fraud score at 1.0
        fraud_score = min(fraud_score, 1.0)
        
        # Determine recommendation
        if fraud_score > 0.8:
            recommendation = "MANUAL_REVIEW"
        elif fraud_score > 0.5:
            recommendation = "MANUAL_REVIEW"
        else:
            recommendation = "APPROVE"
        
        # Store result in context for downstream use
        fraud_result = SemanticFraudResult(
            fraud_score=fraud_score,
            flags=flags,
            recommendation=recommendation
        )
        # pyre-ignore[reportMissingImports]
        context["semantic_fraud_result"] = fraud_result.model_dump()
        
        passed = recommendation != "MANUAL_REVIEW"
        notes = [f"Semantic fraud score: {fraud_score:.2f} — {'Low risk' if fraud_score < 0.3 else 'Elevated risk' if fraud_score < 0.7 else 'High risk'}"]
        if flags:
            for f in flags:
                notes.append(f"⚠ Flag ({f.severity}): {f.signal}")
        else:
            notes.append("No significant anomalies detected.")
        
        return AgentResult(
            passed=passed,
            confidence=1.0 - (fraud_score * 0.3),
            notes=notes
        )
    
    def _run_llm_analysis(
        self, claim: ClaimSubmission, extracted_data: dict, context: dict
    ) -> AgentResult:
        """Live-mode LLM-powered semantic fraud analysis."""
        try:
            from ..llm.client import LLMClient
            import json
            
            client = LLMClient()
            
            claim_json = json.dumps({
                "member_id": claim.member_id,
                "claim_category": claim.claim_category.value,
                "treatment_date": claim.treatment_date,
                "claimed_amount": claim.claimed_amount,
                "hospital_name": claim.hospital_name,
                "diagnosis": extracted_data.get("diagnosis"),
                "line_items": extracted_data.get("line_items", []),
            }, indent=2)
            
            prompt = f"""You are an insurance fraud analyst reviewing a health insurance claim in India.
Analyze the following structured claim data and identify semantic red flags.

Claim data:
{claim_json}

Check for:
1. Procedure-diagnosis mismatch (e.g., MRI billed for a cold)
2. Amount outliers vs. typical Indian hospital rates for this procedure
3. Admission/discharge date inconsistencies
4. Doctor credentials mismatched with procedure type
5. Hospital name inconsistencies across documents

Return a JSON object with fraud_score (0.0-1.0), flags (list of objects with signal, severity, fields_involved), and recommendation (APPROVE or MANUAL_REVIEW).
"""
            
            result = client.generate_structured(prompt, SemanticFraudResult)
            context["semantic_fraud_result"] = result.model_dump()
            
            passed = result.recommendation != "MANUAL_REVIEW"
            notes = [f"Semantic fraud score: {result.fraud_score:.2f}"]
            for f in result.flags:
                notes.append(f"⚠ Flag ({f.severity}): {f.signal}")
            
            return AgentResult(
                passed=passed,
                confidence=1.0 - (result.fraud_score * 0.3),
                notes=notes
            )
        except Exception as e:
            # Graceful degradation — don't block the pipeline
            context["semantic_fraud_result"] = SemanticFraudResult().model_dump()
            return AgentResult(
                passed=True,
                confidence=0.8,
                notes=[f"Semantic fraud analysis unavailable: {str(e)}. Proceeding with standard checks."]
            )
