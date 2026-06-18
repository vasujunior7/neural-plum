from .base import BaseAgent
from ..models import AgentResult, ClaimSubmission, PolicyConfig, ClaimPlan, ClaimCategory


# Deterministic routing table based on claim category
ROUTING_TABLE = {
    "CONSULTATION": {
        "agents": ["DocVerification", "Extraction", "Decision"],
        "skip": {
            "FraudCheck": "OPD consultation claims are low-risk; skip rule-based fraud for speed",
            "SemanticFraud": "OPD consultation claims below high-value threshold are low-risk"
        },
        "fast_track": True,
        "base_complexity": 0.2
    },
    "DIAGNOSTIC": {
        "agents": ["DocVerification", "Extraction", "FraudCheck", "Decision"],
        "skip": {
            "SemanticFraud": "Standard diagnostic claims use rule-based fraud checks only"
        },
        "fast_track": False,
        "base_complexity": 0.5
    },
    "PHARMACY": {
        "agents": ["DocVerification", "Extraction", "Decision"],
        "skip": {
            "FraudCheck": "Low-risk pharmacy claims processed under prescription rules",
            "SemanticFraud": "Low-risk pharmacy claims processed under prescription rules"
        },
        "fast_track": True,
        "base_complexity": 0.2
    },
    "DENTAL": {
        "agents": ["DocVerification", "Extraction", "Decision"],
        "skip": {
            "FraudCheck": "Dental claims processed under separate sub-limit rules",
            "SemanticFraud": "Dental claims processed under separate sub-limit rules"
        },
        "fast_track": True,
        "base_complexity": 0.3
    },
    "VISION": {
        "agents": ["DocVerification", "Extraction", "Decision"],
        "skip": {
            "FraudCheck": "Vision claims are low-value and processed under sub-limit rules",
            "SemanticFraud": "Vision claims are low-value and processed under sub-limit rules"
        },
        "fast_track": True,
        "base_complexity": 0.2
    },
    "ALTERNATIVE_MEDICINE": {
        "agents": ["DocVerification", "Extraction", "FraudCheck", "Decision"],
        "skip": {
            "SemanticFraud": "Alternative medicine uses practitioner validation instead"
        },
        "fast_track": False,
        "base_complexity": 0.4
    },
}

# Default full pipeline for unknown categories
DEFAULT_ROUTE = {
    "agents": ["DocVerification", "Extraction", "FraudCheck", "SemanticFraud", "Decision"],
    "skip": {},
    "fast_track": False,
    "base_complexity": 0.5
}


class PlannerAgent(BaseAgent):
    """
    Classifies claim type, scores complexity, and decides which agents to run.
    Uses a deterministic routing table — no LLM calls needed.
    """
    
    def run(self, claim: ClaimSubmission, policy: PolicyConfig, context: dict) -> AgentResult:
        category = claim.claim_category.value.upper()
        route = ROUTING_TABLE.get(category, DEFAULT_ROUTE)
        
        agents_to_run = list(route["agents"])
        agents_to_skip = dict(route["skip"])
        fast_track = route["fast_track"]
        complexity = route["base_complexity"]
        
        # Override: high-value claims always get full pipeline
        high_value_threshold = policy.fraud_thresholds.auto_manual_review_above
        if claim.claimed_amount > high_value_threshold:
            agents_to_run = ["DocVerification", "Extraction", "FraudCheck", "SemanticFraud", "Decision"]
            agents_to_skip = {}
            fast_track = False
            complexity = max(complexity, 0.7)
        
        # Override: claims with history always get fraud check
        if claim.claims_history and len(claim.claims_history) > 0:
            if "FraudCheck" not in agents_to_run:
                agents_to_run.insert(-1, "FraudCheck")  # Insert before Decision
                agents_to_skip.pop("FraudCheck", None)
            complexity = max(complexity, 0.5)
        
        # Adjust complexity based on amount relative to sub-limit
        category_rules = policy.opd_categories.get(category.lower())
        if category_rules and category_rules.sub_limit > 0:
            amount_ratio = claim.claimed_amount / category_rules.sub_limit
            if amount_ratio > 0.8:
                complexity = min(complexity + 0.2, 1.0)
        
        plan = ClaimPlan(
            claim_category=category,
            complexity_score=round(complexity, 2),
            agents_to_run=agents_to_run,
            agents_to_skip=agents_to_skip,
            fast_track=fast_track
        )
        
        # Store plan in context for downstream use
        context["claim_plan"] = plan.model_dump()
        
        notes = [
            f"Claim classified as {category} — {'Fast Track' if fast_track else 'Full Pipeline'}",
            f"Complexity score: {complexity:.2f}",
            f"Agents to run: {', '.join(agents_to_run)}",
        ]
        if agents_to_skip:
            for agent, reason in agents_to_skip.items():
                notes.append(f"Skipping {agent}: {reason}")
        
        return AgentResult(
            passed=True,
            confidence=1.0,
            notes=notes
        )
